import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 커리 vs 르브론 1v1 시그니처 배틀",
    page_icon="🏀",
    layout="centered"
)

st.title("🏀 커리 vs 르브론 1v1 리얼 배틀")
st.caption("업로드된 실제 슛폼/세레머니 동작이 적용된 2인용 농구 게임!")

st.markdown("""
| 선수 | 캐릭터 | 이동 키 | 슛 키 | 시그니처 모션 |
| :--- | :--- | :--- | :--- | :--- |
| **🔴 P1 (왼쪽)** | **스테판 커리** | `W`, `A`, `S`, `D` | `F` | 슛 동작 & 득점 시 **'Night Night' 세레머니** |
| **🔵 P2 (오른쪽)** | **르브론 제임스** | `↑`, `←`, `↓`, `→` | `Enter` | **고기놀이 Jump 페이드어웨이 슛폼** |
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

// 게임 상태
let p1 = { x: 150, y: 300, vx: 0, vy: 0, radius: 25, color: '#f39c12', score: 0, name: "커리 (P1)", state: 'idle', stateTimer: 0 };
let p2 = { x: 650, y: 300, vx: 0, vy: 0, radius: 25, color: '#8e44ad', score: 0, name: "르브론 (P2)", state: 'idle', stateTimer: 0 };
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
    // 타이머 관리 (슛폼 및 세레머니 모션 유지)
    if (p1.stateTimer > 0) p1.stateTimer--; else p1.state = 'idle';
    if (p2.stateTimer > 0) p2.stateTimer--; else p2.state = 'idle';

    // P1 (커리)
    p1.vx = 0;
    if (keys['a'] || keys['A']) p1.vx = -speed;
    if (keys['d'] || keys['D']) p1.vx = speed;
    if ((keys['w'] || keys['W']) && p1.y >= 345) p1.vy = jump;
    if ((keys['f'] || keys['F']) && ball.holder === p1) {
        shootBall(p1, 1);
        p1.state = 'shooting';
        p1.stateTimer = 30;
    }

    // P2 (르브론)
    p2.vx = 0;
    if (keys['ArrowLeft']) p2.vx = -speed;
    if (keys['ArrowRight']) p2.vx = speed;
    if (keys['ArrowUp'] && p2.y >= 345) p2.vy = jump;
    if (keys['Enter'] && ball.holder === p2) {
        shootBall(p2, -1);
        p2.state = 'shooting';
        p2.stateTimer = 30;
    }

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
                if (h.side === 'left') {
                    p2.score += 2;
                    p2.state = 'celebrate';
                    p2.stateTimer = 60;
                } else {
                    p1.score += 2;
                    p1.state = 'celebrate'; // 커리 Night Night 세레머니
                    p1.stateTimer = 60;
                }
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

// 캔버스 모션 그리기 (커리 & 르브론 폼 연출)
function drawPlayer(p, isCurry) {
    ctx.save();
    ctx.translate(p.x, p.y);

    // 몸통/유니폼
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(0, 10, p.radius, 0, Math.PI);
    ctx.fill();

    // 얼굴 Base
    ctx.fillStyle = isCurry ? '#d2b48c' : '#8b5a2b';
    ctx.beginPath();
    ctx.arc(0, -5, 18, 0, Math.PI * 2);
    ctx.fill();

    // 수염 표현 (르브론: 풍성한 수염 / 커리: 옅은 수염)
    ctx.fillStyle = '#1a1a1a';
    if (!isCurry) {
        ctx.fillRect(-12, 0, 24, 12); // 르브론 턱수염
    } else {
        ctx.fillRect(-8, 5, 16, 4);   // 커리 수염
    }

    // 상태별 포즈 및 세레머니 연출
    if (p.state === 'shooting') {
        // 슛 동작 (손을 위로 쭉 뻗는 팔 렌더링)
        ctx.strokeStyle = isCurry ? '#d2b48c' : '#8b5a2b';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(0, -10);
        ctx.lineTo(isCurry ? 15 : -15, -35); // 슛 발사각 포즈
        ctx.stroke();

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Arial';
        ctx.fillText(isCurry ? "🎯 Quick Release!" : "💥 Fadeaway!", 0, -45);
    } else if (p.state === 'celebrate') {
        if (isCurry) {
            // 커리 'Night Night' 잘자요 세레머니
            ctx.fillStyle = '#f1c40f';
            ctx.font = 'bold 14px Arial';
            ctx.fillText("😴 Night Night~!", 0, -40);
            
            // 두 손 모아 뺨에 대는 동작 시각화
            ctx.strokeStyle = '#d2b48c';
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.moveTo(0, -5);
            ctx.lineTo(12, -15);
            ctx.stroke();
        } else {
            // 르브론 왕관/포효 세레머니
            ctx.fillStyle = '#f1c40f';
            ctx.font = 'bold 14px Arial';
            ctx.fillText("👑 The KING!", 0, -40);
        }
    }

    ctx.restore();

    // 이름 표기
    ctx.fillStyle = '#fff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(p.name, p.x, p.y - p.radius - 10);
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
    drawPlayer(p1, true);  // 커리
    drawPlayer(p2, false); // 르브론

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
