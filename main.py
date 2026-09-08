import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2P Basketball with Shooting Animation", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #121212; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }
        canvas { background: #222; border-bottom: 8px solid #555; }
        #ui {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 40px; color: #fff; font-size: 24px; font-weight: bold;
            background: rgba(0,0,0,0.6); padding: 10px 30px; border-radius: 15px; z-index: 10;
        }
        .p1-color { color: #ff5252; }
        .p2-color { color: #448aff; }
        #game-over {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); display: none; flex-direction: column;
            justify-content: center; align-items: center; color: #fff; z-index: 20;
        }
        #restart-btn {
            margin-top: 20px; padding: 12px 30px; font-size: 22px; font-weight: bold;
            color: #111; background-color: #ffb74d; border: none; border-radius: 8px;
            cursor: pointer; transition: 0.2s;
        }
        #restart-btn:hover { transform: scale(1.05); }
        #controls-guide {
            position: absolute; bottom: 15px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 50px; color: #aaa; font-size: 14px;
            background: rgba(0,0,0,0.5); padding: 8px 20px; border-radius: 10px;
        }
    </style>
</head>
<body>
    <div id="ui">
        <div>1P: <span id="p1-score" class="p1-color">0</span></div>
        <div>TIME: <span id="timer" style="color: #ffeb3b;">60</span>s</div>
        <div>2P: <span id="p2-score" class="p2-color">0</span></div>
    </div>

    <div id="canvas-container">
        <canvas id="gameCanvas" width="900" height="500"></canvas>
    </div>

    <div id="controls-guide">
        <div><b class="p1-color">1P (레드)</b>: A/D (이동) | W (점프) | Space (슛)</div>
        <div><b class="p2-color">2P (블루)</b>: ←/→ (이동) | ↑ (점프) | Enter (슛)</div>
    </div>

    <div id="game-over">
        <h1 id="winner-text" style="font-size: 48px; margin-bottom: 10px;">PLAYER 1 WIN!</h1>
        <p style="font-size: 24px;">최종 스코어 - 1P: <span id="final-p1">0</span> | 2P: <span id="final-p2">0</span></p>
        <button id="restart-btn" onclick="resetGame()">다시 대결하기</button>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        let p1Score = 0, p2Score = 0, timeLeft = 60;
        let gameActive = true, timerInterval;

        const keys = {};

        // 플레이어 설정
        const p1 = {
            x: 180, y: 380, width: 35, height: 60,
            color: '#ff5252', vx: 0, vy: 0, isGrounded: false,
            hasBall: false, id: 1, armAngle: 0, shootAnimTimer: 0, facing: 1
        };

        const p2 = {
            x: 685, y: 380, width: 35, height: 60,
            color: '#448aff', vx: 0, vy: 0, isGrounded: false,
            hasBall: false, id: 2, armAngle: 0, shootAnimTimer: 0, facing: -1
        };

        // 농구공 설정
        const ball = {
            x: 450, y: 200, radius: 12,
            vx: 0, vy: 0, holder: null, rotation: 0, trail: []
        };

        // 골대 설정 (좌/우)
        const hoops = [
            { x: 50, y: 200, rimX: 80, rimY: 240, side: 'left' },
            { x: 850, y: 200, rimX: 820, rimY: 240, side: 'right' }
        ];

        const gravity = 0.45;
        const groundY = 440;

        function init() {
            window.addEventListener('keydown', e => {
                keys[e.code] = true;
                if (e.code === 'Space' && p1.hasBall) shootBall(p1);
                if (e.code === 'Enter' && p2.hasBall) shootBall(p2);
            });

            window.addEventListener('keyup', e => {
                keys[e.code] = false;
            });

            startTimer();
            requestAnimationFrame(gameLoop);
        }

        function startTimer() {
            clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                if (!gameActive) return;
                timeLeft--;
                document.getElementById('timer').innerText = timeLeft;
                if (timeLeft <= 0) endGame();
            }, 1000);
        }

        function resetGame() {
            p1Score = 0; p2Score = 0; timeLeft = 60; gameActive = true;
            document.getElementById('p1-score').innerText = 0;
            document.getElementById('p2-score').innerText = 0;
            document.getElementById('timer').innerText = 60;
            document.getElementById('game-over').style.display = 'none';

            p1.x = 180; p1.y = 380; p1.vx = 0; p1.vy = 0;
            p2.x = 685; p2.y = 380; p2.vx = 0; p2.vy = 0;
            resetBall();
            startTimer();
        }

        function resetBall() {
            ball.x = 450;
            ball.y = 200;
            ball.vx = 0;
            ball.vy = 0;
            ball.holder = null;
            ball.trail = [];
            p1.hasBall = false;
            p2.hasBall = false;
        }

        function shootBall(player) {
            // 상대 골대 조준 계산
            const targetHoop = player.id === 1 ? hoops[1] : hoops[0];
            const targetX = targetHoop.rimX;
            const targetY = targetHoop.rimY;

            // 슛 애니메이션 발동
            player.shootAnimTimer = 15;
            player.hasBall = false;
            ball.holder = null;

            // 물리 투구 궤적 계산 (골대 쪽으로 예쁘게 비상)
            const dx = targetX - (player.x + player.width / 2);
            const dist = Math.abs(dx);

            ball.x = player.x + player.width / 2 + player.facing * 10;
            ball.y = player.y - 10;

            // 거리 기반 자동 정밀 슛 속도 산출
            ball.vx = (dx / dist) * (6.5 + dist * 0.008) + player.vx * 0.3;
            ball.vy = -12.5 - Math.min(dist * 0.01, 3);
        }

        function updatePlayer(p, leftKey, rightKey, jumpKey) {
            if (keys[leftKey]) { p.vx = -4; p.facing = -1; }
            else if (keys[rightKey]) { p.vx = 4; p.facing = 1; }
            else p.vx = 0;

            if (keys[jumpKey] && p.isGrounded) {
                p.vy = -11;
                p.isGrounded = false;
            }

            p.vy += gravity;
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) p.x = 0;
            if (p.x + p.width > canvas.width) p.x = canvas.width - p.width;

            if (p.y + p.height >= groundY) {
                p.y = groundY - p.height;
                p.vy = 0;
                p.isGrounded = true;
            }

            // 슛 애니메이션 타이머 감소
            if (p.shootAnimTimer > 0) {
                p.shootAnimTimer--;
                p.armAngle = -Math.PI / 3 * p.facing; // 슛할 때 팔을 들어올림
            } else {
                p.armAngle = p.hasBall ? -Math.PI / 6 * p.facing : 0;
            }

            // 공을 가지고 있을 때의 위치 업데이트
            if (!ball.holder) {
                const dist = Math.hypot((p.x + p.width/2) - ball.x, (p.y + p.height/2) - ball.y);
                if (dist < 38) {
                    ball.holder = p;
                    p.hasBall = true;
                }
            } else if (ball.holder === p) {
                ball.x = p.x + p.width / 2 + p.facing * 12;
                ball.y = p.y + 10;
                ball.vx = 0;
                ball.vy = 0;
            }
        }

        function updateBall() {
            if (ball.holder) {
                ball.trail = [];
                return;
            }

            ball.vy += gravity;
            ball.x += ball.vx;
            ball.y += ball.vy;

            // 공 회전 및 궤적 잔상 효과
            ball.rotation += ball.vx * 0.05;
            ball.trail.push({ x: ball.x, y: ball.y });
            if (ball.trail.length > 8) ball.trail.shift();

            // 바닥 튕김
            if (ball.y + ball.radius >= groundY) {
                ball.y = groundY - ball.radius;
                ball.vy *= -0.65;
                ball.vx *= 0.8;
            }

            // 벽 튕김
            if (ball.x - ball.radius <= 0 || ball.x + ball.radius >= canvas.width) {
                ball.vx *= -0.7;
            }

            // 골대 충돌 및 득점 체크
            hoops.forEach(hoop => {
                // 백보드 바운스
                const isLeftBb = hoop.side === 'left' && Math.abs(ball.x - hoop.x) < 15;
                const isRightBb = hoop.side === 'right' && Math.abs(ball.x - hoop.x) < 15;
                if ((isLeftBb || isRightBb) && ball.y > hoop.y && ball.y < hoop.y + 80) {
                    ball.vx *= -0.7;
                }

                // 림 득점 (통과 애니메이션)
                const distToRim = Math.hypot(ball.x - hoop.rimX, ball.y - hoop.rimY);
                if (distToRim < 18 && ball.vy > 0) {
                    if (hoop.side === 'right') {
                        p1Score += 2;
                        document.getElementById('p1-score').innerText = p1Score;
                    } else {
                        p2Score += 2;
                        document.getElementById('p2-score').innerText = p2Score;
                    }
                    resetBall();
                }
            });
        }

        function endGame() {
            gameActive = false;
            clearInterval(timerInterval);
            
            const winnerText = document.getElementById('winner-text');
            if (p1Score > p2Score) {
                winnerText.innerText = "PLAYER 1 WIN!";
                winnerText.style.color = "#ff5252";
            } else if (p2Score > p1Score) {
                winnerText.innerText = "PLAYER 2 WIN!";
                winnerText.style.color = "#448aff";
            } else {
                winnerText.innerText = "DRAW GAME!";
                winnerText.style.color = "#ffeb3b";
            }

            document.getElementById('final-p1').innerText = p1Score;
            document.getElementById('final-p2').innerText = p2Score;
            document.getElementById('game-over').style.display = 'flex';
        }

        function drawPlayer(p) {
            ctx.save();
            ctx.translate(p.x + p.width / 2, p.y + p.height / 2);

            // 몸통
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.width / 2, -p.height / 2, p.width, p.height);

            // 눈 (바라보는 방향)
            ctx.fillStyle = '#fff';
            ctx.fillRect(p.facing * 5, -p.height / 2 + 8, 8, 8);

            // 팔 애니메이션
            ctx.strokeStyle = p.color;
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.moveTo(0, -5);
            const armX = Math.cos(p.armAngle) * 22 * p.facing;
            const armY = Math.sin(p.armAngle) * 22;
            ctx.lineTo(armX, armY);
            ctx.stroke();

            ctx.restore();
        }

        function drawBall() {
            // 공 잔상 애니메이션 (궤적)
            for (let i = 0; i < ball.trail.length; i++) {
                const t = ball.trail[i];
                ctx.fillStyle = `rgba(255, 152, 0, ${ (i + 1) / 12 })`;
                ctx.beginPath();
                ctx.arc(t.x, t.y, ball.radius * ((i + 1) / 10), 0, Math.PI * 2);
                ctx.fill();
            }

            // 농구공 본체 + 회전 무늬
            ctx.save();
            ctx.translate(ball.x, ball.y);
            ctx.rotate(ball.rotation);

            ctx.fillStyle = '#ff9800';
            ctx.beginPath();
            ctx.arc(0, 0, ball.radius, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = '#222';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(0, 0, ball.radius, 0, Math.PI * 2);
            ctx.moveTo(-ball.radius, 0);
            ctx.lineTo(ball.radius, 0);
            ctx.moveTo(0, -ball.radius);
            ctx.lineTo(0, ball.radius);
            ctx.stroke();

            ctx.restore();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 코트 바닥
            ctx.fillStyle = '#3e2723';
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = '#ffb74d';
            ctx.fillRect(0, groundY, canvas.width, 5);

            // 골대 그리기
            hoops.forEach(h => {
                // 지지대 및 백보드
                ctx.fillStyle = '#fff';
                ctx.fillRect(h.side === 'left' ? h.x - 10 : h.x, h.y, 10, 80);
                // 림
                ctx.strokeStyle = '#e65100';
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.arc(h.rimX, h.rimY, 15, 0, Math.PI);
                ctx.stroke();
            });

            // 플레이어 및 공 그리기
            drawPlayer(p1);
            drawPlayer(p2);
            drawBall();
        }

        function gameLoop() {
            if (gameActive) {
                updatePlayer(p1, 'KeyA', 'KeyD', 'KeyW');
                updatePlayer(p2, 'ArrowLeft', 'ArrowRight', 'ArrowUp');
                updateBall();
            }
            draw();
            requestAnimationFrame(gameLoop);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

components.html(game_html, height=600)
