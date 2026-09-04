import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 Classic Basketball Arcade",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Classic Basketball Arcade Game")

st.markdown("""
### 🎮 게임 방법
1. 화면을 **마우스 클릭(또는 터치)**하여 공을 당긴 후 떼면, **화살표 방향과 힘으로 공이 발사**됩니다.
2. 제한시간(60초) 동안 최대한 많은 슛을 성공시켜 높은 점수를 획득하세요!
3. 골대 그물에 깔끔하게 들어가면 추가 점수를 받습니다.
""")

game_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #1a1a24; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #232332; border: 4px solid #fff; border-radius: 12px; box-shadow: 0 0 25px rgba(0,0,0,0.7); cursor: crosshair; }
        #hud {
            position: absolute; top: 20px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 22px; font-weight: bold;
            background: rgba(0,0,0,0.8); padding: 10px 30px; border-radius: 8px; border: 2px solid #ff9900;
            display: flex; gap: 40px; align-items: center;
        }
        #message {
            position: absolute; top: 30%; left: 50%; transform: translate(-50%, -50%);
            font-size: 48px; font-weight: 900; color: #ffeb3b; text-shadow: 0 0 15px #ff9800;
            opacity: 0; transition: opacity 0.3s; pointer-events: none; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">
            <div>SCORE: <span id="score" style="color:#ff9900;">0</span></div>
            <div>TIME: <span id="timer" style="color:#00e676;">60</span>s</div>
            <div>BEST: <span id="high-score" style="color:#00e5ff;">0</span></div>
        </div>
        <div id="message">SWISH! 🔥</div>
        <canvas id="gameCanvas" width="900" height="550"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const timerEl = document.getElementById('timer');
const highScoreEl = document.getElementById('high-score');
const messageEl = document.getElementById('message');

let score = 0;
let highScore = 0;
let timeLeft = 60;
let gameActive = true;

// 물리 파라미터
const gravity = 0.35;
const bounce = 0.6;

// 공 객체
const ball = {
    x: 220,
    y: 400,
    r: 16,
    vx: 0,
    vy: 0,
    isDragging: false,
    isFlying: false,
    dragStartX: 0,
    dragStartY: 0,
    reset: function() {
        this.x = 220;
        this.y = 400;
        this.vx = 0;
        this.vy = 0;
        this.isFlying = false;
        this.isDragging = false;
    }
};

// 골대 객체
const hoop = {
    x: 720,
    y: 220,
    rimLeft: 670,
    rimRight: 740,
    rimY: 220,
    scored: false
};

// 타이머 루프
const timerInterval = setInterval(() => {
    if (gameActive && timeLeft > 0) {
        timeLeft--;
        timerEl.innerText = timeLeft;
        if (timeLeft === 0) {
            gameActive = false;
            showMessage("GAME OVER! 🏀");
        }
    }
}, 1000);

// 조작 이벤트
canvas.addEventListener('mousedown', (e) => {
    if (!gameActive || ball.isFlying) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const dist = Math.hypot(mouseX - ball.x, mouseY - ball.y);
    if (dist < ball.r * 2.5) {
        ball.isDragging = true;
        ball.dragStartX = mouseX;
        ball.dragStartY = mouseY;
    }
});

canvas.addEventListener('mousemove', (e) => {
    if (ball.isDragging) {
        const rect = canvas.getBoundingClientRect();
        ball.x = e.clientX - rect.left;
        ball.y = e.clientY - rect.top;
    }
});

canvas.addEventListener('mouseup', (e) => {
    if (ball.isDragging) {
        ball.isDragging = false;
        ball.isFlying = true;

        // 드래그 거리와 방향 계산
        const dx = 220 - ball.x;
        const dy = 400 - ball.y;

        ball.vx = dx * 0.12;
        ball.vy = dy * 0.12;

        hoop.scored = false;
    }
});

function showMessage(txt) {
    messageEl.innerText = txt;
    messageEl.style.opacity = '1';
    setTimeout(() => { messageEl.style.opacity = '0'; }, 1200);
}

function update() {
    if (ball.isFlying) {
        ball.x += ball.vx;
        ball.y += ball.vy;
        ball.vy += gravity;

        // 바닥 충돌
        if (ball.y + ball.r > 480) {
            ball.y = 480 - ball.r;
            ball.vy *= -bounce;
            ball.vx *= 0.8;

            if (Math.abs(ball.vy) < 1 && Math.abs(ball.vx) < 1) {
                ball.reset();
            }
        }

        // 벽 충돌
        if (ball.x + ball.r > canvas.width || ball.x - ball.r < 0) {
            ball.vx *= -bounce;
        }

        // 골대 백보드 충돌
        if (ball.x + ball.r > 745 && ball.x - ball.r < 755 && ball.y > 140 && ball.y < 260) {
            ball.vx *= -0.7;
        }

        // 링 좌우 충돌
        const distRimL = Math.hypot(ball.x - hoop.rimLeft, ball.y - hoop.rimY);
        const distRimR = Math.hypot(ball.x - hoop.rimRight, ball.y - hoop.rimY);

        if (distRimL < ball.r) { ball.vx *= -0.6; ball.vy *= -0.6; }
        if (distRimR < ball.r) { ball.vx *= -0.6; ball.vy *= -0.6; }

        // 득점 판정
        if (!hoop.scored && ball.vy > 0 && ball.x > hoop.rimLeft && ball.x < hoop.rimRight && Math.abs(ball.y - hoop.rimY) < 12) {
            hoop.scored = true;
            score += 2;
            scoreEl.innerText = score;
            if (score > highScore) {
                highScore = score;
                highScoreEl.innerText = highScore;
            }
            showMessage("SWISH! +2 🔥");
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 바닥
    ctx.fillStyle = '#b71c1c';
    ctx.fillRect(0, 480, canvas.width, 70);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 476, canvas.width, 4);

    // 골대 백보드
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(745, 120, 10, 130);
    ctx.strokeStyle = '#d32f2f';
    ctx.lineWidth = 3;
    ctx.strokeRect(745, 160, 10, 60);

    // 골대 링 및 그물
    ctx.strokeStyle = '#ff6f00';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(hoop.rimLeft, hoop.rimY);
    ctx.lineTo(hoop.rimRight, hoop.rimY);
    ctx.stroke();

    // 그물 그래픽
    ctx.strokeStyle = 'rgba(255,255,255,0.5)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(hoop.rimLeft + 5, hoop.rimY);
    ctx.lineTo(hoop.rimLeft + 15, hoop.rimY + 45);
    ctx.lineTo(hoop.rimRight - 15, hoop.rimY + 45);
    ctx.lineTo(hoop.rimRight - 5, hoop.rimY);
    ctx.stroke();

    // 조준 화살표 (드래그 중일 때)
    if (ball.isDragging) {
        ctx.strokeStyle = '#ffeb3b';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(ball.x, ball.y);
        ctx.lineTo(ball.x + (220 - ball.x) * 2, ball.y + (400 - ball.y) * 2);
        ctx.stroke();
        ctx.setLineDash([]);
    }

    // 농구공
    ctx.fillStyle = '#e65100';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 공 선 무늬
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, -0.5, 0.5);
    ctx.stroke();
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

components.html(game_html, height=600)
