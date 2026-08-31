import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 커리 vs 르브론 1v1 농구 대결",
    page_icon="🏀",
    layout="centered"
)

st.title("🏀 커리 vs 르브론 1v1 배틀")
st.caption("스테판 커리와 르브론 제임스의 2인용 키보드 대결!")

# 조작법 가이드
st.markdown("""
| 선수 | 캐릭터 | 이동 키 | 슛 키 |
| :--- | :--- | :--- | :--- |
| **🔴 P1 (왼쪽)** | **스테판 커리** | `W`, `A`, `S`, `D` | `F` |
| **🔵 P2 (오른쪽)** | **르브론 제임스** | `↑`, `←`, `↓`, `→` | `Enter` |
""")

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

// 얼굴 이미지 로드 (무료 SVG 일러스트 URL 활용)
const curryImg = new Image();
curryImg.src = 'https://api.dicebear.com/7.x/bottts/svg?seed=Curry'; // 커리 캐릭터 아이콘

const lebronImg = new Image();
lebronImg.src = 'https://api.dicebear.com/7.x/bottts/svg?seed=LeBron'; // 르브론 캐릭터 아이콘

// 게임 상태
let p1 = { x: 150, y: 300, vx: 0, vy: 0, radius: 25, color: '#f39c12', score: 0, img: curryImg, name: "커리", angle: 0 };
let p2 = { x: 650, y: 300, vx: 0, vy: 0, radius: 25, color: '#8e44ad', score: 0, img: lebronImg, name: "르브론", angle: 0 };
let ball = { x: 400, y: 200, vx: 0, vy: 0, radius: 12, color: '#f1c40f', holder: null };

const gravity = 0.4;
const speed = 5;
const jump = -10;

// 백보드 & 골대
const hoops = [
    { x: 50, y: 180, w: 10, h: 60, rimX: 75, rimY: 210, side: 'left' },
    { x: 740, y: 180, w: 10, h: 60, rimX: 725, rimY: 210, side: 'right' }
];

const keys = {};

window.addEventListener('keydown', e => { 
    keys[e.key] = true; 
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Enter"].indexOf(e.key) > -1) {
        e.preventDefault();
    }
});
window.addEventListener('keyup', e => { keys[e.key] = false; });

function update() {
    // P1 (커리) 이동
    p1.vx = 0;
    if (keys['a'] || keys['A']) { p1.vx = -speed; p1.angle = -0.2; }
    else if (keys['d'] || keys['D']) { p1.vx = speed; p1.angle = 0.2; }
    else { p1.angle = 0; }

    if ((keys['w'] || keys['W']) && p1.y >= 345) p1.vy = jump;
    if ((keys['f'] || keys['F']) && ball.holder === p1) shootBall(p1, 1);

    // P2 (르브론) 이동
    p2.vx = 0;
    if (keys['ArrowLeft']) { p2.vx = -speed; p2.angle = -0.2; }
    else if (keys['ArrowRight']) { p2.vx = speed; p2.angle = 0.2; }
    else { p2.angle = 0; }

    if (keys['ArrowUp'] && p2.y >= 345) p2.vy = jump;
    if (keys['Enter'] && ball.holder === p2) shootBall(p2, -1);

    // 중력 및 이동
    [p1, p2].forEach(p => {
        p.vy += gravity;
        p.x += p.vx;
        p.y += p.vy;

        if (p.x - p.radius < 0) p.x = p.radius;
        if (p.x + p.radius > canvas.width) p.x = canvas.width - p.radius;
        if (p.y + p.radius > 370) {
            p.y = 370 - p.radius;
            p.vy = 0;
        }
    });

    // 공 물리
    if (ball.holder) {
        ball.x = ball.holder.x;
        ball.y = ball.holder.y - 20;
    } else {
        ball.vy += gravity;
        ball.x += ball.vx;
        ball.y += ball.vy;

        if (ball.y + ball.radius > 370) {
            ball.y = 370 - ball.radius;
            ball.vy *= -0.6;
        }
        if (ball.x - ball.radius < 0 || ball.x + ball.radius > canvas.width) {
            ball.vx *= -0.8;
        }

        [p1, p2].forEach(p => {
            let dist = Math.hypot(p.x - ball.x, p.y - ball.y);
            if (dist < p.radius + ball.radius + 5) {
                ball.holder = p;
            }
        });

        // 득점 판정
        hoops.forEach(h => {
            let distToRim = Math.hypot(ball.x - h.rimX, ball.y - h.rimY);
            if (distToRim < 25 && ball.vy > 0) {
                if (h.side === 'left') p2.score += 2;
                else p1.score += 2;
                resetBall();
            }
        });
    }
}

function shootBall(player, dir) {
    ball.holder = null;
    ball.vx = dir * 10;
    ball.vy = -12;
}

function resetBall() {
    ball.holder = null;
    ball.x = 400;
    ball.y = 150;
    ball.vx = 0;
    ball.vy = 0;
}

function drawPlayer(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.angle); // 이동 시 회전 애니메이션

    // 유니폼 몸통
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(0, 10, p.radius, 0, Math.PI);
    ctx.fill();

    // 얼굴/캐릭터 이미지
    ctx.drawImage(p.img, -p.radius, -p.radius, p.radius * 2, p.radius * 2);

    ctx.restore();

    // 이름 표시
    ctx.fillStyle = '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(p.name, p.x, p.y - p.radius - 5);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 바닥 코트
    ctx.fillStyle = '#e67e22';
    ctx.fillRect(0, 370, canvas.width, 30);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(400, 370); ctx.lineTo(400, 200);
    ctx.stroke();

    // 골대
    hoops.forEach(h => {
        ctx.fillStyle = '#fff';
        ctx.fillRect(h.x, h.y, h.w, h.h);
        ctx.fillStyle = '#e74c3c';
        ctx.fillRect(h.side === 'left' ? h.x + 10 : h.x - 25, h.rimY, 25, 5);
    });

    // 캐릭터 그리기
    drawPlayer(p1);
    drawPlayer(p2);

    // 농구공
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = ball.color;
    ctx.fill();
    ctx.strokeStyle = '#d35400';
    ctx.stroke();
    ctx.closePath();

    // 점수판
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 22px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`🔥 커리: ${p1.score}`, 40, 40);
    ctx.textAlign = 'right';
    ctx.fillText(`👑 르브론: ${p2.score}`, 760, 40);
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

components.html(game_html, height=450)
