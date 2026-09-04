import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 2P Animated SD Basketball",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 2P Animated SD Basketball (Kobe vs Jordan)")

st.markdown("""
### 🎮 2P 대전 조작법
| 플레이어 | 이동 | 점프 | 슛 / 덩크 |
| :--- | :--- | :--- | :--- |
| **1P (Kobe #24)** | `A` (좌), `D` (우) | `W` | **`F` 키** |
| **2P (Jordan #23)** | `←` (좌), `→` (우) | `↑` | **`L` 키** |

* **🎯 Green Light Shot**: 게이지를 초록색 영역(70%~88%)에 맞추면 **100% 무조건 성공!**
* **🔥 시네마틱 덩크**: 골대 근처에서 전진 중 슛 키(`F` / `L`)를 누르면 **카메라 줌인 + 슬로우 모션 덩크!**
""")

game_2p_animated_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: 'Impact', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #181822; border: 4px solid #fff; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        
        #hud {
            position: absolute; top: 15px; left: 30px; color: #fff; font-size: 22px;
            background: rgba(0,0,0,0.75); padding: 8px 18px; border-radius: 6px; border-left: 5px solid #f1c40f;
            display: flex; gap: 20px;
        }
        #green-splash {
            position: absolute; top: 25%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; color: #2ecc71; text-shadow: 0 0 20px #2ecc71, 2px 2px #000;
            opacity: 0; transition: opacity 0.2s; pointer-events: none; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">
            <div>1P (KOBE): <span id="score1" style="color:#f1c40f;">0</span></div>
            <div>|</div>
            <div>2P (JORDAN): <span id="score2" style="color:#e74c3c;">0</span></div>
        </div>
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
const score1El = document.getElementById('score1');
score2El = document.getElementById('score2');

let score1 = 0;
let score2 = 0;

// 카메라 시스템
const camera = { x: 0, y: 0, scale: 1.0, targetScale: 1.0, targetX: 0, targetY: 0 };

// 골대
const hoop = { x: 750, y: 190, rimX: 715, rimY: 220, rimR: 16 };

// 플레이어 객체 생성 함수
function createPlayer(id, x, color1, color2, number, hairType) {
    return {
        id: id,
        x: x,
        y: 375,
        w: 36,
        h: 40,
        vx: 0,
        vy: 0,
        color1: color1,
        color2: color2,
        number: number,
        hairType: hairType,
        isJumping: false,
        isDunking: false,
        dunkProgress: 0,
        dunkScored: false,
        isCharging: false,
        power: 0,
        animFrame: 0, // 팔다리 애니메이션용
        isMoving: false
    };
}

const p1 = createPlayer(1, 150, '#fdb927', '#552583', '24', 'afro'); // 코비 (Lakers)
const p2 = createPlayer(2, 280, '#ce1141', '#111111', '23', 'bald'); // 조던 (Bulls)

let balls = [];

// 키 상태 제어
const keys = {};

window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    keys[k] = true;
    if (e.key === 'ArrowLeft') keys['arrowleft'] = true;
    if (e.key === 'ArrowRight') keys['arrowright'] = true;
    if (e.key === 'ArrowUp') keys['arrowup'] = true;

    // 1P 슛/덩크 시작
    if (k === 'f') handleShootOrDunkPress(p1);
    // 2P 슛/덩크 시작
    if (k === 'l') handleShootOrDunkPress(p2);
});

window.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    keys[k] = false;
    if (e.key === 'ArrowLeft') keys['arrowleft'] = false;
    if (e.key === 'ArrowRight') keys['arrowright'] = false;
    if (e.key === 'ArrowUp') keys['arrowup'] = false;

    // 1P 슛 방출
    if (k === 'f') releaseShoot(p1);
    // 2P 슛 방출
    if (k === 'l') releaseShoot(p2);
});

function handleShootOrDunkPress(p) {
    if (p.x > 450 && p.isMoving && !p.isDunking) {
        startDunk(p);
    } else if (!p.isCharging && !p.isDunking) {
        p.isCharging = true;
        p.power = 0;
    }
}

function startDunk(p) {
    p.isDunking = true;
    p.dunkProgress = 0;
    p.dunkScored = false;
    p.isJumping = true;
    p.isCharging = false;
}

function releaseShoot(p) {
    if (p.isCharging && !p.isDunking) {
        shootBall(p);
        p.isCharging = false;
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

    if (p.power >= 70 && p.power <= 88) {
        isGreen = true;
        const startX = p.x + 20;
        const startY = p.y;
        const targetX = hoop.rimX;
        const targetY = hoop.rimY;

        const gravity = 0.42;
        const time = 38;
        vx = (targetX - startX) / time;
        vy = (targetY - startY - 0.5 * gravity * time * time) / time;
    } else {
        vx = 7 + (p.power / 100) * 8;
        vy = -8 - (p.power / 100) * 5;
    }

    balls.push({
        x: p.x + 20,
        y: p.y,
        vx: vx,
        vy: vy,
        r: 10,
        isGreen: isGreen,
        isScored: false,
        ownerId: p.id
    });
}

function updatePlayer(p, leftKey, rightKey, jumpKey) {
    p.isMoving = false;

    if (p.isDunking) {
        p.dunkProgress += 0.012; // 슬로우 모션
        p.x = 480 + p.dunkProgress * (hoop.rimX - 510);
        p.y = 375 - Math.sin(p.dunkProgress * Math.PI) * 175;

        camera.targetScale = 1.6;
        camera.targetX = (p.x + hoop.rimX) / 2 - 450 / camera.targetScale;
        camera.targetY = (p.y + hoop.rimY) / 2 - 250 / camera.targetScale;

        if (p.dunkProgress >= 0.88 && !p.dunkScored) {
            if (p.id === 1) score1 += 2; else score2 += 2;
            score1El.innerText = score1;
            score2El.innerText = score2;
            p.dunkScored = true;

            triggerGreenSplash(`${p.id === 1 ? 'KOBE' : 'JORDAN'} SLOW-MO DUNK! 🔥`);
            playGreenGiantSound();

            balls.push({ x: hoop.rimX, y: hoop.rimY + 12, vx: 1, vy: 5, r: 10, isGreen: true, isScored: true });
        }

        if (p.dunkProgress >= 1.0) {
            p.isDunking = false;
            p.y = 375;
            p.isJumping = false;
        }
    } else {
        if (keys[leftKey]) { p.x -= 4; p.isMoving = true; }
        if (keys[rightKey]) { p.x += 4; p.isMoving = true; }
        if (keys[jumpKey] && !p.isJumping) {
            p.vy = -11;
            p.isJumping = true;
        }

        p.y += p.vy;
        p.vy += 0.55;

        if (p.y >= 375) {
            p.y = 375;
            p.isJumping = false;
        }

        if (p.x < 20) p.x = 20;
        if (p.x > 620) p.x = 620;
    }

    if (p.isMoving || p.isJumping) {
        p.animFrame += 0.2; // 팔다리 애니메이션 속도
    }

    if (p.isCharging) {
        p.power = Math.min(100, p.power + 2.3);
    }
}

function update() {
    // 1P & 2P 업데이트
    updatePlayer(p1, 'a', 'd', 'w');
    updatePlayer(p2, 'arrowleft', 'arrowright', 'arrowup');

    // 덩크 중이 아니면 카메라 원복
    if (!p1.isDunking && !p2.isDunking) {
        camera.targetScale = 1.0;
        camera.targetX = 0;
        camera.targetY = 0;
    }

    camera.scale += (camera.targetScale - camera.scale) * 0.1;
    camera.x += (camera.targetX - camera.x) * 0.1;
    camera.y += (camera.targetY - camera.y) * 0.1;

    // 농구공 물리
    for (let i = balls.length - 1; i >= 0; i--) {
        const b = balls[i];
        b.x += b.vx;
        b.y += b.vy;
        b.vy += 0.42;

        if (b.y >= 410) { b.y = 410; b.vy *= -0.5; }

        if (!b.isGreen && b.x >= hoop.x - 10 && b.x <= hoop.x + 10 && b.y >= hoop.y && b.y <= hoop.y + 90) {
            b.vx *= -0.6;
            b.x = hoop.x - 12;
        }

        const distToRim = Math.hypot(b.x - hoop.rimX, b.y - hoop.rimY);
        if (distToRim < hoop.rimR && b.vy > 0 && !b.isScored) {
            if (b.ownerId === 1) score1 += 2;
            else if (b.ownerId === 2) score2 += 2;

            score1El.innerText = score1;
            score2El.innerText = score2;
            b.isScored = true;

            triggerGreenSplash(b.isGreen ? "PERFECT GREEN RELEASE! 🔥" : "HO HO HO! GREEN GIANT! 🔥");
            playGreenGiantSound();
        }

        if (b.x > 920 || b.y > 520) balls.splice(i, 1);
    }
}

// 팔다리 애니메이션이 적용된 SD 캐릭터 그리기
function drawPlayer(p) {
    const legAngle = Math.sin(p.animFrame) * 12; // 다리 흔들림
    const armAngle = Math.cos(p.animFrame) * 15; // 팔 흔들림

    // 1. 짧은 다리 애니메이션 (Short Legs)
    ctx.fillStyle = '#3d2314';
    // 왼다리
    ctx.save();
    ctx.translate(p.x + 9, p.y + 34);
    ctx.rotate((p.isMoving ? legAngle : 0) * Math.PI / 180);
    ctx.fillRect(-3, 0, 6, 11);
    ctx.fillStyle = '#fff'; // 신발
    ctx.fillRect(-4, 9, 8, 4);
    ctx.restore();

    // 오른다리
    ctx.fillStyle = '#3d2314';
    ctx.save();
    ctx.translate(p.x + 27, p.y + 34);
    ctx.rotate((p.isMoving ? -legAngle : 0) * Math.PI / 180);
    ctx.fillRect(-3, 0, 6, 11);
    ctx.fillStyle = '#fff'; // 신발
    ctx.fillRect(-4, 9, 8, 4);
    ctx.restore();

    // 2. 몸통 (유니폼)
    ctx.fillStyle = p.color1;
    ctx.fillRect(p.x, p.y, p.w, 24);
    ctx.fillStyle = p.color2;
    ctx.fillRect(p.x, p.y + 24, p.w, 10);

    // 등번호
    ctx.fillStyle = p.color2;
    ctx.font = 'bold 12px Impact';
    ctx.fillText(p.number, p.x + 11, p.y + 17);

    // 3. 짧은 팔 애니메이션 (Short Arms)
    ctx.fillStyle = '#3d2314';
    if (p.isDunking) {
        ctx.fillRect(p.x + 28, p.y - 12, 6, 16); // 덩크 높게 든 팔
    } else {
        // 왼팔
        ctx.save();
        ctx.translate(p.x - 2, p.y + 8);
        ctx.rotate((p.isMoving ? -armAngle : 0) * Math.PI / 180);
        ctx.fillRect(-3, 0, 6, 12);
        ctx.restore();

        // 오른팔
        ctx.save();
        ctx.translate(p.x + 38, p.y + 8);
        ctx.rotate((p.isMoving ? armAngle : 0) * Math.PI / 180);
        ctx.fillRect(-3, 0, 6, 12);
        ctx.restore();
    }

    // 4. 대두 머리
    ctx.fillStyle = '#3d2314';
    ctx.beginPath();
    ctx.arc(p.x + 18, p.y - 14, 18, 0, Math.PI * 2);
    ctx.fill();

    // 헤어스타일 (코비 아프로 / 조던 민머리)
    if (p.hairType === 'afro') {
        ctx.fillStyle = '#0a0a0a';
        ctx.beginPath();
        ctx.arc(p.x + 18, p.y - 20, 19, Math.PI, 2 * Math.PI);
        ctx.fill();
    }

    // 공 들기
    if (p.isDunking && p.dunkProgress < 0.88) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(p.x + 31, p.y - 20, 10, 0, Math.PI * 2);
        ctx.fill();
    } else if (!p.isCharging && !p.isDunking) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(p.x + 32, p.y + 16, 10, 0, Math.PI * 2);
        ctx.fill();
    }

    // 5. 슛 게이지 HUD
    if (p.isCharging) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(p.x - 8, p.y - 58, 52, 11);
        
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(p.x + 28, p.y - 58, 9, 11);

        const isGreenZone = p.power >= 70 && p.power <= 88;
        ctx.fillStyle = isGreenZone ? '#2ecc71' : '#f39c12';
        ctx.fillRect(p.x - 8, p.y - 58, (p.power / 100) * 52, 11);
        
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.strokeRect(p.x - 8, p.y - 58, 52, 11);
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.scale(camera.scale, camera.scale);
    ctx.translate(-camera.x, -camera.y);

    // 1. 코트 바닥
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

    // 3. 1P 및 2P 캐릭터 그리기
    drawPlayer(p1);
    drawPlayer(p2);

    // 4. 농구공
    for (let b of balls) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    ctx.restore();
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

components.html(game_2p_animated_html, height=580)
