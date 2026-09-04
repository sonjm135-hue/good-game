import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🎮 Classic Breakout Game",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 클래식 벽돌깨기 게임")

st.markdown("""
### 🕹️ 조작 방법
* **키보드**: `←` / `→` (좌우 방향키)
* **마우스**: 게임 화면 안에서 마우스를 좌우로 움직여 패들을 조작할 수 있습니다.
* 모든 벽돌을 깨뜨리면 게임에서 승리합니다!
""")

game_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #0f172a; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #1e293b; border: 4px solid #38bdf8; border-radius: 12px; box-shadow: 0 0 25px rgba(56, 189, 248, 0.3); }
        #hud {
            position: absolute; top: 20px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 20px; font-weight: bold;
            background: rgba(15, 23, 42, 0.85); padding: 10px 30px; border-radius: 8px; border: 2px solid #38bdf8;
            display: flex; gap: 40px; align-items: center;
        }
        #message {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; font-weight: 900; color: #facc15; text-shadow: 0 0 15px rgba(250, 204, 21, 0.8);
            opacity: 0; transition: opacity 0.3s; pointer-events: none; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">
            <div>SCORE: <span id="score" style="color:#38bdf8;">0</span></div>
            <div>LIVES: <span id="lives" style="color:#f43f5e;">❤️❤️❤️</span></div>
        </div>
        <div id="message">STAGE CLEAR! 🎉</div>
        <canvas id="gameCanvas" width="800" height="500"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const livesEl = document.getElementById('lives');
const messageEl = document.getElementById('message');

let score = 0;
let lives = 3;
let gameOver = false;

// 패들 설정
const paddle = {
    w: 110,
    h: 14,
    x: (canvas.width - 110) / 2,
    y: canvas.height - 30,
    speed: 8,
    dx: 0
};

// 공 설정
const ball = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    r: 8,
    speed: 5,
    dx: 4,
    dy: -4
};

// 벽돌 설정
const brickRowCount = 5;
const brickColumnCount = 8;
const brickPadding = 12;
const brickOffsetTop = 60;
const brickOffsetLeft = 40;
const brickWidth = (canvas.width - (brickOffsetLeft * 2) - (brickPadding * (brickColumnCount - 1))) / brickColumnCount;
const brickHeight = 20;

const brickColors = ['#f43f5e', '#fb923c', '#facc15', '#4ade80', '#38bdf8'];

const bricks = [];
for (let c = 0; c < brickColumnCount; c++) {
    bricks[c] = [];
    for (let r = 0; r < brickRowCount; r++) {
        bricks[c][r] = { x: 0, y: 0, status: 1, color: brickColors[r] };
    }
}

// 키보드 및 마우스 이벤트
let rightPressed = false;
let leftPressed = false;

document.addEventListener('keydown', (e) => {
    if (e.key === 'Right' || e.key === 'ArrowRight') rightPressed = true;
    if (e.key === 'Left' || e.key === 'ArrowLeft') leftPressed = true;
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'Right' || e.key === 'ArrowRight') rightPressed = false;
    if (e.key === 'Left' || e.key === 'ArrowLeft') leftPressed = false;
});

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const relativeX = e.clientX - rect.left;
    if (relativeX > 0 && relativeX < canvas.width) {
        paddle.x = relativeX - paddle.w / 2;
    }
});

function showMessage(txt) {
    messageEl.innerText = txt;
    messageEl.style.opacity = '1';
}

function collisionDetection() {
    let activeBricks = 0;
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            const b = bricks[c][r];
            if (b.status === 1) {
                activeBricks++;
                if (ball.x > b.x && ball.x < b.x + brickWidth && ball.y > b.y && ball.y < b.y + brickHeight) {
                    ball.dy = -ball.dy;
                    b.status = 0;
                    score += 10;
                    scoreEl.innerText = score;
                }
            }
        }
    }

    if (activeBricks === 0 && !gameOver) {
        gameOver = true;
        showMessage("YOU WIN! 🎉");
    }
}

function update() {
    if (gameOver) return;

    // 패들 이동
    if (rightPressed && paddle.x < canvas.width - paddle.w) {
        paddle.x += paddle.speed;
    } else if (leftPressed && paddle.x > 0) {
        paddle.x -= paddle.speed;
    }

    // 공 이동
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 벽 충돌 (좌, 우)
    if (ball.x + ball.r > canvas.width || ball.x - ball.r < 0) {
        ball.dx = -ball.dx;
    }

    // 천장 충돌
    if (ball.y - ball.r < 0) {
        ball.dy = -ball.dy;
    }

    // 바닥/패들 충돌
    if (ball.y + ball.r > paddle.y && ball.x > paddle.x && ball.x < paddle.x + paddle.w) {
        // 패들의 어느 부위에 맞았는지에 따라 반사 각도 조절
        const collidePoint = ball.x - (paddle.x + paddle.w / 2);
        ball.dx = collidePoint * 0.15;
        ball.dy = -Math.abs(ball.dy);
    } else if (ball.y + ball.r > canvas.height) {
        lives--;
        livesEl.innerText = '❤️'.repeat(lives);

        if (lives <= 0) {
            gameOver = true;
            showMessage("GAME OVER 💀");
        } else {
            // 위치 리셋
            ball.x = canvas.width / 2;
            ball.y = canvas.height - 50;
            ball.dx = 4;
            ball.dy = -4;
            paddle.x = (canvas.width - paddle.w) / 2;
        }
    }

    collisionDetection();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 벽돌 그리기
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            if (bricks[c][r].status === 1) {
                const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                bricks[c][r].x = brickX;
                bricks[c][r].y = brickY;

                ctx.fillStyle = bricks[c][r].color;
                ctx.beginPath();
                ctx.roundRect(brickX, brickY, brickWidth, brickHeight, 4);
                ctx.fill();
            }
        }
    }

    // 패들 그리기
    ctx.fillStyle = '#38bdf8';
    ctx.beginPath();
    ctx.roundRect(paddle.x, paddle.y, paddle.w, paddle.h, 6);
    ctx.fill();

    // 공 그리기
    ctx.fillStyle = '#facc15';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fill();
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

components.html(game_html, height=580)
