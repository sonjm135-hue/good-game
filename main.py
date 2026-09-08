import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="2P Basketball - Detailed & Skill Edition", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #121212; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }
        canvas { background: #1a1a24; border-bottom: 8px solid #333; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        #ui {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 30px; color: #fff; font-size: 20px; font-weight: bold;
            background: rgba(0,0,0,0.85); padding: 10px 30px; border-radius: 15px; z-index: 10; border: 1px solid #444;
        }
        .p1-color { color: #ff5252; }
        .p2-color { color: #448aff; }
        
        /* 캐릭터 및 스킬 선택 화면 */
        #select-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15,15,22,0.95); display: flex; flex-direction: column;
            justify-content: center; align-items: center; color: #fff; z-index: 30;
        }
        .select-container { display: flex; gap: 50px; margin-top: 20px; }
        .player-box {
            background: #252538; padding: 25px; border-radius: 15px; border: 2px solid #444;
            display: flex; flex-direction: column; align-items: center; width: 280px;
        }
        .skill-opt {
            width: 100%; padding: 10px; margin: 6px 0; background: #33334d; border: 2px solid transparent;
            color: #fff; border-radius: 8px; cursor: pointer; text-align: left; font-size: 14px; transition: 0.2s;
        }
        .skill-opt:hover { background: #444466; }
        .skill-opt.selected { border-color: #ffb74d; background: #555588; font-weight: bold; }
        #start-game-btn {
            margin-top: 30px; padding: 14px 40px; font-size: 24px; font-weight: bold;
            color: #111; background: #ffb74d; border: none; border-radius: 10px; cursor: pointer; transition: 0.2s;
        }
        #start-game-btn:hover { transform: scale(1.08); background: #ffa726; }

        #game-over, #quarter-notice {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); display: none; flex-direction: column;
            justify-content: center; align-items: center; color: #fff; z-index: 20;
        }
        #restart-btn {
            margin-top: 20px; padding: 12px 30px; font-size: 22px; font-weight: bold;
            color: #111; background-color: #ffb74d; border: none; border-radius: 8px; cursor: pointer;
        }
        #controls-guide {
            position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 30px; color: #ccc; font-size: 12px;
            background: rgba(0,0,0,0.85); padding: 8px 20px; border-radius: 10px; border: 1px solid #333;
        }
        .badge { padding: 2px 6px; background: #e65100; color: #fff; border-radius: 4px; font-size: 11px; }
    </style>
</head>
<body>
    <div id="ui">
        <div>1P: <span id="p1-score" class="p1-color">0</span></div>
        <div style="color: #4caf50;"><span id="quarter-text">1Q</span></div>
        <div>TIME: <span id="timer" style="color: #ffeb3b;">60</span>s</div>
        <div>2P: <span id="p2-score" class="p2-color">0</span></div>
    </div>

    <!-- 스킬 선택 화면 -->
    <div id="select-screen">
        <h1 style="font-size: 36px; margin-bottom: 5px; color: #ffb74d;">🏀 스킬 선택 & 경기 시작</h1>
        <p style="color: #aaa; margin-bottom: 20px;">원하는 스킬을 고르고 경기 시작 버튼을 누르세요!</p>
        
        <div class="select-container">
            <!-- 1P 선택 -->
            <div class="player-box" style="border-color: #ff5252;">
                <h2 class="p1-color" style="margin-top:0;">1P 스킬 선택</h2>
                <div class="skill-opt selected" onclick="selectSkill(1, 'sniper', this)">
                    🎯 <b>스나이퍼</b><br><small>3점슛 Perfect 구간 대폭 확대</small>
                </div>
                <div class="skill-opt" onclick="selectSkill(1, 'dash', this)">
                    ⚡ <b>음속 대쉬</b><br><small>순간 가속 및 스태미나 즉시 회복</small>
                </div>
                <div class="skill-opt" onclick="selectSkill(1, 'block', this)">
                    🛡️ <b>철벽 블락</b><br><small>고고도 수비 점프 & 강력한 슛 쳐내기</small>
                </div>
            </div>

            <!-- 2P 선택 -->
            <div class="player-box" style="border-color: #448aff;">
                <h2 class="p2-color" style="margin-top:0;">2P 스킬 선택</h2>
                <div class="skill-opt selected" onclick="selectSkill(2, 'sniper', this)">
                    🎯 <b>스나이퍼</b><br><small>3점슛 Perfect 구간 대폭 확대</small>
                </div>
                <div class="skill-opt" onclick="selectSkill(2, 'dash', this)">
                    ⚡ <b>음속 대쉬</b><br><small>순간 가속 및 스태미나 즉시 회복</small>
                </div>
                <div class="skill-opt" onclick="selectSkill(2, 'block', this)">
                    🛡️ <b>철벽 블락</b><br><small>고고도 수비 점프 & 강력한 슛 쳐내기</small>
                </div>
            </div>
        </div>

        <button id="start-game-btn" onclick="startGame()">경기 시작!</button>
    </div>

    <div id="canvas-container">
        <canvas id="gameCanvas" width="900" height="500"></canvas>
    </div>

    <div id="controls-guide">
        <div><b class="p1-color">1P</b>: A/D(이동) | W(점프) | L-Shift(대쉬) | Space(슛) | <span class="badge">E</span> 스킬</div>
        <div><b class="p2-color">2P</b>: ←/→(이동) | ↑(점프) | R-Shift(대쉬) | Enter(슛) | <span class="badge">K</span> 스킬</div>
    </div>

    <div id="quarter-notice">
        <h1 id="quarter-notice-title" style="font-size: 40px; color: #ffb74d; margin: 0;">1Q END</h1>
        <p style="font-size: 20px; color: #ccc;">잠시 후 다음 쿼터가 시작됩니다...</p>
    </div>

    <div id="game-over">
        <h1 id="winner-text" style="font-size: 48px; margin-bottom: 10px;">PLAYER 1 WIN!</h1>
        <p style="font-size: 24px;">최종 스코어 - 1P: <span id="final-p1">0</span> | 2P: <span id="final-p2">0</span></p>
        <button id="restart-btn" onclick="showSelectScreen()">다시 하기</button>
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
            
            if (type === 'bounce') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(120, now);
                osc.frequency.exponentialRampToValueAtTime(30, now + 0.1);
                gain.gain.setValueAtTime(0.2, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.1);
            } else if (type === 'jump') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'triangle'; osc.frequency.setValueAtTime(150, now);
                osc.frequency.exponentialRampToValueAtTime(320, now + 0.1);
                gain.gain.setValueAtTime(0.2, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.1);
            } else if (type === 'dunk') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sawtooth'; osc.frequency.setValueAtTime(280, now);
                osc.frequency.exponentialRampToValueAtTime(40, now + 0.3);
                gain.gain.setValueAtTime(0.4, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.3);
            } else if (type === 'goal') {
                const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(523, now);
                osc.frequency.setValueAtTime(659, now + 0.1); osc.frequency.setValueAtTime(783, now + 0.2);
                gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                osc.connect(gain); gain.connect(audioCtx.destination); osc.start(now); osc.stop(now + 0.35);
            }
        }

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        const QUARTER_TIME = 60;
        let currentQuarter = 1;
        let p1Score = 0, p2Score = 0, timeLeft = QUARTER_TIME;
        let gameActive = false, timerInterval;
        let effectText = { text: '', alpha: 0, x: 0, y: 0 };
        let screenShake = 0;
        let particles = [];

        const keys = {};

        const hoops = [
            { x: 60, y: 190, rimX: 95, rimY: 230, side: 'left' },
            { x: 840, y: 190, rimX: 805, rimY: 230, side: 'right' }
        ];

        let p1SelectedSkill = 'sniper';
        let p2SelectedSkill = 'sniper';

        const p1 = {
            x: 180, y: 370, width: 38, height: 72, color: '#e53935', jerseyNo: '23', hairColor: '#333',
            vx: 0, vy: 0, isGrounded: false, hasBall: false, id: 1, armAngle: 0, shootAnimTimer: 0, facing: 1,
            gauge: 0, gaugeDir: 1, isCharging: false, animFrame: 0, isDunking: false, isDashing: false,
            skill: 'sniper', skillCd: 0, skillActive: false, stamina: 100
        };

        const p2 = {
            x: 685, y: 370, width: 38, height: 72, color: '#1e88e5', jerseyNo: '30', hairColor: '#ffb74d',
            vx: 0, vy: 0, isGrounded: false, hasBall: false, id: 2, armAngle: 0, shootAnimTimer: 0, facing: -1,
            gauge: 0, gaugeDir: 1, isCharging: false, animFrame: 0, isDunking: false, isDashing: false,
            skill: 'sniper', skillCd: 0, skillActive: false, stamina: 100
        };

        const ball = {
            x: 450, y: 200, radius: 11, vx: 0, vy: 0, holder: null, rotation: 0, trail: [], isOnFire: false
        };

        const gravity = 0.45;
        const groundY = 430;

        function selectSkill(playerNum, skillType, element) {
            const parent = element.parentElement;
            parent.querySelectorAll('.skill-opt').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');

            if (playerNum === 1) p1SelectedSkill = skillType;
            else p2SelectedSkill = skillType;
        }

        function showSelectScreen() {
            document.getElementById('game-over').style.display = 'none';
            document.getElementById('select-screen').style.display = 'flex';
        }

        function startGame() {
            p1.skill = p1SelectedSkill;
            p2.skill = p2SelectedSkill;
            document.getElementById('select-screen').style.display = 'none';
            resetGame();
        }

        function activateSkill(player) {
            if (player.skillCd > 0) return;
            player.skillCd = 8.0; playSound('jump');

            if (player.skill === 'sniper') {
                player.skillActive = true;
                effectText = { text: "PERFECT AIM!", alpha: 1.0, x: player.x + 20, y: player.y - 30 };
            } else if (player.skill === 'dash') {
                player.vx = player.facing * 14; player.stamina = 100;
                effectText = { text: "SONIC DASH!", alpha: 1.0, x: player.x + 20, y: player.y - 30 };
            } else if (player.skill === 'block') {
                player.vy = -15;
                effectText = { text: "IRON BLOCK!", alpha: 1.0, x: player.x + 20, y: player.y - 30 };
            }
            addParticles(player.x, player.y, '#ffb74d', 15);
        }

        function addParticles(x, y, color, count = 10) {
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: x, y: y,
                    vx: (Math.random() - 0.5) * 6, vy: (Math.random() - 0.5) * 6,
                    radius: Math.random() * 3 + 1, color: color, life: 1.0
                });
            }
        }

        function init() {
            window.addEventListener('keydown', e => {
                initAudio();
                if (e.repeat) return;
                keys[e.code] = true;

                if (e.code === 'Space' && p1.hasBall) {
                    if (checkDunkCondition(p1)) triggerDunk(p1);
                    else { p1.isCharging = true; p1.gauge = 0; p1.gaugeDir = 1; }
                }
                if (e.code === 'KeyE') activateSkill(p1);

                if (e.code === 'Enter' && p2.hasBall) {
                    if (checkDunkCondition(p2)) triggerDunk(p2);
                    else { p2.isCharging = true; p2.gauge = 0; p2.gaugeDir = 1; }
                }
                if (e.code === 'KeyK') activateSkill(p2);
            });

            window.addEventListener('keyup', e => {
                keys[e.code] = false;
                if (e.code === 'Space' && p1.hasBall && p1.isCharging) shootBall(p1);
                if (e.code === 'Enter' && p2.hasBall && p2.isCharging) shootBall(p2);
            });

            requestAnimationFrame(gameLoop);
        }

        function checkDunkCondition(player) {
            const targetHoop = player.id === 1 ? hoops[1] : hoops[0];
            return Math.abs((player.x + player.width/2) - targetHoop.rimX) < 160;
        }

        function triggerDunk(player) {
            player.isDunking = true; player.isCharging = false;
            player.vy = -12.5; player.vx = player.id === 1 ? 4.8 : -4.8;
            playSound('jump');
        }

        function executeDunk(player) {
            const targetHoop = player.id === 1 ? hoops[1] : hoops[0];
            player.hasBall = false; player.isDunking = false; player.shootAnimTimer = 15;
            ball.holder = null; ball.x = targetHoop.rimX; ball.y = targetHoop.rimY - 5;
            ball.vx = player.id === 1 ? 0.5 : -0.5; ball.vy = 12;

            playSound('dunk'); screenShake = 8;
            addParticles(targetHoop.rimX, targetHoop.rimY, '#ff9800', 20);
            effectText = { text: "SLAM DUNK!!", alpha: 1.0, x: targetHoop.rimX, y: targetHoop.rimY - 35 };
        }

        function startTimer() {
            clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                if (!gameActive) return;
                timeLeft--;
                document.getElementById('timer').innerText = timeLeft;
                
                if (p1.skillCd > 0) p1.skillCd = Math.max(0, p1.skillCd - 1);
                if (p2.skillCd > 0) p2.skillCd = Math.max(0, p2.skillCd - 1);

                if (p1.stamina < 100 && !p1.isDashing) p1.stamina = Math.min(100, p1.stamina + 4);
                if (p2.stamina < 100 && !p2.isDashing) p2.stamina = Math.min(100, p2.stamina + 4);

                if (timeLeft <= 0) handleQuarterEnd();
            }, 1000);
        }

        function handleQuarterEnd() {
            gameActive = false; clearInterval(timerInterval);

            if (currentQuarter < 3) {
                const noticeElem = document.getElementById('quarter-notice');
                document.getElementById('quarter-notice-title').innerText = currentQuarter + "Q END";
                noticeElem.style.display = 'flex';

                setTimeout(() => {
                    noticeElem.style.display = 'none';
                    currentQuarter++; timeLeft = QUARTER_TIME;
                    document.getElementById('quarter-text').innerText = currentQuarter + "Q";
                    document.getElementById('timer').innerText = timeLeft;
                    resetRoundPositions(); gameActive = true; startTimer();
                }, 2000);
            } else { endGame(); }
        }

        function resetGame() {
            p1Score = 0; p2Score = 0; currentQuarter = 1; timeLeft = QUARTER_TIME; gameActive = true;
            document.getElementById('p1-score').innerText = 0;
            document.getElementById('p2-score').innerText = 0;
            document.getElementById('quarter-text').innerText = "1Q";
            document.getElementById('timer').innerText = QUARTER_TIME;
            document.getElementById('game-over').style.display = 'none';
            resetRoundPositions(); startTimer();
        }

        function resetRoundPositions() {
            p1.x = 180; p1.y = 370; p1.vx = 0; p1.vy = 0; p1.stamina = 100;
            p1.hasBall = false; p1.shootAnimTimer = 0; p1.facing = 1; p1.isCharging = false; p1.isDunking = false; p1.skillActive = false;

            p2.x = 685; p2.y = 370; p2.vx = 0; p2.vy = 0; p2.stamina = 100;
            p2.hasBall = false; p2.shootAnimTimer = 0; p2.facing = -1; p2.isCharging = false; p2.isDunking = false; p2.skillActive = false;

            ball.x = 450; ball.y = 200; ball.vx = 0; ball.vy = 0;
            ball.holder = null; ball.trail = []; ball.rotation = 0; ball.isOnFire = false;
        }

        function shootBall(player) {
            const targetHoop = player.id === 1 ? hoops[1] : hoops[0];
            const targetX = targetHoop.rimX;

            player.shootAnimTimer = 15; player.hasBall = false; player.isCharging = false; ball.holder = null;
            const dx = targetX - (player.x + player.width / 2);
            const dist = Math.abs(dx);

            ball.x = player.x + player.width / 2 + player.facing * 10;
            ball.y = player.y - 10;

            // [난이도 완화] Perfect Zone 확장 (55% ~ 80% 적정 범위 인정)
            let perfectMin = 55, perfectMax = 80;
            if (player.skillActive) { perfectMin = 30; perfectMax = 95; player.skillActive = false; }

            const isPerfect = player.gauge >= perfectMin && player.gauge <= perfectMax;
            playSound('jump');

            if (isPerfect) {
                ball.vx = (dx / dist) * (6.0 + dist * 0.007);
                ball.vy = -12.5; ball.isOnFire = true;
                effectText = { text: "GREAT SHOT!", alpha: 1.0, x: player.x, y: player.y - 30 };
            } else {
                ball.isOnFire = false;
                let err = (player.gauge - 65) * 0.05;
                ball.vx = (dx / dist) * (6.0 + dist * 0.007) + err;
                ball.vy = -12.0;
            }
        }

        function updatePlayer(p, leftKey, rightKey, jumpKey, dashKey) {
            p.isDashing = keys[dashKey] && p.stamina > 5;
            if (p.isDashing) p.stamina = Math.max(0, p.stamina - 0.7);

            const speed = p.isDashing ? 6.5 : 4.0;

            if (keys[leftKey]) { p.vx = -speed; p.facing = -1; p.animFrame += 0.2; }
            else if (keys[rightKey]) { p.vx = speed; p.facing = 1; p.animFrame += 0.2; }
            else { p.vx = 0; p.animFrame = 0; }

            if (keys[jumpKey] && p.isGrounded && !p.isDunking) {
                p.vy = -11.5; p.isGrounded = false; playSound('jump');
            }

            p.vy += gravity; p.x += p.vx; p.y += p.vy;

            if (p.isDunking) {
                const targetHoop = p.id === 1 ? hoops[1] : hoops[0];
                const distToRim = Math.hypot((p.x + p.width/2) - targetHoop.rimX, p.y - targetHoop.rimY);
                if (distToRim < 55 || p.vy > 0) executeDunk(p);
            }

            if (p.x < 0) p.x = 0;
            if (p.x + p.width > canvas.width) p.x = canvas.width - p.width;

            if (p.y + p.height >= groundY) {
                p.y = groundY - p.height; p.vy = 0; p.isGrounded = true; p.isDunking = false;
            }

            // 게이지 속도 조절 (너무 빠르지 않게)
            if (p.isCharging && p.hasBall) {
                p.gauge += p.gaugeDir * 3.0;
                if (p.gauge >= 100) { p.gauge = 100; p.gaugeDir = -1; }
                if (p.gauge <= 0) { p.gauge = 0; p.gaugeDir = 1; }
            }

            if (p.shootAnimTimer > 0) { p.shootAnimTimer--; p.armAngle = -Math.PI / 2.5 * p.facing; } 
            else { p.armAngle = p.hasBall ? -Math.PI / 5 * p.facing : 0; }

            if (!ball.holder) {
                const dist = Math.hypot((p.x + p.width/2) - ball.x, (p.y + p.height/2) - ball.y);
                if (dist < 38) { ball.holder = p; p.hasBall = true; }
            } else if (ball.holder === p) {
                const bounceY = (p.vx !== 0 && p.isGrounded) ? Math.abs(Math.sin(p.animFrame * 2)) * 16 : 0;
                if (bounceY > 14) playSound('bounce');
                ball.x = p.x + p.width / 2 + p.facing * 16;
                ball.y = p.y + 15 + bounceY;
                ball.vx = 0; ball.vy = 0;
            }
        }

        function updateBall() {
            if (ball.holder) { ball.trail = []; return; }

            ball.vy += gravity; ball.x += ball.vx; ball.y += ball.vy;
            ball.rotation += ball.vx * 0.05;

            ball.trail.push({ x: ball.x, y: ball.y });
            if (ball.trail.length > (ball.isOnFire ? 8 : 4)) ball.trail.shift();

            if (ball.y + ball.radius >= groundY) {
                ball.y = groundY - ball.radius; ball.vy *= -0.65; ball.vx *= 0.8;
                if (Math.abs(ball.vy) > 2) playSound('bounce');
            }

            if (ball.x - ball.radius <= 0 || ball.x + ball.radius >= canvas.width) ball.vx *= -0.7;

            hoops.forEach(hoop => {
                const isLeftBb = hoop.side === 'left' && Math.abs(ball.x - hoop.x) < 15;
                const isRightBb = hoop.side === 'right' && Math.abs(ball.x - hoop.x) < 15;
                if ((isLeftBb || isRightBb) && ball.y > hoop.y && ball.y < hoop.y + 80) {
                    ball.vx *= -0.7; playSound('bounce');
                }

                // 림 득점 판정 (12px 유효 인정)
                const distToRim = Math.hypot(ball.x - hoop.rimX, ball.y - hoop.rimY);
                if (distToRim <= 12 && ball.vy > 0) {
                    playSound('goal'); screenShake = 6;
                    addParticles(hoop.rimX, hoop.rimY, '#4caf50', 18);

                    if (hoop.side === 'right') { p1Score += 2; document.getElementById('p1-score').innerText = p1Score; } 
                    else { p2Score += 2; document.getElementById('p2-score').innerText = p2Score; }
                    resetRoundPositions();
                }
            });
        }

        function updateParticles() {
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i]; p.x += p.vx; p.y += p.vy; p.life -= 0.035;
                if (p.life <= 0) particles.splice(i, 1);
            }
        }

        function endGame() {
            gameActive = false; clearInterval(timerInterval); playSound('goal');
            const winnerText = document.getElementById('winner-text');
            if (p1Score > p2Score) { winnerText.innerText = "PLAYER 1 WIN!"; winnerText.style.color = "#ff5252"; } 
            else if (p2Score > p1Score) { winnerText.innerText = "PLAYER 2 WIN!"; winnerText.style.color = "#448aff"; } 
            else { winnerText.innerText = "DRAW GAME!"; winnerText.style.color = "#ffeb3b"; }

            document.getElementById('final-p1').innerText = p1Score;
            document.getElementById('final-p2').innerText = p2Score;
            document.getElementById('game-over').style.display = 'flex';
        }

        // --- 디테일해진 그래픽 렌더링 ---
        function drawCourt() {
            // 코트 나뭇결 바닥
            ctx.fillStyle = '#d7ccc8'; ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = '#bcaaa4';
            for (let i = 0; i < canvas.width; i += 40) { ctx.fillRect(i, groundY, 20, canvas.height - groundY); }
            ctx.fillStyle = '#8d6e63'; ctx.fillRect(0, groundY, canvas.width, 6);

            // 코트 라인
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(60, groundY, 180, -Math.PI/2, 0); ctx.stroke();
            ctx.beginPath(); ctx.arc(840, groundY, 180, -Math.PI, -Math.PI/2); ctx.stroke();
            ctx.moveTo(450, groundY); ctx.lineTo(450, canvas.height); ctx.stroke();

            // 백보드 및 림
            hoops.forEach(h => {
                ctx.fillStyle = '#fff'; ctx.fillRect(h.side === 'left' ? h.x - 10 : h.x, h.y, 10, 80);
                ctx.strokeStyle = '#e65100'; ctx.lineWidth = 5;
                ctx.beginPath(); ctx.arc(h.rimX, h.rimY, 16, 0, Math.PI); ctx.stroke();
            });
        }

        function drawPlayer(p) {
            ctx.save();
            ctx.translate(p.x + p.width / 2, p.y);

            // 그림자
            ctx.fillStyle = 'rgba(0,0,0,0.3)';
            ctx.beginPath(); ctx.ellipse(0, p.height - 2, 18, 6, 0, 0, Math.PI * 2); ctx.fill();

            // 다리 & 신발
            const runCycle = Math.sin(p.animFrame * 3);
            ctx.fillStyle = '#fff'; // 운동화
            ctx.fillRect(-11 + runCycle * 8, p.height - 8, 10, 8);
            ctx.fillRect(1 - runCycle * 8, p.height - 8, 10, 8);

            ctx.fillStyle = '#ffcc80'; // 피부
            ctx.fillRect(-9 + runCycle * 8, p.height - 22, 7, 14);
            ctx.fillRect(2 - runCycle * 8, p.height - 22, 7, 14);

            // 유니폼 상/하의
            ctx.fillStyle = p.color;
            ctx.fillRect(-13, p.height - 36, 26, 15); // 바지
            ctx.fillRect(-14, 20, 28, 22); // 상의

            // 등번호
            ctx.fillStyle = '#ffffff'; ctx.font = 'bold 12px Arial'; ctx.textAlign = 'center';
            ctx.fillText(p.jerseyNo, 0, 36);

            // 머리 & 헤어스타일 (디테일)
            ctx.fillStyle = '#ffcc80';
            ctx.beginPath(); ctx.arc(0, 10, 11, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = p.hairColor; // 헤어
            ctx.beginPath(); ctx.arc(0, 7, 12, Math.PI, Math.PI * 2); ctx.fill();

            ctx.fillStyle = '#111'; // 눈
            ctx.fillRect(p.facing * 4, 9, 3, 3);

            // 팔
            ctx.strokeStyle = '#ffcc80'; ctx.lineWidth = 5;
            ctx.beginPath(); ctx.moveTo(0, 24);
            let armX = p.hasBall ? Math.cos(p.armAngle) * 20 * p.facing : Math.sin(p.animFrame * 3) * 10 * p.facing;
            let armY = p.hasBall ? 24 + Math.sin(p.armAngle) * 20 : 38;
            ctx.lineTo(armX, armY); ctx.stroke();

            ctx.restore();

            // UI: 스태미나 바
            ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(p.x - 1, p.y - 16, 40, 5);
            ctx.fillStyle = '#00e676'; ctx.fillRect(p.x - 1, p.y - 16, (p.stamina / 100) * 40, 5);

            // UI: 슈팅 게이지
            if (p.hasBall && p.isCharging) {
                const gx = p.x + p.width / 2 - 30; const gy = p.y - 30;
                let minZone = p.skillActive ? 30 : 55;
                let maxZone = p.skillActive ? 95 : 80;

                ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'; ctx.fillRect(gx - 2, gy - 2, 64, 10);
                ctx.fillStyle = '#ff9800'; ctx.fillRect(gx, gy, 60, 6);
                ctx.fillStyle = '#4caf50'; ctx.fillRect(gx + (minZone/100)*60, gy, ((maxZone - minZone)/100)*60, 6); // 적정 난이도 녹색지대

                const barX = gx + (p.gauge / 100) * 60;
                ctx.fillStyle = '#ffffff'; ctx.fillRect(barX - 1.5, gy - 2, 3, 10);
            }
        }

        function drawBall() {
            for (let i = 0; i < ball.trail.length; i++) {
                const t = ball.trail[i];
                ctx.fillStyle = ball.isOnFire ? `rgba(255, 87, 34, ${ (i + 1) / 8 })` : `rgba(255, 152, 0, ${ (i + 1) / 8 })`;
                ctx.beginPath(); ctx.arc(t.x, t.y, ball.radius * ((i + 1) / 6), 0, Math.PI * 2); ctx.fill();
            }

            ctx.save();
            ctx.translate(ball.x, ball.y);
            ctx.rotate(ball.rotation);

            ctx.fillStyle = ball.isOnFire ? '#ff3d00' : '#ff9800';
            ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI * 2); ctx.fill();

            ctx.strokeStyle = '#222'; ctx.lineWidth = 1.2;
            ctx.beginPath(); ctx.arc(0, 0, ball.radius, 0, Math.PI * 2);
            ctx.moveTo(-ball.radius, 0); ctx.lineTo(ball.radius, 0); ctx.stroke();

            ctx.restore();
        }

        function drawParticles() {
            particles.forEach(p => {
                ctx.save(); ctx.globalAlpha = p.life; ctx.fillStyle = p.color;
                ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2); ctx.fill(); ctx.restore();
            });
        }

        function drawEffects() {
            if (effectText.alpha > 0) {
                ctx.save();
                ctx.fillStyle = `rgba(255, 215, 0, ${effectText.alpha})`;
                ctx.font = 'bold 22px Arial'; ctx.textAlign = 'center';
                ctx.fillText(effectText.text, effectText.x, effectText.y);
                ctx.restore();
                effectText.alpha -= 0.02; effectText.y -= 0.3;
            }
        }

        function draw() {
            ctx.save();
            if (screenShake > 0) {
                ctx.translate((Math.random() - 0.5) * 6, (Math.random() - 0.5) * 6);
                screenShake--;
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawCourt();
            drawPlayer(p1);
            drawPlayer(p2);
            drawBall();
            drawParticles();
            drawEffects();

            ctx.restore();
        }

        function gameLoop() {
            if (gameActive) {
                updatePlayer(p1, 'KeyA', 'KeyD', 'KeyW', 'ShiftLeft');
                updatePlayer(p2, 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ShiftRight');
                updateBall();
                updateParticles();
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
