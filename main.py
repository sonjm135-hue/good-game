import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="NBA Superstars 2P - Enhanced Hoop", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #0d0e15; font-family: 'Impact', 'Arial Black', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }
        canvas { background: #141520; border-bottom: 10px solid #c5a059; box-shadow: 0 0 35px rgba(197, 160, 89, 0.3); }
        
        #ui {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 35px; color: #fff; font-size: 24px; font-weight: bold; align-items: center;
            background: rgba(11, 12, 16, 0.92); padding: 12px 35px; border-radius: 20px; z-index: 10; border: 2px solid #c5a059;
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
        }
        .p1-color { color: #ffc72c; text-shadow: 0 0 10px #1d428a; }
        .p2-color { color: #fdb927; text-shadow: 0 0 10px #552583; }
        .q-badge { background: #ff3d00; color: #fff; padding: 4px 12px; border-radius: 8px; font-size: 18px; letter-spacing: 1px; }
        .fire-text { color: #ffea00; animation: blink 0.3s infinite alternate; font-size: 18px; }

        @keyframes blink { from { opacity: 1; } to { opacity: 0.5; } }

        #game-over {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.92); display: none; flex-direction: column;
            justify-content: center; align-items: center; color: #fff; z-index: 30;
        }
        .overlay-title { font-size: 55px; margin: 0; text-shadow: 0 0 20px #c5a059; text-align: center; }
        .overlay-sub { font-size: 26px; margin-top: 15px; }

        #restart-btn {
            margin-top: 30px; padding: 15px 45px; font-size: 26px; font-weight: bold;
            color: #000; background: #c5a059; border: none; border-radius: 12px; cursor: pointer;
            box-shadow: 0 0 20px #c5a059; transition: 0.15s;
        }
        #restart-btn:hover { transform: scale(1.1); background: #ffea00; }

        #controls-guide {
            position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 35px; color: #fff; font-size: 13px; font-family: sans-serif;
            background: rgba(0,0,0,0.85); padding: 8px 25px; border-radius: 10px; border: 1px solid #444;
        }
        .key { background: #333; padding: 2px 6px; border-radius: 4px; border: 1px solid #666; color: #ffea00; }
    </style>
</head>
<body>
    <div id="ui">
        <div>30. CURRY <span id="p1-combo" class="fire-text"></span>: <span id="p1-score" class="p1-color">0</span></div>
        <div style="display:flex; flex-direction:column; align-items:center;">
            <span id="q-text" class="q-badge">1st QTR</span>
            <span style="color: #ffea00; margin-top: 2px;"><span id="timer">60</span>s</span>
        </div>
        <div>23. LEBRON <span id="p2-combo" class="fire-text"></span>: <span id="p2-score" class="p2-color">0</span></div>
    </div>

    <div id="canvas-container">
        <canvas id="gameCanvas" width="960" height="520"></canvas>
    </div>

    <div id="controls-guide">
        <div><b class="p1-color">CURRY (GSW)</b>: <span class="key">A</span><span class="key">D</span> 이동 | <span class="key">W</span> 점프 | <span class="key">Space</span> 점프슛 | <span class="key">E</span> 스틸</div>
        <div><b class="p2-color">LEBRON (LAL)</b>: <span class="key">←</span><span class="key">→</span> 이동 | <span class="key">↑</span> 점프 | <span class="key">Enter</span> 점프슛 | <span class="key">K</span> 스틸</div>
        <div style="color: #00e676;">💡 <span class="key">ESC</span> 전체화면</div>
    </div>

    <div id="game-over">
        <h1 id="winner-text" class="overlay-title">STEPH CURRY WINS!</h1>
        <p id="final-score" class="overlay-sub">최종 점수 <span id="final-p1" class="p1-color">0</span> : <span id="final-p2" class="p2-color">0</span></p>
        <button id="restart-btn" onclick="onBtnClick()">다음 쿼터 / 새 경기</button>
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
                osc.type = 'sawtooth'; osc.frequency.setValueAtTime(220, now);
                osc.frequency.exponentialRampToValueAtTime(50, now + 0.12);
                gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.12);
            } else if (type === 'fire') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'square'; osc.frequency.setValueAtTime(450, now);
                osc.frequency.exponentialRampToValueAtTime(900, now + 0.18);
                gain.gain.setValueAtTime(0.25, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.18);
            } else if (type === 'goal') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(523, now);
                osc.frequency.setValueAtTime(659, now + 0.08); osc.frequency.setValueAtTime(783, now + 0.16);
                osc.frequency.setValueAtTime(1046, now + 0.24);
                gain.gain.setValueAtTime(0.35, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.4);
            } else if (type === 'bounce') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(180, now);
                osc.frequency.exponentialRampToValueAtTime(40, now + 0.08);
                gain.gain.setValueAtTime(0.15, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.08);
            }
        }

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        const QTR_TIME = 60;
        let currentQuarter = 1;
        let p1Score = 0, p2Score = 0, timeLeft = QTR_TIME;
        let gameActive = true, timerInterval;
        let screenShake = 0;
        let particles = [];
        let floatingTexts = [];

        const keys = {};

        const hoops = [
            { x: 50, y: 140, rimX: 95, rimY: 220, side: 'left', netAnim: 0 },
            { x: 910, y: 140, rimX: 865, rimY: 220, side: 'right', netAnim: 0 }
        ];

        const p1 = {
            id: 1, name: "CURRY", number: "30", skinColor: '#e0ac69', hairColor: '#3a2312',
            primaryColor: '#1d428a', secondaryColor: '#ffc72c', headbandColor: '#ffc72c',
            x: 200, y: 340, width: 44, height: 80, headRadius: 26,
            vx: 0, vy: 0, isGrounded: false, hasBall: false, facing: 1,
            gauge: 0, gaugeDir: 1, isCharging: false, streak: 0, isFire: false,
            stunTimer: 0, walkCycle: 0, stealAnim: 0, shootAnim: 0
        };

        const p2 = {
            id: 2, name: "LEBRON", number: "23", skinColor: '#8d5524', hairColor: '#1a0d00',
            primaryColor: '#552583', secondaryColor: '#fdb927', headbandColor: '#552583',
            x: 710, y: 340, width: 44, height: 80, headRadius: 26,
            vx: 0, vy: 0, isGrounded: false, hasBall: false, facing: -1,
            gauge: 0, gaugeDir: 1, isCharging: false, streak: 0, isFire: false,
            stunTimer: 0, walkCycle: 0, stealAnim: 0, shootAnim: 0
        };

        const ball = {
            x: 480, y: 200, radius: 13, vx: 0, vy: 0, holder: null, rotation: 0, trail: [], isFireBall: false, isPerfectShot: false
        };

        const gravity = 0.5;
        const groundY = 430;

        // 전체 화면 토글 함수
        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch((err) => {
                    console.log(`전체화면 전환 실패: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

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

        function init() {
            window.addEventListener('keydown', e => {
                initAudio();

                // ESC 키 누르면 전체화면 토글
                if (e.code === 'Escape') {
                    toggleFullscreen();
                }

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
            requestAnimationFrame(gameLoop);
        }

        function attack(attacker, victim) {
            attacker.stealAnim = 15;
            const dist = Math.hypot((attacker.x + attacker.width/2) - (victim.x + victim.width/2), attacker.y - victim.y);
            attacker.vx = attacker.facing * 9;

            if (dist < 65) {
                playSound('hit'); screenShake = 8;
                victim.stunTimer = 25; victim.vx = attacker.facing * 11; victim.vy = -4;
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
                if (timeLeft <= 0) quarterEnded();
            }, 1000);
        }

        function quarterEnded() {
            clearInterval(timerInterval);
            if (currentQuarter < 3) {
                gameActive = false;
                const modal = document.getElementById('game-over');
                const title = document.getElementById('winner-text');
                const btn = document.getElementById('restart-btn');
                
                title.innerText = `${currentQuarter}쿼터 종료!`;
                title.style.color = "#ffea00";
                btn.innerText = `${currentQuarter + 1}쿼터 시작!`;
                modal.style.display = 'flex';
            } else {
                endGame();
            }
        }

        function onBtnClick() {
            const modal = document.getElementById('game-over');
            modal.style.display = 'none';

            if (currentQuarter >= 3 && !gameActive) {
                currentQuarter = 1; p1Score = 0; p2Score = 0;
                document.getElementById('p1-score').innerText = 0;
                document.getElementById('p2-score').innerText = 0;
            } else {
                currentQuarter++;
            }

            const qNames = ["1st QTR", "2nd QTR", "3rd QTR"];
            document.getElementById('q-text').innerText = qNames[currentQuarter - 1];

            timeLeft = QTR_TIME;
            document.getElementById('timer').innerText = timeLeft;
            gameActive = true;
            resetRoundPositions();
            startTimer();
        }

        function resetRoundPositions() {
            p1.x = 200; p1.y = 340; p1.vx = 0; p1.vy = 0; p1.hasBall = false; p1.stunTimer = 0; p1.isCharging = false;
            p2.x = 710; p2.y = 340; p2.vx = 0; p2.vy = 0; p2.hasBall = false; p2.stunTimer = 0; p2.isCharging = false;
            ball.x = 480; ball.y = 200; ball.vx = 0; ball.vy = 0; ball.holder = null; ball.trail = []; ball.isFireBall = false; ball.isPerfectShot = false;
        }

        function shootBall(player) {
            player.shootAnim = 20;
            const targetHoop = player.id === 1 ? hoops[1] : hoops[0];
            const dx = targetHoop.rimX - (player.x + player.width / 2);
            const dist = Math.abs(dx);

            player.hasBall = false; player.isCharging = false; ball.holder = null;
            ball.x = player.x + player.width / 2 + player.facing * 15;
            ball.y = player.y - 30;

            // ON FIRE 상태여도 반드시 초록색 영역(45 ~ 75%) 타이밍을 맞춰야만 골 적용!
            const isGreenZone = player.gauge >= 45 && player.gauge <= 75;

            if (isGreenZone) {
                ball.isPerfectShot = true;
                ball.isFireBall = player.isFire;

                const timeToRim = 32;
                ball.vx = dx / timeToRim;
                ball.vy = (targetHoop.rimY - 15 - ball.y - 0.5 * gravity * Math.pow(timeToRim, 2)) / timeToRim;

                playSound('fire'); screenShake = player.isFire ? 10 : 5;
                addText(player.isFire ? "🔥 ON FIRE 3PTS!" : "🎯 PERFECT SWISH!!", player.x, player.y - 40, '#00e676', 1.5);
            } else {
                ball.isPerfectShot = false;
                let err = (player.gauge - 60) * 0.12;
                ball.vx = (dx / dist) * (6.5 + dist * 0.005) + err;
                ball.vy = -12.0; playSound('bounce');
                addText("MISS!", player.x, player.y - 30, '#aaa', 1.0);
            }
        }

        function updatePlayer(p, leftKey, rightKey, jumpKey) {
            if (p.stealAnim > 0) p.stealAnim--;
            if (p.shootAnim > 0) p.shootAnim--;

            if (p.stunTimer > 0) { p.stunTimer--; p.vx *= 0.8; }
            else {
                let speed = 5.8 + (p.isFire ? 2 : 0);
                if (keys[leftKey]) { p.vx = -speed; p.facing = -1; p.walkCycle += 0.28; }
                else if (keys[rightKey]) { p.vx = speed; p.facing = 1; p.walkCycle += 0.28; }
                else { p.vx *= 0.7; p.walkCycle = 0; }

                if (keys[jumpKey] && p.isGrounded) {
                    p.vy = -12.8 - (p.isFire ? 2 : 0); p.isGrounded = false; playSound('bounce');
                }
            }

            p.vy += gravity; p.x += p.vx; p.y += p.vy;

            if (p.x < 10) p.x = 10;
            if (p.x + p.width > canvas.width - 10) p.x = canvas.width - 10 - p.width;

            if (p.y + p.height >= groundY) {
                p.y = groundY - p.height; p.vy = 0; p.isGrounded = true;
            }

            if (p.isCharging && p.hasBall) {
                p.gauge += p.gaugeDir * 4.8;
                if (p.gauge >= 100) { p.gauge = 100; p.gaugeDir = -1; }
                if (p.gauge <= 0) { p.gauge = 0; p.gaugeDir = 1; }
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

            hoops.forEach(hoop => {
                if (hoop.netAnim > 0) hoop.netAnim--;

                const distToRim = Math.hypot(ball.x - hoop.rimX, ball.y - hoop.rimY);

                if (!ball.isPerfectShot && distToRim < 22 && distToRim > 12) {
                    ball.vx *= -0.8; ball.vy *= -0.5; playSound('bounce'); screenShake = 3;
                }

                if (distToRim <= 15 && ball.vy > 0) {
                    hoop.netAnim = 18;
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

                    addText(ball.isFireBall ? "3PTS 🔥 SWISH!!" : "2PTS SWISH!!", hoop.rimX, hoop.rimY - 40, '#ffea00', 1.6);
                    resetRoundPositions();
                }
            });
        }

        function endGame() {
            gameActive = false; clearInterval(timerInterval); playSound('goal');
            const modal = document.getElementById('game-over');
            const winnerText = document.getElementById('winner-text');
            const btn = document.getElementById('restart-btn');

            if (p1Score > p2Score) { winnerText.innerText = "STEPH CURRY WINS!"; winnerText.style.color = "#ffc72c"; } 
            else if (p2Score > p1Score) { winnerText.innerText = "LEBRON JAMES WINS!"; winnerText.style.color = "#fdb927"; } 
            else { winnerText.innerText = "DRAW GAME!"; winnerText.style.color = "#ffffff"; }

            document.getElementById('final-p1').innerText = p1Score;
            document.getElementById('final-p2').innerText = p2Score;
            btn.innerText = "새 경기 시작!";
            modal.style.display = 'flex';
        }

        function drawCourt() {
            ctx.fillStyle = '#221508'; ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = '#c5a059'; ctx.fillRect(0, groundY, canvas.width, 6);

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.arc(70, groundY, 210, -Math.PI/2, 0); ctx.stroke();
            ctx.beginPath(); ctx.arc(890, groundY, 210, -Math.PI, -Math.PI/2); ctx.stroke();
            ctx.moveTo(480, groundY); ctx.lineTo(480, canvas.height); ctx.stroke();

            hoops.forEach(h => {
                const isLeft = h.side === 'left';
                const poleX = isLeft ? 15 : 945;
                const boardX = isLeft ? 50 : 910;
                
                ctx.fillStyle = isLeft ? '#1d428a' : '#552583';
                ctx.beginPath();
                ctx.moveTo(poleX, groundY);
                ctx.lineTo(poleX + (isLeft ? 15 : -15), groundY);
                ctx.lineTo(boardX + (isLeft ? -10 : 10), h.y + 40);
                ctx.lineTo(boardX + (isLeft ? -25 : 25), h.y + 40);
                ctx.fill();

                ctx.fillStyle = '#111';
                ctx.fillRect(isLeft ? 0 : 930, groundY - 70, 30, 70);
                ctx.fillStyle = isLeft ? '#ffc72c' : '#fdb927';
                ctx.fillRect(isLeft ? 5 : 935, groundY - 60, 20, 50);

                ctx.strokeStyle = '#666'; ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(poleX, h.y + 20); ctx.lineTo(boardX, h.y + 20);
                ctx.moveTo(poleX, h.y + 70); ctx.lineTo(boardX, h.y + 70);
                ctx.stroke();

                ctx.fillStyle = 'rgba(255, 255, 255, 0.18)';
                ctx.fillRect(boardX - (isLeft ? 0 : 8), h.y, 8, 100);
                
                ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3;
                ctx.strokeRect(boardX - (isLeft ? 0 : 8), h.y, 8, 100);

                ctx.strokeStyle = '#e63946'; ctx.lineWidth = 3;
                ctx.strokeRect(boardX + (isLeft ? 2 : -18), h.y + 55, 16, 28);

                ctx.fillStyle = '#ff3d00';
                ctx.fillRect(boardX + (isLeft ? 8 : -20), h.y + 78, 12, 6);

                ctx.strokeStyle = '#ff3d00'; ctx.lineWidth = 5; ctx.lineCap = 'round';
                ctx.beginPath();
                const rimStartX = boardX + (isLeft ? 20 : -20);
                const rimEndX = h.rimX + (isLeft ? 16 : -16);
                ctx.moveTo(rimStartX, h.rimY);
                ctx.lineTo(rimEndX, h.rimY);
                ctx.stroke();

                const netSwing = h.netAnim > 0 ? Math.sin(h.netAnim) * 6 : 0;
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)'; ctx.lineWidth = 1.8;
                
                const netTopLeft = h.rimX - 16;
                const netTopRight = h.rimX + 16;
                const netBotLeft = h.rimX - 9 + netSwing;
                const netBotRight = h.rimX + 9 + netSwing;
                const netBottomY = h.rimY + 32;

                ctx.beginPath();
                for(let i=0; i<=4; i++) {
                    let tx = netTopLeft + (i / 4) * 32;
                    let bx = netBotLeft + (i / 4) * 18;
                    ctx.moveTo(tx, h.rimY);
                    ctx.lineTo(bx, netBottomY);
                }
                ctx.moveTo(netTopLeft, h.rimY + 10); ctx.lineTo(netTopRight, h.rimY + 10);
                ctx.moveTo(netTopLeft + 3, h.rimY + 20); ctx.lineTo(netTopRight - 3, h.rimY + 20);
                ctx.stroke();
            });
        }

        function drawCustomNBAPlayer(p) {
            ctx.save();
            const centerX = p.x + p.width / 2;
            ctx.translate(centerX, p.y);

            if (p.stunTimer > 0) ctx.rotate((Math.random() - 0.5) * 0.4);

            ctx.fillStyle = 'rgba(0,0,0,0.4)';
            ctx.beginPath(); ctx.ellipse(0, p.height, 22, 6, 0, 0, Math.PI * 2); ctx.fill();

            const legSwing = Math.sin(p.walkCycle) * 14;
            ctx.strokeStyle = p.skinColor; ctx.lineWidth = 8; ctx.lineCap = 'round';
            ctx.beginPath(); ctx.moveTo(-6, 50); ctx.lineTo(-6 + legSwing, p.height - 2); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(6, 50); ctx.lineTo(6 - legSwing, p.height - 2); ctx.stroke();

            ctx.fillStyle = p.secondaryColor;
            ctx.fillRect(-10 + legSwing, p.height - 4, 12, 6);
            ctx.fillRect(2 - legSwing, p.height - 4, 12, 6);

            ctx.fillStyle = p.primaryColor; ctx.fillRect(-14, 38, 28, 16);
            ctx.fillStyle = p.secondaryColor; ctx.fillRect(-14, 50, 28, 4);

            ctx.fillStyle = p.primaryColor; ctx.fillRect(-13, 14, 26, 26);
            ctx.fillStyle = p.secondaryColor; ctx.font = 'bold 12px Arial'; ctx.textAlign = 'center';
            ctx.fillText(p.number, 0, 32);

            ctx.strokeStyle = p.skinColor; ctx.lineWidth = 7;
            if (p.shootAnim > 0) {
                ctx.beginPath(); ctx.moveTo(-10, 18); ctx.lineTo(-14, -8); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(10, 18); ctx.lineTo(p.facing * 18, -12); ctx.stroke();
            } else if (p.stealAnim > 0) {
                ctx.beginPath(); ctx.moveTo(-10, 18); ctx.lineTo(p.facing * 30, 20); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(10, 18); ctx.lineTo(p.facing * 25, 28); ctx.stroke();
            } else {
                ctx.beginPath(); ctx.moveTo(-10, 18); ctx.lineTo(-10 - legSwing * 0.8, 32); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(10, 18); ctx.lineTo(10 + legSwing * 0.8, 32); ctx.stroke();
            }

            ctx.fillStyle = p.skinColor;
            ctx.beginPath(); ctx.arc(0, -2, p.headRadius, 0, Math.PI * 2); ctx.fill();

            if (p.id === 1) { // CURRY
                ctx.fillStyle = p.hairColor;
                ctx.beginPath(); ctx.arc(0, -10, p.headRadius, Math.PI, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#5c3a1e';
                ctx.fillRect(-8, 12, 16, 5); ctx.fillRect(-4, 8, 8, 4);
                ctx.fillStyle = p.headbandColor; ctx.fillRect(-p.headRadius, -10, p.headRadius * 2, 6);
            } else { // LEBRON
                ctx.fillStyle = p.hairColor;
                ctx.beginPath(); ctx.arc(0, -12, p.headRadius, Math.PI, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#1a0d00';
                ctx.beginPath(); ctx.arc(0, 10, 14, 0, Math.PI); ctx.fill();
                ctx.fillStyle = p.headbandColor; ctx.fillRect(-p.headRadius, -8, p.headRadius * 2, 7);
            }

            ctx.fillStyle = '#000';
            if (p.stunTimer > 0) {
                ctx.font = 'bold 12px Arial'; ctx.fillText('X X', p.facing * 4 - 8, 4);
            } else {
                ctx.fillRect(p.facing * 6, 0, 5, 5);
                ctx.fillRect(p.facing * 6 - 2, -4, 8, 2);
            }

            if (p.isFire) {
                ctx.strokeStyle = '#ffea00'; ctx.lineWidth = 4;
                ctx.beginPath(); ctx.arc(0, -2, p.headRadius + 5 + Math.random()*4, 0, Math.PI * 2); ctx.stroke();
            }

            ctx.restore();

            if (p.hasBall && p.isCharging) {
                const gx = p.x + p.width / 2 - 35; const gy = p.y - 45;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)'; ctx.fillRect(gx, gy, 70, 9);
                ctx.fillStyle = '#ff1744'; ctx.fillRect(gx, gy, 70, 9);
                ctx.fillStyle = '#00e676'; ctx.fillRect(gx + 31.5, gy, 21, 9);

                const barX = gx + (p.gauge / 100) * 70;
                ctx.fillStyle = '#ffffff'; ctx.fillRect(barX - 2, gy - 2, 4, 13);
            }
        }

        function drawBall() {
            for (let i = 0; i < ball.trail.length; i++) {
                const t = ball.trail[i];
                ctx.fillStyle = ball.isFireBall ? `rgba(255, 234, 0, ${ (i + 1) / 10 })` : `rgba(255, 152, 0, ${ (i + 1) / 6 })`;
                ctx.beginPath(); ctx.arc(t.x, t.y, ball.radius * ((i + 1) / 8), 0, Math.PI * 2); ctx.fill();
            }

            ctx.save(); ctx.translate(ball.x, ball.y); ctx.rotate(ball.rotation);
            ctx.fillStyle = ball.isFireBall ? '#ffea00' : '#ff8c00';
            ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = '#000'; ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI * 2);
            ctx.moveTo(-ball.radius, 0); ctx.lineTo(ball.radius, 0); ctx.stroke();
            ctx.restore();
        }

        function drawUIEffects() {
            for (let i = floatingTexts.length - 1; i >= 0; i--) {
                const ft = floatingTexts[i];
                ctx.save(); ctx.globalAlpha = ft.alpha;
                ctx.fillStyle = ft.color; ctx.font = `bold ${22 * ft.scale}px Impact`;
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
            drawCustomNBAPlayer(p1);
            drawCustomNBAPlayer(p2);
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

components.html(game_html, height=620)
