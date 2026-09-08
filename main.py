import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Crazy Basketball 2P", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #0d0e15; font-family: 'Impact', 'Arial Black', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }
        canvas { background: #181925; border-bottom: 10px solid #ff9800; box-shadow: 0 0 30px rgba(255, 152, 0, 0.3); }
        
        #ui {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 40px; color: #fff; font-size: 26px; font-weight: bold;
            background: rgba(0,0,0,0.85); padding: 12px 35px; border-radius: 20px; z-index: 10; border: 2px solid #ff9800;
            box-shadow: 0 0 15px rgba(0,0,0,0.8);
        }
        .p1-color { color: #ff3d00; text-shadow: 0 0 8px #ff3d00; }
        .p2-color { color: #00e5ff; text-shadow: 0 0 8px #00e5ff; }
        .fire-text { color: #ffea00; animation: blink 0.3s infinite alternate; }

        @keyframes blink { from { opacity: 1; } to { opacity: 0.5; } }

        #game-over {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9); display: none; flex-direction: column;
            justify-content: center; align-items: center; color: #fff; z-index: 30;
        }
        #restart-btn {
            margin-top: 25px; padding: 15px 45px; font-size: 28px; font-weight: bold;
            color: #000; background: #ffea00; border: none; border-radius: 12px; cursor: pointer;
            box-shadow: 0 0 20px #ffea00; transition: 0.1s;
        }
        #restart-btn:hover { transform: scale(1.1); }

        #controls-guide {
            position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 40px; color: #fff; font-size: 13px; font-family: sans-serif;
            background: rgba(0,0,0,0.8); padding: 8px 25px; border-radius: 10px; border: 1px solid #444;
        }
        .key { background: #333; padding: 2px 6px; border-radius: 4px; border: 1px solid #666; color: #ffea00; }
    </style>
</head>
<body>
    <div id="ui">
        <div>1P <span id="p1-combo" class="fire-text"></span>: <span id="p1-score" class="p1-color">0</span></div>
        <div style="color: #ffea00;">TIME <span id="timer">45</span>s</div>
        <div>2P <span id="p2-combo" class="fire-text"></span>: <span id="p2-score" class="p2-color">0</span></div>
    </div>

    <div id="canvas-container">
        <canvas id="gameCanvas" width="960" height="520"></canvas>
    </div>

    <div id="controls-guide">
        <div><b class="p1-color">1P</b>: <span class="key">A</span><span class="key">D</span> 이동 | <span class="key">W</span> 점프 | <span class="key">Space</span> 슛 | <span class="key">E</span> 밀쳐내기/스틸</div>
        <div><b class="p2-color">2P</b>: <span class="key">←</span><span class="key">→</span> 이동 | <span class="key">↑</span> 점프 | <span class="key">Enter</span> 슛 | <span class="key">K</span> 밀쳐내기/스틸</div>
    </div>

    <div id="game-over">
        <h1 id="winner-text" style="font-size: 60px; margin: 0; text-shadow: 0 0 20px #ff9800;">PLAYER 1 WIN!</h1>
        <p style="font-size: 30px; margin-top: 10px;">최종 점수 <span id="final-p1" class="p1-color">0</span> : <span id="final-p2" class="p2-color">0</span></p>
        <button id="restart-btn" onclick="resetGame()">한 판 더!!</button>
    </div>

    <script>
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let audioCtx;

        function initAudio() {
            if (!audioCtx) audioCtx = new AudioCtx();
            if (audioCtx.state === 'suspended') audioCtx.resume();
        }

        function playSound(type) {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            
            if (type === 'hit') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sawtooth'; osc.frequency.setValueAtTime(180, now);
                osc.frequency.exponentialRampToValueAtTime(40, now + 0.15);
                gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.15);
            } else if (type === 'fire') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'square'; osc.frequency.setValueAtTime(400, now);
                osc.frequency.exponentialRampToValueAtTime(800, now + 0.2);
                gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.2);
            } else if (type === 'goal') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(523, now);
                osc.frequency.setValueAtTime(659, now + 0.08); osc.frequency.setValueAtTime(783, now + 0.16);
                osc.frequency.setValueAtTime(1046, now + 0.24);
                gain.gain.setValueAtTime(0.4, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.4);
            } else if (type === 'bounce') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(200, now);
                osc.frequency.exponentialRampToValueAtTime(50, now + 0.08);
                gain.gain.setValueAtTime(0.15, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.08);
            }
        }

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        const GAME_TIME = 45;
        let p1Score = 0, p2Score = 0, timeLeft = GAME_TIME;
        let gameActive = true, timerInterval;
        let screenShake = 0;
        let particles = [];
        let floatingTexts = [];
        let items = [];

        const keys = {};

        const hoops = [
            { x: 70, y: 180, rimX: 110, rimY: 220, side: 'left' },
            { x: 890, y: 180, rimX: 850, rimY: 220, side: 'right' }
        ];

        const p1 = {
            x: 200, y: 340, width: 44, height: 75, headRadius: 22, color: '#ff3d00',
            vx: 0, vy: 0, isGrounded: false, hasBall: false, id: 1, facing: 1,
            gauge: 0, gaugeDir: 1, isCharging: false, streak: 0, isFire: false,
            stunTimer: 0, itemType: null, itemTimer: 0
        };

        const p2 = {
            x: 710, y: 340, width: 44, height: 75, headRadius: 22, color: '#00e5ff',
            vx: 0, vy: 0, isGrounded: false, hasBall: false, id: 2, facing: -1,
            gauge: 0, gaugeDir: 1, isCharging: false, streak: 0, isFire: false,
            stunTimer: 0, itemType: null, itemTimer: 0
        };

        const ball = {
            x: 480, y: 200, radius: 13, vx: 0, vy: 0, holder: null, rotation: 0, trail: [], isFireBall: false
        };

        const gravity = 0.5;
        const groundY = 430;

        function addText(text, x, y, color = '#ffea00', scale = 1) {
            floatingTexts.push({ text, x, y, color, scale, alpha: 1.0 });
        }

        function addParticles(x, y, color, count = 12) {
            for (let i = 0; i < count; i++) {
                particles.push({
                    x, y, vx: (Math.random() - 0.5) * 10, vy: (Math.random() - 0.5) * 10,
                    radius: Math.random() * 4 + 2, color, life: 1.0
                });
            }
        }

        function spawnItem() {
            if (items.length > 0 || Math.random() > 0.4) return;
            const types = ['SPEED', 'JUMP', 'MAGNET', 'BOMB'];
            const type = types[Math.floor(Math.random() * types.length)];
            items.push({ x: 200 + Math.random() * 560, y: 100, type, radius: 16, vy: 1 });
        }

        function init() {
            window.addEventListener('keydown', e => {
                initAudio();
                if (e.repeat) return;
                keys[e.code] = true;

                if (e.code === 'Space' && p1.hasBall && p1.stunTimer <= 0) {
                    p1.isCharging = true; p1.gauge = 0; p1.gaugeDir = 1;
                }
                if (e.code === 'KeyE' && p1.stunTimer <= 0) attack(p1, p2);

                if (e.code === 'Enter' && p2.hasBall && p2.stunTimer <= 0) {
                    p2.isCharging = true; p2.gauge = 0; p2.gaugeDir = 1;
                }
                if (e.code === 'KeyK' && p2.stunTimer <= 0) attack(p2, p1);
            });

            window.addEventListener('keyup', e => {
                keys[e.code] = false;
                if (e.code === 'Space' && p1.hasBall && p1.isCharging) shootBall(p1);
                if (e.code === 'Enter' && p2.hasBall && p2.isCharging) shootBall(p2);
            });

            startTimer();
            setInterval(spawnItem, 8000);
            requestAnimationFrame(gameLoop);
        }

        function attack(attacker, victim) {
            const dist = Math.hypot((attacker.x + attacker.width/2) - (victim.x + victim.width/2), attacker.y - victim.y);
            attacker.vx = attacker.facing * 8;

            if (dist < 60) {
                playSound('hit'); screenShake = 8;
                victim.stunTimer = 25; victim.vx = attacker.facing * 10; victim.vy = -5;
                addParticles(victim.x + 20, victim.y + 20, '#ff1744', 15);
                addText("STEAL!!", victim.x, victim.y - 20, '#ff1744', 1.3);

                if (victim.hasBall) {
                    victim.hasBall = false; ball.holder = attacker; attacker.hasBall = true;
                }
            }
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
            p1Score = 0; p2Score = 0; timeLeft = GAME_TIME; gameActive = true;
            document.getElementById('p1-score').innerText = 0;
            document.getElementById('p2-score').innerText = 0;
            document.getElementById('game-over').style.display = 'none';
            resetRoundPositions(); startTimer();
        }

        function resetRoundPositions() {
            p1.x = 200; p1.y = 340; p1.vx = 0; p1.vy = 0; p1.hasBall = false; p1.stunTimer = 0; p1.isCharging = false;
            p2.x = 710; p2.y = 340; p2.vx = 0; p2.vy = 0; p2.hasBall = false; p2.stunTimer = 0; p2.isCharging = false;
            ball.x = 480; ball.y = 200; ball.vx = 0; ball.vy = 0; ball.holder = null; ball.trail = []; ball.isFireBall = false;
        }

        function shootBall(player) {
            const targetHoop = player.id === 1 ? hoops[1] : hoops[0];
            const dx = targetHoop.rimX - (player.x + player.width / 2);
            const dist = Math.abs(dx);

            player.hasBall = false; player.isCharging = false; ball.holder = null;
            ball.x = player.x + player.width / 2 + player.facing * 15;
            ball.y = player.y - 15;

            // 온파이어 상태면 적중률 대폭 상승
            let minVal = player.isFire ? 30 : 50;
            let maxVal = player.isFire ? 95 : 82;
            const isPerfect = player.gauge >= minVal && player.gauge <= maxVal;

            if (isPerfect || player.isFire) {
                ball.vx = (dx / dist) * (7.0 + dist * 0.006);
                ball.vy = player.isFire ? -14.5 : -13.0;
                ball.isFireBall = player.isFire;
                playSound('fire'); screenShake = player.isFire ? 10 : 4;
                addText(player.isFire ? "🔥 FIRE SHOOT!!" : "PERFECT!!", player.x, player.y - 40, '#ffea00', 1.4);
            } else {
                let err = (player.gauge - 65) * 0.08;
                ball.vx = (dx / dist) * (6.5 + dist * 0.006) + err;
                ball.vy = -12.0; playSound('bounce');
                addText("BAD!", player.x, player.y - 30, '#aaa', 1.0);
            }
        }

        function updatePlayer(p, leftKey, rightKey, jumpKey) {
            if (p.stunTimer > 0) { p.stunTimer--; p.vx *= 0.8; }
            else {
                let speed = 5.5 + (p.itemType === 'SPEED' ? 3 : 0) + (p.isFire ? 2 : 0);
                if (keys[leftKey]) { p.vx = -speed; p.facing = -1; }
                else if (keys[rightKey]) { p.vx = speed; p.facing = 1; }
                else { p.vx *= 0.7; }

                let jumpPower = -12.5 - (p.itemType === 'JUMP' ? 3.5 : 0) - (p.isFire ? 2 : 0);
                if (keys[jumpKey] && p.isGrounded) {
                    p.vy = jumpPower; p.isGrounded = false; playSound('bounce');
                }
            }

            p.vy += gravity; p.x += p.vx; p.y += p.vy;

            if (p.x < 10) p.x = 10;
            if (p.x + p.width > canvas.width - 10) p.x = canvas.width - 10 - p.width;

            if (p.y + p.height >= groundY) {
                p.y = groundY - p.height; p.vy = 0; p.isGrounded = true;
            }

            if (p.isCharging && p.hasBall) {
                p.gauge += p.gaugeDir * 4.0;
                if (p.gauge >= 100) { p.gauge = 100; p.gaugeDir = -1; }
                if (p.gauge <= 0) { p.gauge = 0; p.gaugeDir = 1; }
            }

            // 아이템 수거 판정
            items.forEach((item, idx) => {
                if (Math.hypot((p.x + p.width/2) - item.x, p.y - item.y) < 35) {
                    p.itemType = item.type; p.itemTimer = 300;
                    playSound('fire'); addText(`GET: ${item.type}!`, p.x, p.y - 30, '#00e5ff', 1.2);
                    if (item.type === 'BOMB') {
                        p.stunTimer = 40; screenShake = 10; playSound('hit');
                        addParticles(p.x, p.y, '#ff1744', 20);
                    }
                    items.splice(idx, 1);
                }
            });

            // 자석 아이템 발동
            if (p.itemType === 'MAGNET' && !ball.holder && Math.hypot((p.x + p.width/2) - ball.x, p.y - ball.y) < 220) {
                ball.vx += ((p.x + p.width/2) - ball.x) * 0.08;
                ball.vy += (p.y - ball.y) * 0.08;
            }

            if (!ball.holder && p.stunTimer <= 0) {
                if (Math.hypot((p.x + p.width/2) - ball.x, (p.y + p.height/2) - ball.y) < 42) {
                    ball.holder = p; p.hasBall = true;
                }
            } else if (ball.holder === p) {
                ball.x = p.x + p.width / 2 + p.facing * 18;
                ball.y = p.y + 10; ball.vx = 0; ball.vy = 0;
            }
        }

        function updateBall() {
            if (ball.holder) { ball.trail = []; return; }

            ball.vy += gravity; ball.x += ball.vx; ball.y += ball.vy;
            ball.rotation += ball.vx * 0.08;

            ball.trail.push({ x: ball.x, y: ball.y });
            if (ball.trail.length > (ball.isFireBall ? 10 : 5)) ball.trail.shift();

            if (ball.y + ball.radius >= groundY) {
                ball.y = groundY - ball.radius; ball.vy *= -0.7; ball.vx *= 0.8;
                if (Math.abs(ball.vy) > 2) playSound('bounce');
            }

            if (ball.x - ball.radius <= 0 || ball.x + ball.radius >= canvas.width) ball.vx *= -0.7;

            // 골대/백보드 판정 (찰지게 튕기기)
            hoops.forEach(hoop => {
                const distToRim = Math.hypot(ball.x - hoop.rimX, ball.y - hoop.rimY);

                // 림에 맞고 튕길 때 쫄깃한 소리
                if (distToRim < 22 && distToRim > 12) {
                    ball.vx *= -0.8; ball.vy *= -0.5; playSound('bounce'); screenShake = 3;
                }

                // 득점!
                if (distToRim <= 12 && ball.vy > 0) {
                    playSound('goal'); screenShake = 12;
                    addParticles(hoop.rimX, hoop.rimY, '#ffea00', 25);

                    let scorer = hoop.side === 'right' ? p1 : p2;
                    let opponent = hoop.side === 'right' ? p2 : p1;

                    scorer.streak++; opponent.streak = 0;
                    if (scorer.streak >= 2) { scorer.isFire = true; playSound('fire'); }
                    opponent.isFire = false;

                    if (hoop.side === 'right') { p1Score += (ball.isFireBall ? 3 : 2); document.getElementById('p1-score').innerText = p1Score; } 
                    else { p2Score += (ball.isFireBall ? 3 : 2); document.getElementById('p2-score').innerText = p2Score; }

                    document.getElementById('p1-combo').innerText = p1.isFire ? "🔥ON FIRE!" : "";
                    document.getElementById('p2-combo').innerText = p2.isFire ? "🔥ON FIRE!" : "";

                    addText(ball.isFireBall ? "3PTS 🔥 GOAL!!" : "2PTS GOAL!!", hoop.rimX, hoop.rimY - 40, '#ffea00', 1.6);
                    resetRoundPositions();
                }
            });
        }

        function endGame() {
            gameActive = false; clearInterval(timerInterval); playSound('goal');
            const winnerText = document.getElementById('winner-text');
            if (p1Score > p2Score) { winnerText.innerText = "PLAYER 1 WIN!"; winnerText.style.color = "#ff3d00"; } 
            else if (p2Score > p1Score) { winnerText.innerText = "PLAYER 2 WIN!"; winnerText.style.color = "#00e5ff"; } 
            else { winnerText.innerText = "DRAW GAME!"; winnerText.style.color = "#ffea00"; }

            document.getElementById('final-p1').innerText = p1Score;
            document.getElementById('final-p2').innerText = p2Score;
            document.getElementById('game-over').style.display = 'flex';
        }

        function drawCourt() {
            ctx.fillStyle = '#1e1f2f'; ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = '#ff9800'; ctx.fillRect(0, groundY, canvas.width, 5);

            // 하프코트 및 3점슛 라인
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.arc(70, groundY, 210, -Math.PI/2, 0); ctx.stroke();
            ctx.beginPath(); ctx.arc(890, groundY, 210, -Math.PI, -Math.PI/2); ctx.stroke();
            ctx.moveTo(480, groundY); ctx.lineTo(480, canvas.height); ctx.stroke();

            // 백보드 & 림
            hoops.forEach(h => {
                ctx.fillStyle = '#fff'; ctx.fillRect(h.side === 'left' ? h.x - 12 : h.x, h.y, 12, 90);
                ctx.strokeStyle = '#ff3d00'; ctx.lineWidth = 6;
                ctx.beginPath(); ctx.arc(h.rimX, h.rimY, 16, 0, Math.PI); ctx.stroke();
            });
        }

        function drawPlayer(p) {
            ctx.save();
            ctx.translate(p.x + p.width / 2, p.y);

            if (p.stunTimer > 0) ctx.rotate((Math.random() - 0.5) * 0.3); // 기절 애니메이션

            // 그림자
            ctx.fillStyle = 'rgba(0,0,0,0.4)';
            ctx.beginPath(); ctx.ellipse(0, p.height, 20, 6, 0, 0, Math.PI * 2); ctx.fill();

            // 몸통
            ctx.fillStyle = p.color;
            ctx.fillRect(-14, 26, 28, 26);

            // 대두 머리 (중독성 비주얼 키포인트)
            ctx.fillStyle = '#ffcc80';
            ctx.beginPath(); ctx.arc(0, 10, p.headRadius, 0, Math.PI * 2); ctx.fill();

            // 헤어 / 모자
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.headRadius, -8, p.headRadius * 2, 12);

            // 눈 (익살스러운 표현)
            ctx.fillStyle = '#000';
            if (p.stunTimer > 0) {
                ctx.font = 'bold 12px Arial'; ctx.fillText('X X', p.facing * 4 - 8, 14);
            } else {
                ctx.fillRect(p.facing * 6, 8, 5, 5);
            }

            // 불꽃 효과 (ON FIRE)
            if (p.isFire) {
                ctx.fillStyle = '#ffea00';
                ctx.beginPath(); ctx.arc(0, -10, 16 + Math.random()*6, 0, Math.PI*2); ctx.fill();
            }

            ctx.restore();

            // 슈팅 게이지
            if (p.hasBall && p.isCharging) {
                const gx = p.x + p.width / 2 - 35; const gy = p.y - 35;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'; ctx.fillRect(gx, gy, 70, 8);
                ctx.fillStyle = '#ff1744'; ctx.fillRect(gx, gy, 70, 8);
                ctx.fillStyle = '#00e676'; ctx.fillRect(gx + 35, gy, 20, 8); // Perfect Zone

                const barX = gx + (p.gauge / 100) * 70;
                ctx.fillStyle = '#ffffff'; ctx.fillRect(barX - 2, gy - 2, 4, 12);
            }
        }

        function drawBall() {
            for (let i = 0; i < ball.trail.length; i++) {
                const t = ball.trail[i];
                ctx.fillStyle = ball.isFireBall ? `rgba(255, 234, 0, ${ (i + 1) / 10 })` : `rgba(255, 152, 0, ${ (i + 1) / 6 })`;
                ctx.beginPath(); ctx.arc(t.x, t.y, ball.radius * ((i + 1) / 8), 0, Math.PI * 2); ctx.fill();
            }

            ctx.save();
            ctx.translate(ball.x, ball.y);
            ctx.rotate(ball.rotation);

            ctx.fillStyle = ball.isFireBall ? '#ffea00' : '#ff9800';
            ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI * 2); ctx.fill();

            ctx.strokeStyle = '#000'; ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI * 2);
            ctx.moveTo(-ball.radius, 0); ctx.lineTo(ball.radius, 0); ctx.stroke();

            ctx.restore();
        }

        function drawItems() {
            items.forEach(item => {
                ctx.fillStyle = item.type === 'BOMB' ? '#ff1744' : '#00e5ff';
                ctx.beginPath(); ctx.arc(item.x, item.y, item.radius, 0, Math.PI*2); ctx.fill();
                ctx.fillStyle = '#000'; ctx.font = 'bold 10px Arial'; ctx.textAlign = 'center';
                ctx.fillText(item.type[0], item.x, item.y + 3);
                item.y += item.vy;
                if (item.y + item.radius >= groundY) item.y = groundY - item.radius;
            });
        }

        function drawUIEffects() {
            for (let i = floatingTexts.length - 1; i >= 0; i--) {
                const ft = floatingTexts[i];
                ctx.save(); ctx.globalAlpha = ft.alpha;
                ctx.fillStyle = ft.color; ctx.font = `bold ${20 * ft.scale}px Impact`;
                ctx.textAlign = 'center'; ctx.fillText(ft.text, ft.x, ft.y);
                ctx.restore();
                ft.y -= 0.8; ft.alpha -= 0.02;
                if (ft.alpha <= 0) floatingTexts.splice(i, 1);
            }

            for (let i = particles.length - 1; i >= 0; i--) {
                const pt = particles[i]; pt.x += pt.vx; pt.y += pt.vy; pt.life -= 0.03;
                if (pt.life <= 0) { particles.splice(i, 1); continue; }
                ctx.save(); ctx.globalAlpha = pt.life; ctx.fillStyle = pt.color;
                ctx.beginPath(); ctx.arc(pt.x, pt.y, pt.radius, 0, Math.PI*2); ctx.fill(); ctx.restore();
            }
        }

        function draw() {
            ctx.save();
            if (screenShake > 0) {
                ctx.translate((Math.random() - 0.5) * screenShake, (Math.random() - 0.5) * screenShake);
                screenShake *= 0.9;
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawCourt();
            drawItems();
            drawPlayer(p1);
            drawPlayer(p2);
            drawBall();
            drawUIEffects();

            ctx.restore();
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
