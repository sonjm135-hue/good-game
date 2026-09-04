import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 Kobe SD Dunk & Slow-Mo Basketball",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Kobe SD Cinematic Dunk & Green Release")

st.markdown("""
### 🎮 변경 및 추가된 조작법
* **귀여운 SD 신체 비율**: 몸통과 머리에 비해 **짧은 팔과 다리**로 캐릭터 비율이 수정되었습니다.
* **🔥 시네마틱 덩크 (Dunk)**: 골대 근처(페인트 존)로 이동하며 **`F` 키**를 누르면:
  * **카메라가 코비에게 순간 줌인(Zoom-In)** 됩니다.
  * **시간이 슬로우 모션(Slow-Motion)**으로 흐르며 역동적이고 멋진 덩크 슛 연출이 펼쳐집니다!
* **🎯 초록색 게이지 (Green Release)**: 어디서 쏘든 **100% 무조건 성공!**
""")

game_sd_dunk_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: 'Impact', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #181822; border: 4px solid #fff; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        
        #hud {
            position: absolute; top: 15px; left: 30px; color: #fff; font-size: 24px;
            background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 5px; border-left: 5px solid #f1c40f;
        }
        #green-splash {
            position: absolute; top: 25%; left: 50%; transform: translate(-50%, -50%);
            font-size: 45px; color: #2ecc71; text-shadow: 0 0 20px #2ecc71, 2px 2px #000;
            opacity: 0; transition: opacity 0.2s; pointer-events: none; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">KOBE #24 | PTS: <span id="score" style="color:#2ecc71;">0</span> | FGM: <span id="fgm">0</span></div>
        <div id="green-splash">HO HO HO! GREEN GIANT! 🔥</div>
        <canvas id="gameCanvas" width="900" height="500"></canvas>
    </div>

<script>
// Sound System
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playGreenGiantSound() {
    const audio = new Audio('https://www.soundboard.com/handler/gettrack.ashx?id=516543');
    audio.play().catch(() => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.frequency.setValueAtTime(440, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.4);
    });
}

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const greenSplash = document.getElementById('green-splash');
const scoreEl = document.getElementById('score');
const fgmEl = document.getElementById('fgm');

let score = 0;
let fgm = 0;

// 카메라 시스템 (슬로우 모션 & 줌 연출용)
const camera = {
    x: 0,
    y: 0,
    scale: 1.0,
    targetScale: 1.0,
    targetX: 0,
    targetY: 0
};

// SD 귀여운 코비 (짧은 팔다리)
const player = {
    x: 180,
    y: 375,
    w: 36,
    h: 40, // 짧은 몸통
    vx: 0,
    vy: 0,
    isJumping: false,
    isDunking: false,
    dunkProgress: 0,
    dunkScored: false
};

const hoop = {
    x: 750,
    y: 190,
    rimX: 715,
    rimY: 220,
    rimR: 16
};

let balls = [];
let isCharging = false;
let power = 0;

const keys = { a: false, d: false, w: false, space: false };

window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (k === 'a') keys.a = true;
    if (k === 'd') keys.d = true;
    if (k === 'w') keys.w = true;
    if (e.code === 'Space') keys.space = true;
    if (k === 'f') handleShootOrDunkPress();
});

window.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    if (k === 'a') keys.a = false;
    if (k === 'd') keys.d = false;
    if (k === 'w') keys.w = false;
    if (e.code === 'Space') keys.space = false;
    if (k === 'f') releaseShoot();
});

canvas.addEventListener('mousedown', handleShootOrDunkPress);
canvas.addEventListener('mouseup', releaseShoot);

function handleShootOrDunkPress() {
    if (player.x > 460 && (keys.d || keys.a || player.isJumping) && !player.isDunking) {
        startDunk();
    } else if (!isCharging && !player.isDunking) {
        isCharging = true;
        power = 0;
    }
}

function startDunk() {
    player.isDunking = true;
    player.dunkProgress = 0;
    player.dunkScored = false;
    player.isJumping = true;
    isCharging = false;
}

function releaseShoot() {
    if (isCharging && !player.isDunking) {
        shootBall(power);
        isCharging = false;
    }
}

function triggerGreenSplash(text = "HO HO HO! GREEN GIANT! 🔥") {
    greenSplash.innerText = text;
    greenSplash.style.opacity = '1';
    setTimeout(() => { greenSplash.style.opacity = '0'; }, 1300);
}

function shootBall(p) {
    let isGreen = false;
    let vx, vy;

    if (p >= 70 && p <= 88) {
        isGreen = true;
        const startX = player.x + 20;
        const startY = player.y;
        const targetX = hoop.rimX;
        const targetY = hoop.rimY;

        const gravity = 0.42;
        const time = 38;
        vx = (targetX - startX) / time;
        vy = (targetY - startY - 0.5 * gravity * time * time) / time;
    } else {
        vx = 7 + (p / 100) * 8;
        vy = -8 - (p / 100) * 5;
    }

    balls.push({
        x: player.x + 20,
        y: player.y,
        vx: vx,
        vy: vy,
        r: 10,
        isGreen: isGreen,
        isScored: false
    });
}

function update() {
    // 1. 덩크 및 슬로우 모션 / 줌 효과 연출
    if (player.isDunking) {
        // 슬로우 모션: dunkProgress 증가 속도를 느리게 설정 (0.012)
        player.dunkProgress += 0.012;
        
        player.x = 480 + player.dunkProgress * (hoop.rimX - 510);
        player.y = 375 - Math.sin(player.dunkProgress * Math.PI) * 175;

        // 카메라 줌인 타겟 설정 (선수와 골대 중심으로 1.6배 확대)
        camera.targetScale = 1.6;
        camera.targetX = (player.x + hoop.rimX) / 2 - 450 / camera.targetScale;
        camera.targetY = (player.y + hoop.rimY) / 2 - 250 / camera.targetScale;

        // 덩크 림 타격 시점
        if (player.dunkProgress >= 0.88 && !player.dunkScored) {
            score += 2;
            fgm += 1;
            scoreEl.innerText = score;
            fgmEl.innerText = fgm;
            player.dunkScored = true;

            triggerGreenSplash("KOBE SLOW-MO DUNK! 🔥");
            playGreenGiantSound();

            balls.push({
                x: hoop.rimX,
                y: hoop.rimY + 12,
                vx: 1,
                vy: 5,
                r: 10,
                isGreen: true,
                isScored: true
            });
        }

        if (player.dunkProgress >= 1.0) {
            player.isDunking = false;
            player.y = 375;
            player.isJumping = false;
        }
    } else {
        // 카메라 원상 복구 (줌 아웃)
        camera.targetScale = 1.0;
        camera.targetX = 0;
        camera.targetY = 0;

        // 이동 물리
        if (keys.a) player.x -= 4;
        if (keys.d) player.x += 4;
        if ((keys.w || keys.space) && !player.isJumping) {
            player.vy = -11;
            player.isJumping = true;
        }

        player.y += player.vy;
        player.vy += 0.55;

        if (player.y >= 375) {
            player.y = 375;
            player.isJumping = false;
        }

        if (player.x < 30) player.x = 30;
        if (player.x > 620) player.x = 620;
    }

    // 카메라 부드러운 보간 (Lerp)
    camera.scale += (camera.targetScale - camera.scale) * 0.1;
    camera.x += (camera.targetX - camera.x) * 0.1;
    camera.y += (camera.targetY - camera.y) * 0.1;

    // 2. 슛 게이지 충전
    if (isCharging) {
        power = Math.min(100, power + 2.3);
    }

    // 3. 농구공 물리
    for (let i = balls.length - 1; i >= 0; i--) {
        const b = balls[i];
        b.x += b.vx;
        b.y += b.vy;
        b.vy += 0.42;

        if (b.y >= 410) {
            b.y = 410;
            b.vy *= -0.5;
        }

        if (!b.isGreen && b.x >= hoop.x - 10 && b.x <= hoop.x + 10 && b.y >= hoop.y && b.y <= hoop.y + 90) {
            b.vx *= -0.6;
            b.x = hoop.x - 12;
        }

        const distToRim = Math.hypot(b.x - hoop.rimX, b.y - hoop.rimY);
        if (distToRim < hoop.rimR && b.vy > 0 && !b.isScored) {
            score += 2;
            fgm += 1;
            scoreEl.innerText = score;
            fgmEl.innerText = fgm;
            b.isScored = true;

            triggerGreenSplash(b.isGreen ? "PERFECT GREEN RELEASE! 🔥" : "HO HO HO! GREEN GIANT! 🔥");
            playGreenGiantSound();
        }

        if (b.x > 920 || b.y > 520) {
            balls.splice(i, 1);
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 카메라 줌인/슬로우 모션 트랜스폼 적용
    ctx.save();
    ctx.scale(camera.scale, camera.scale);
    ctx.translate(-camera.x, -camera.y);

    // 1. 코트 바닥 & 페인트존
    ctx.fillStyle = '#c85a17';
    ctx.fillRect(0, 415, 900, 85);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 413, 900, 4);

    ctx.fillStyle = '#552583';
    ctx.fillRect(600, 415, 300, 85);
    ctx.strokeStyle = '#fdb927';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(750, 415, 220, Math.PI, 1.5 * Math.PI);
    ctx.stroke();

    // 2. 백보드 및 골대
    ctx.fillStyle = '#222';
    ctx.fillRect(770, 190, 12, 225);
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.fillRect(750, 140, 10, 100);
    ctx.strokeStyle = '#ce1141';
    ctx.strokeRect(750, 170, 8, 40);
    
    ctx.strokeStyle = '#e67e22';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(715, 220);
    ctx.lineTo(750, 220);
    ctx.stroke();

    // 3. SD 코비 브라이언트 (대두 + 짧은 팔다리)
    // 짧은 다리 (Short Legs)
    ctx.fillStyle = '#3d2314';
    ctx.fillRect(player.x + 6, player.y + 32, 7, 10);
    ctx.fillRect(player.x + 23, player.y + 32, 7, 10);
    // 신발
    ctx.fillStyle = '#fff';
    ctx.fillRect(player.x + 4, player.y + 40, 10, 5);
    ctx.fillRect(player.x + 23, player.y + 40, 10, 5);

    // 몸통 (유니폼)
    ctx.fillStyle = '#fdb927';
    ctx.fillRect(player.x, player.y, player.w, 24);
    ctx.fillStyle = '#552583';
    ctx.fillRect(player.x, player.y + 24, player.w, 10);

    // 등번호 24
    ctx.fillStyle = '#552583';
    ctx.font = 'bold 12px Impact';
    ctx.fillText('24', player.x + 12, player.y + 17);

    // 짧은 팔 (Short Arms)
    ctx.fillStyle = '#3d2314';
    if (player.isDunking) {
        ctx.fillRect(player.x + 28, player.y - 12, 6, 16); // 덩크 시 위로 올린 팔
    } else {
        ctx.fillRect(player.x - 5, player.y + 8, 7, 12);
        ctx.fillRect(player.x + 34, player.y + 8, 7, 12);
    }

    // 대두 머리 (Big Head)
    ctx.fillStyle = '#3d2314';
    ctx.beginPath();
    ctx.arc(player.x + 18, player.y - 14, 18, 0, Math.PI * 2);
    ctx.fill();

    // 짧은 아프로 헤어
    ctx.fillStyle = '#0a0a0a';
    ctx.beginPath();
    ctx.arc(player.x + 18, player.y - 20, 19, Math.PI, 2 * Math.PI);
    ctx.fill();

    // 덩크 및 기본 공 포지션
    if (player.isDunking && player.dunkProgress < 0.88) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(player.x + 31, player.y - 20, 10, 0, Math.PI * 2);
        ctx.fill();
    } else if (!isCharging && !player.isDunking) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(player.x + 32, player.y + 16, 10, 0, Math.PI * 2);
        ctx.fill();
    }

    // 4. 초록색 슛 게이지 HUD
    if (isCharging) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(player.x - 8, player.y - 58, 52, 11);
        
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(player.x + 28, player.y - 58, 9, 11);

        const isGreenZone = power >= 70 && power <= 88;
        ctx.fillStyle = isGreenZone ? '#2ecc71' : '#f39c12';
        ctx.fillRect(player.x - 8, player.y - 58, (power / 100) * 52, 11);
        
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.strokeRect(player.x - 8, player.y - 58, 52, 11);
    }

    // 5. 농구공
    for (let b of balls) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    ctx.restore(); // 카메라 변환 복구
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>"""

components.html(game_sd_dunk_html, height=580)
