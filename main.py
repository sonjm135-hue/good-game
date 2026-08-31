import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 1v1 스트리트 농구 배틀",
    page_icon="🏀",
    layout="centered"
)

st.title("🏀 1v1 스트리트 농구 게임")
st.caption("친구와 한 키보드로 즐기는 2인용 실시간 농구 대결!")

# 게임 조작법 가이드
st.markdown("""
| 구분 | 🔴 선수 1 (왼쪽) | 🔵 선수 2 (오른쪽) |
| :--- | :--- | :--- |
| **이동** | `W`, `A`, `S`, `D` | `↑`, `←`, `↓`, `→` |
| **슛** | `F` 키 | `Enter` 키 |
""")

# JavaScript & HTML5 Canvas 기반 농구 게임 엔진
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; color: white; font-family: sans-serif; }
        canvas { border: 4px solid #fff; border-radius: 10px; background: #d35400; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="400"></canvas>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 게임 상태
let p1 = { x: 150, y: 300, vx: 0, vy: 0, radius: 20, color: '#e74c3c', score: 0, hasBall: false };
let p2 = { x: 650, y: 300, vx: 0, vy: 0, radius: 20, color: '#3498db', score: 0, hasBall: false };
let ball = { x: 400, y: 200, vx: 0, vy: 0, radius: 10, color: '#f39c12', holder: null };

const gravity = 0.4;
const speed = 5;
const jump = -10;

// 백보드 & 골대 정보
const hoops = [
    { x: 50, y: 180, w: 10, h: 60, rimX: 75, rimY: 210, side: 'left' },
    { x: 740, y: 180, w: 10, h: 60, rimX: 725, rimY: 210, side: 'right' }
];

const keys = {};

window.addEventListener('keydown', e => { keys[e.key] = true; });
window.addEventListener('keyup', e => { keys[e.key] = false; });

function update() {
    // P1 조작 (WASD + F)
    p1.vx = 0;
    if (keys['a'] || keys['A']) p1.vx = -speed;
    if (keys['d'] || keys['D']) p1.vx = speed;
    if ((keys['w'] || keys['W']) && p1.y >= 350) p1.vy = jump;
    if ((keys['f'] || keys['F']) && ball.holder === p1) shootBall(p1, 1);

    // P2 조작 (화살표 + Enter)
    p2.vx = 0;
    if (keys['ArrowLeft']) p2.vx = -speed;
    if (keys['ArrowRight']) p2.vx = speed;
    if (keys['ArrowUp'] && p2.y >= 350) p2.vy = jump;
    if (keys['Enter'] && ball.holder === p2) shootBall(p2, -1);

    // 중력 및 이동 처리
    [p1, p2].forEach(p => {
        p.vy += gravity;
        p.x += p.vx;
        p.y += p.vy;

        // 벽 & 바닥 충돌
        if (p.x - p.radius < 0) p.x = p.radius;
        if (p.x + p.radius > canvas.width) p.x = canvas.width - p.radius;
        if (p.y + p.radius > 370) {
            p.y = 370 - p.radius;
            p.vy = 0;
        }
    });

    // 공 물리 업데이트
    if (ball.holder) {
        ball.x = ball.holder.x;
        ball.y = ball.holder.y - 15;
    } else {
        ball.vy += gravity;
        ball.x += ball.vx;
        ball.y += ball.vy;

        // 공 바닥 튕김
        if (ball.y + ball.radius > 370) {
            ball.y = 370 - ball.radius;
            ball.vy *= -0.6;
        }
        // 공 벽 튕김
        if (ball.x - ball.radius < 0 || ball.x + ball.radius > canvas.width) {
            ball.vx *= -0.8;
        }

        // 공 획득 판단
        [p1, p2].forEach(p => {
            let dist = Math.hypot(p.x - ball.x, p.y - ball.y);
            if (dist < p.radius + ball.radius + 5) {
                ball.holder = p;
            }
        });

        // 득점 판정
        hoops.forEach(h => {
            let distToRim = Math.hypot(ball.x - h.rimX, ball.y - h.rimY);
            if (distToRim < 20 && ball.vy > 0) {
                if (h.side === 'left') p2.score += 2;
                else p1.score += 2;
                resetBall();
            }
        });
    }
}

function shootBall(player, dir) {
    ball.holder = null;
    ball.vx = dir * 9;
    ball.vy = -11;
}

function resetBall() {
    ball.holder = null;
    ball.x = 400;
    ball.y = 150;
    ball.vx = 0;
    ball.vy = 0;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    # 바닥/코트 선
    ctx.fillStyle = '#e67e22';
    ctx.fillRect(0, 370, canvas.width, 30);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(400, 370); ctx.lineTo(400, 200);
    ctx.stroke();

    # 백보드 & 골대
    hoops.forEach(h => {
        ctx.fillStyle = '#fff';
        ctx.fillRect(h.x, h.y, h.w, h.h);
        ctx.fillStyle = '#e74c3c';
        ctx.fillRect(h.side === 'left' ? h.x + 10 : h.x - 25, h.rimY, 25, 5);
    });

    # 선수 1, 2
    [p1, p2].forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();
        ctx.closePath();
    });

    # 공
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = ball.color;
    ctx.fill();
    ctx.closePath();

    # 스코어보드
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    ctx.fillText(`🔴 P1: ${p1.score}`, 50, 40);
    ctx.fillText(`🔵 P2: ${p2.score}`, 650, 40);
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

loop();
</script>
</body>
</html>
"""

# HTML 요소 렌더링
components.html(game_html, height=450)
