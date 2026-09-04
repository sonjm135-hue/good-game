import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 Kobe 2D Dunk & Green Basketball",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Kobe 2D Dunk & Green Basketball Edition")

st.markdown("""
### 🎮 게임 조작법
* **이동 (Move)**: `A` (왼쪽), `D` (오른쪽)
* **점프 (Jump)**: `W` 또는 `Space`
* **점프 슛 / 세트 슛**: **`F` 키 또는 마우스 클릭**
  * 초록색 영역(70%~88%)에서 떼면 **어디서 쏘든 100% 무조건 득점!**
* **🔥 덩크 (Dunk)**: **골대 근처(페인트 존)로 전진하면서 `F` 키를 빠르게 누르면 덩크 발동!**
* **🔊 득점 사운드**: 득점 시 **"Ho Ho Ho Green Giant!"** 음성이 출력됩니다!
""")

game_kobe_2d_html = """<!DOCTYPE html>
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
            position: absolute; top: 28%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; color: #2ecc71; text-shadow: 0 0 20px #2ecc71, 2px 2px #000;
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
// Green Giant Sound System
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

// 플레이어 (Kobe Bryant 2D 설정)
const player = {
    x: 180,
    y: 360,
    w: 32,
    h: 60,
    vx: 0,
    vy: 0,
    isJumping: false,
    isDunking: false,
    dunkProgress: 0
};

// 골대 및 림 설정
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
    // 덩크 조건: 골대 근처(x > 500)에서 이동 중
    if (player.x > 500 && (keys.d || keys.a || player.isJumping) && !player.isDunking) {
        startDunk();
    } else if (!isCharging && !player.isDunking) {
        isCharging = true;
        power = 0;
    }
}

function startDunk() {
    player.isDunking = true;
    player.dunkProgress = 0;
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

    // 초록색 게이지 (70% ~ 88%): 무조건 100% 득점 궤적 자동 계산
    if (p >= 70 && p <= 88) {
        isGreen = true;
        const startX = player.x + 20;
        const startY = player.y;
        const targetX = hoop.rimX;
        const targetY = hoop.rimY;

        // 물리 곡선 역산
        const gravity = 0.42;
        const time = 38; // 프레임
        vx = (targetX - startX) / time;
        vy = (targetY - startY - 0.5 * gravity * time * time) / time;
    } else {
        // 일반/미스 슛
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
    // 1. 덩크 애니메이션 처리
    if (player.isDunking) {
        player.dunkProgress += 0.04;
        
        // 공중 부양 후 림으로 이동
        player.x = 520 + player.dunkProgress * (hoop.rimX - 540);
        player.y = 360 - Math.sin(player.dunkProgress * Math.PI) * 160;

        // 덩크 완성 시점 (림 착지 직전)
        if (player.dunkProgress >= 0.85 && !player.dunkScored) {
            score += 2;
            fgm += 1;
            scoreEl.innerText = score;
            fgmEl.innerText = fgm;
            player.dunkScored = true;

            triggerGreenSplash("KOBE DUNK! GREEN GIANT! 🔥");
            playGreenGiantSound();

            // 튕겨나가는 공 연출
            balls.push({
                x: hoop.rimX,
                y: hoop.rimY + 10,
                vx: 1,
                vy: 6,
                r: 10,
                isGreen: true,
                isScored: true
            });
        }

        if (player.dunkProgress >= 1.0) {
            player.isDunking = false;
            player.dunkScored = false;
            player.y = 360;
            player.isJumping = false;
        }
    } else {
        // 일반 이동 물리
        if (keys.a) player.x -= 4;
        if (keys.d) player.x += 4;
        if ((keys.w || keys.space) && !player.isJumping) {
            player.vy = -11;
            player.isJumping = true;
        }

        player.y += player.vy;
        player.vy += 0.55; // 중력

        if (player.y >= 360) {
            player.y = 360;
            player.isJumping = false;
        }

        if (player.x < 30) player.x = 30;
        if (player.x > 620) player.x = 620;
    }

    // 2. 슛 게이지 충전
    if (isCharging) {
        power = Math.min(100, power + 2.3);
    }

    // 3. 농구공 물리 및 100% Green Light 판정
    for (let i = balls.length - 1; i >= 0; i--) {
        const b = balls[i];
        b.x += b.vx;
        b.y += b.vy;
        b.vy += 0.42;

        // 바닥 튕김
        if (b.y >= 410) {
            b.y = 410;
            b.vy *= -0.5;
        }

        // 일반 슛 백보드 반발 (Green Light가 아닐 때만)
        if (!b.isGreen && b.x >= hoop.x - 10 && b.x <= hoop.x + 10 && b.y >= hoop.y && b.y <= hoop.y + 90) {
            b.vx *= -0.6;
            b.x = hoop.x - 12;
        }

        // 득점 판정
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

    // 1. 코트 바닥 & 3점선
    ctx.fillStyle = '#c85a17';
    ctx.fillRect(0, 420, 900, 80);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 418, 900, 4);

    ctx.fillStyle = '#552583'; // Lakers Purple Paint
    ctx.fillRect(600, 420, 300, 80);
    ctx.strokeStyle = '#fdb927'; // Lakers Gold Line
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(750, 420, 220, Math.PI, 1.5 * Math.PI);
    ctx.stroke();

    // 2. 백보드 및 골대
    ctx.fillStyle = '#222';
    ctx.fillRect(770, 190, 12, 230);
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.fillRect(750, 140, 10, 100);
    ctx.strokeStyle = '#ce1141';
    ctx.strokeRect(750, 170, 8, 40);
    
    // 림 (골대)
    ctx.strokeStyle = '#e67e22';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(715, 220);
    ctx.lineTo(750, 220);
    ctx.stroke();

    // 3. 코비 브라이언트 캐릭터 그리기
    // 유니폼 (Lakers #24 Yellow & Purple)
    ctx.fillStyle = '#fdb927';
    ctx.fillRect(player.x, player.y, player.w, player.h);
    ctx.fillStyle = '#552583';
    ctx.fillRect(player.x, player.y + 35, player.w, 25);

    // 피부 톤
    ctx.fillStyle = '#3d2314';
    ctx.beginPath();
    ctx.arc(player.x + 16, player.y - 10, 13, 0, Math.PI * 2);
    ctx.fill();

    // 💇‍♂️ 코비 브라이언트 헤어 (짧은 아프로 도트 스타일)
    ctx.fillStyle = '#0a0a0a';
    ctx.beginPath();
    ctx.arc(player.x + 16, player.y - 14, 14, Math.PI, 2 * Math.PI);
    ctx.fill();
    // 머리 질감 도트 표현
    ctx.fillStyle = '#222';
    ctx.fillRect(player.x + 6, player.y - 24, 6, 4);
    ctx.fillRect(player.x + 15, player.y - 26, 6, 4);
    ctx.fillRect(player.x + 22, player.y - 23, 5, 4);

    // 등번호 24
    ctx.fillStyle = '#552583';
    ctx.font = 'bold 12px Impact';
    ctx.fillText('24', player.x + 10, player.y + 22);

    // 덩크 시 공 손에 고정
    if (player.isDunking && player.dunkProgress < 0.85) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(player.x + 30, player.y - 10, 10, 0, Math.PI * 2);
        ctx.fill();
    } else if (!isCharging && !player.isDunking) {
        // 일반 평소 공
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(player.x + 26, player.y + 12, 10, 0, Math.PI * 2);
        ctx.fill();
    }

    // 4. 초록색 슛 게이지 HUD
    if (isCharging) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(player.x - 10, player.y - 50, 52, 11);
        
        // 초록색 무조건 득점 존 (70% ~ 88%)
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(player.x + 26, player.y - 50, 9, 11);

        // 게이지 채우기
        const isGreenZone = power >= 70 && power <= 88;
        ctx.fillStyle = isGreenZone ? '#2ecc71' : '#f39c12';
        ctx.fillRect(player.x - 10, player.y - 50, (power / 100) * 52, 11);
        
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.strokeRect(player.x - 10, player.y - 50, 52, 11);
    }

    // 5. 날아가는 농구공들
    for (let b of balls) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
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

components.html(game_kobe_2d_html, height=580)
