import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🐍 Classic Snake Game",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 클래식 스네이크 게임")

st.markdown("""
### 🕹️ 조작 방법
* **키보드 방향키**: `↑`, `↓`, `←`, `→` (이동)
* 빨간 사과🍎를 먹으면 몸통이 길어지고 10점을 획득합니다.
* 벽에 부딪히거나 자신의 몸통에 부딪히면 게임이 종료됩니다.
""")

game_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #0f172a; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #1e293b; border: 4px solid #10b981; border-radius: 12px; box-shadow: 0 0 25px rgba(16, 185, 129, 0.3); }
        #hud {
            position: absolute; top: 20px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 20px; font-weight: bold;
            background: rgba(15, 23, 42, 0.85); padding: 10px 30px; border-radius: 8px; border: 2px solid #10b981;
            display: flex; gap: 40px; align-items: center;
        }
        #message {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; font-weight: 900; color: #ef4444; text-shadow: 0 0 15px rgba(239, 68, 68, 0.8);
            opacity: 0; transition: opacity 0.3s; pointer-events: none; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">
            <div>SCORE: <span id="score" style="color:#10b981;">0</span></div>
            <div>HIGH SCORE: <span id="high-score" style="color:#f59e0b;">0</span></div>
        </div>
        <div id="message">GAME OVER 💀<br><span style="font-size:20px; color:#fff;">방향키를 눌러 다시 시작</span></div>
        <canvas id="gameCanvas" width="600" height="400"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const highScoreEl = document.getElementById('high-score');
const messageEl = document.getElementById('message');

const gridSize = 20;
const tileCountX = canvas.width / gridSize;
const tileCountY = canvas.height / gridSize;

let snake = [{ x: 10, y: 10 }];
let dx = 1;
let dy = 0;
let apple = { x: 15, y: 10 };
let score = 0;
let highScore = 0;
let gameOver = false;
let gameInterval;

function generateApple() {
    apple.x = Math.floor(Math.random() * tileCountX);
    apple.y = Math.floor(Math.random() * tileCountY);
    // 사과가 뱀 몸통 위에 생성되지 않도록 방지
    snake.forEach(segment => {
        if (segment.x === apple.x && segment.y === apple.y) {
            generateApple();
        }
    });
}

function update() {
    if (gameOver) return;

    const head = { x: snake[0].x + dx, y: snake[0].y + dy };

    // 벽 충돌 체크
    if (head.x < 0 || head.x >= tileCountX || head.y < 0 || head.y >= tileCountY) {
        endGame();
        return;
    }

    // 자기 몸통 충돌 체크
    for (let i = 0; i < snake.length; i++) {
        if (snake[i].x === head.x && snake[i].y === head.y) {
            endGame();
            return;
        }
    }

    snake.unshift(head);

    // 사과 먹기
    if (head.x === apple.x && head.y === apple.y) {
        score += 10;
        scoreEl.innerText = score;
        if (score > highScore) {
            highScore = score;
            highScoreEl.innerText = highScore;
        }
        generateApple();
    } else {
        snake.pop();
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 격자 그리기
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }

    // 사과 그리기
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(apple.x * gridSize + gridSize/2, apple.y * gridSize + gridSize/2, gridSize/2 - 2, 0, Math.PI * 2);
    ctx.fill();

    // 뱀 그리기
    snake.forEach((segment, index) => {
        ctx.fillStyle = index === 0 ? '#10b981' : '#34d399';
        ctx.beginPath();
        ctx.roundRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2, 4);
        ctx.fill();
    });
}

function endGame() {
    gameOver = true;
    messageEl.style.opacity = '1';
}

function resetGame() {
    snake = [{ x: 10, y: 10 }];
    dx = 1; dy = 0;
    score = 0;
    scoreEl.innerText = score;
    gameOver = false;
    messageEl.style.opacity = '0';
    generateApple();
}

document.addEventListener('keydown', (e) => {
    if (gameOver) {
        resetGame();
        return;
    }

    switch (e.key) {
        case 'ArrowUp':
            if (dy !== 1) { dx = 0; dy = -1; }
            break;
        case 'ArrowDown':
            if (dy !== -1) { dx = 0; dy = 1; }
            break;
        case 'ArrowLeft':
            if (dx !== 1) { dx = -1; dy = 0; }
            break;
        case 'ArrowRight':
            if (dx !== -1) { dx = 1; dy = 0; }
            break;
    }
});

function gameLoop() {
    update();
    draw();
}

generateApple();
setInterval(gameLoop, 100);
</script>
</body>
</html>"""

components.html(game_html, height=520)
