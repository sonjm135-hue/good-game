import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 2D Classic Basketball Game",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 2D 클래식 아케이드 농구 게임")

st.markdown("""
### 🎮 2D 게임 조작법
* **이동 (Move)**: `A` (왼쪽), `D` (오른쪽)
* **점프 (Jump)**: `W` 또는 `Space`
* **슛 (Shoot)**: **`F` 키 또는 마우스 클릭**
  * 누르고 있으면 슛 파워 게이지가 상승하며, 초록색 구간에서 떼면 클린 슛과 함께 **Green Giant 사운드**가 출력됩니다!
""")

game_2d_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: 'Impact', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #1a1a24; border: 4px solid #fff; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        
        #hud {
            position: absolute; top: 15px; left: 30px; color: #fff; font-size: 24px;
            background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 5px; border-left: 5px solid #2ecc71;
        }
        #green-splash {
            position: absolute; top: 30%; left: 50%; transform: translate(-50%, -50%);
            font-size: 40px; color: #2ecc71; text-shadow: 0 0 15px #2ecc71, 2px 2px #000;
            opacity: 0; transition: opacity 0.2s; pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">SCORE: <span id="score" style="color:#2ecc71;">0</span> | FGM: <span id="fgm">0</span></div>
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

// Game Entities
const player = {
    x: 180,
    y: 360,
    w: 30,
    h: 60,
    vx: 0,
    vy: 0,
    isJumping: false
};

const hoop = {
    x: 750,
    y: 200,
    rimX: 720,
    rimY: 230,
    rimR: 15
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
    if (k === 'f') startCharging();
});

window.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    if (k === 'a') keys.a = false;
    if (k === 'd') keys.d = false;
    if (k === 'w') keys.w = false;
    if (e.code === 'Space') keys.space = false;
    if (k === 'f') releaseShoot();
});

canvas.addEventListener('mousedown', startCharging);
canvas.addEventListener('mouseup', releaseShoot);

function startCharging() {
    if (!isCharging) {
        isCharging = true;
        power = 0;
    }
}

function releaseShoot() {
    if (isCharging) {
        shootBall(power);
        isCharging = false;
    }
}

function triggerGreenSplash() {
    greenSplash.style.opacity = '1';
    setTimeout(() => { greenSplash.style.opacity = '0'; }, 1300);
}

function shootBall(p) {
    let isPerfect = false;
    let vx = 8 + (p / 100) * 8;
    let vy = -9 - (p / 100) * 5;

    // Green Release 타이밍 (70% ~ 88%)
    if (p >= 70 && p <= 88) {
        isPerfect = true;
        vx = 10.2;
        vy = -12.5;
    }

    balls.push({
        x: player.x + 20,
        y: player.y,
        vx: vx,
        vy: vy,
        r: 10,
        isPerfect: isPerfect,
        isScored: false
    });
}

function update() {
    // 이동 물리
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

    // 경계 제한
    if (player.x < 30) player.x = 30;
    if (player.x > 600) player.x = 600;

    // 슛 게이지 충전
    if (isCharging) {
        power = Math.min(100, power + 2.2);
    }

    // 공 물리 업데이트
    for (let i = balls.length - 1; i >= 0; i--) {
        const b = balls[i];
        b.x += b.vx;
        b.y += b.vy;
        b.vy += 0.42; // 중력

        // 바닥 튕김
        if (b.y >= 410) {
            b.y = 410;
            b.vy *= -0.5;
        }

        // 백보드 충돌
        if (b.x >= hoop.x - 10 && b.x <= hoop.x + 10 && b.y >= hoop.y && b.y <= hoop.y + 90) {
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

            triggerGreenSplash();
            playGreenGiantSound();
        }

        // 제거
        if (b.x > 920 || b.y > 520) {
            balls.splice(i, 1);
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. 코트 바닥
    ctx.fillStyle = '#c85a17';
    ctx.fillRect(0, 420, 900, 80);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 418, 900, 4);

    // 2D 3점선 및 페인트존
    ctx.fillStyle = '#ce1141';
    ctx.fillRect(620, 420, 280, 80);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(750, 420, 220, Math.PI, 1.5 * Math.PI);
    ctx.stroke();

    // 2. 백보드 및 골대
    // 기둥
    ctx.fillStyle = '#333';
    ctx.fillRect(770, 200, 12, 220);
    // 백보드
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.fillRect(750, 150, 10, 100);
    ctx.strokeStyle = '#ce1141';
    ctx.strokeRect(750, 180, 8, 40);
    // 림
    ctx.strokeStyle = '#e67e22';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(720, 230);
    ctx.lineTo(750, 230);
    ctx.stroke();

    // 3. 2D 캐릭터 플레이어
    ctx.fillStyle = '#3498db';
    ctx.fillRect(player.x, player.y, player.w, player.h); // 몸통
    ctx.fillStyle = '#f1c40f';
    ctx.beginPath();
    ctx.arc(player.x + 15, player.y - 12, 12, 0, Math.PI * 2); // 머리
    ctx.fill();

    // 플레이어가 잡고 있는 공
    if (!isCharging) {
        ctx.fillStyle = '#e67e22';
        ctx.beginPath();
        ctx.arc(player.x + 25, player.y + 10, 10, 0, Math.PI * 2);
        ctx.fill();
    }

    // 4. 2D 슛 게이지 HUD
    if (isCharging) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(player.x - 10, player.y - 45, 50, 10);
        
        // 초록색 Perfect Zone
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(player.x + 25, player.y - 45, 9, 10);

        // 현재 파워 채우기
        ctx.fillStyle = (power >= 70 && power <= 88) ? '#2ecc71' : '#f39c12';
        ctx.fillRect(player.x - 10, player.y - 45, (power / 100) * 50, 10);
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.strokeRect(player.x - 10, player.y - 45, 50, 10);
    }

    // 5. 농구공들
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

components.html(game_2d_html, height=580)
