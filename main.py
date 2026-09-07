import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🎵 Advanced Rhythm Beat Game",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 업그레이드 박자 맞추기 리듬 게임")

st.markdown("""
### 🕹️ 게임 조작 및 설명
* **라인 키**: `D` | `F` | `J` | `K`
* **목숨(❤️)**: 총 3개가 제공되며, **MISS 발생 시 하트가 1개 차감**됩니다. (0개가 되면 GAME OVER!)
* **곡 & 난이도**: 대기 화면에서 원하시는 최신 스타일 음악 트랙과 난이도를 고른 뒤 **[GAME START]**를 눌러 시작하세요.
""")

game_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0; padding: 0; background-color: #0b0c10; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff; user-select: none; display: flex; justify-content: center; align-items: center; height: 100vh;
        }
        #game-container {
            width: 480px; height: 640px; background: #1f2833; border: 4px solid #66fcf1;
            border-radius: 16px; box-shadow: 0 0 35px rgba(102, 252, 241, 0.3); position: relative; overflow: hidden;
        }
        #hud {
            position: absolute; top: 15px; left: 0; width: 100%; display: flex; justify-content: space-around;
            align-items: center; font-size: 18px; font-weight: bold; z-index: 10; background: rgba(11, 12, 16, 0.75); padding: 10px 0;
            border-bottom: 2px solid #45a29e;
        }
        #start-screen, #game-over-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(11, 12, 16, 0.92); display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 20; gap: 20px;
        }
        .select-group { display: flex; flex-direction: column; gap: 8px; width: 80%; text-align: left; }
        label { font-size: 14px; color: #66fcf1; font-weight: bold; }
        select, button {
            padding: 12px; font-size: 16px; font-weight: bold; border-radius: 8px; border: none;
            cursor: pointer; background: #0b0c10; color: #fff; border: 2px solid #45a29e; outline: none;
        }
        button {
            background: linear-gradient(135deg, #45a29e, #66fcf1); color: #0b0c10;
            margin-top: 15px; border: none; box-shadow: 0 0 15px rgba(102, 252, 241, 0.5);
            transition: transform 0.15s;
        }
        button:hover { transform: scale(1.05); }
        #judgment {
            position: absolute; top: 38%; left: 50%; transform: translate(-50%, -50%);
            font-size: 40px; font-weight: 900; opacity: 0; transition: opacity 0.15s, transform 0.15s;
            pointer-events: none; z-index: 10; text-shadow: 0 0 15px rgba(255,255,255,0.8);
        }
        #combo-display {
            position: absolute; top: 46%; left: 50%; transform: translateX(-50%);
            font-size: 26px; font-weight: bold; color: #facc15; z-index: 10; pointer-events: none;
        }
        canvas { background: #0b0c10; display: block; }
    </style>
</head>
<body>
    <div id="game-container">
        <!-- 시작 / 설정 화면 -->
        <div id="start-screen">
            <h1 style="color:#66fcf1; margin-bottom:10px; text-shadow:0 0 10px #66fcf1;">🎵 RHYTHM BEAT</h1>
            <div class="select-group">
                <label>🎵 최신 트랙 선택</label>
                <select id="track-select">
                    <option value="cyber">1. Cyber Neon Beat (EDM)</option>
                    <option value="synth">2. Midnight Synthwave (Retro)</option>
                    <option value="arcade">3. High Energy Arcade (Fast)</option>
                </select>
            </div>
            <div class="select-group">
                <label>⚡ 난이도 선택</label>
                <select id="diff-select">
                    <option value="easy">EASY (속도 느림 / 입문자용)</option>
                    <option value="normal" selected>NORMAL (표준 속도)</option>
                    <option value="hard">HARD (속도 빠름 / 고난도)</option>
                </select>
            </div>
            <button onclick="startGame()">GAME START 🚀</button>
        </div>

        <!-- 게임 오버 화면 -->
        <div id="game-over-screen" style="display: none;">
            <h1 style="color:#ef4444; font-size:42px; margin-bottom:0;">GAME OVER</h1>
            <div style="font-size:20px; color:#c5c6c7;">최종 점수: <span id="final-score" style="color:#66fcf1;">0</span></div>
            <div style="font-size:20px; color:#c5c6c7;">최대 콤보: <span id="final-combo" style="color:#facc15;">0</span></div>
            <button onclick="showStartScreen()">다시 하기 🔄</button>
        </div>

        <!-- 게임 진행 HUD -->
        <div id="hud">
            <div>LIVES: <span id="lives" style="color:#ef4444;">❤️❤️❤️</span></div>
            <div>SCORE: <span id="score" style="color:#66fcf1;">0</span></div>
            <div>ACC: <span id="accuracy" style="color:#facc15;">100%</span></div>
        </div>

        <div id="judgment">PERFECT</div>
        <div id="combo-display"></div>
        <canvas id="gameCanvas" width="480" height="640"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const scoreEl = document.getElementById('score');
const accuracyEl = document.getElementById('accuracy');
const livesEl = document.getElementById('lives');
const judgmentEl = document.getElementById('judgment');
const comboDisplay = document.getElementById('combo-display');

const startScreen = document.getElementById('start-screen');
const gameOverScreen = document.getElementById('game-over-screen');
const finalScoreEl = document.getElementById('final-score');
const finalComboEl = document.getElementById('final-combo');

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

// 배경 루프 음악용 오실레이터 비트 제너레이터
let bgmTimer = null;
function playBGMTrack(type) {
    if (bgmTimer) clearInterval(bgmTimer);
    let step = 0;
    let baseFreq = type === 'cyber' ? 110 : (type === 'synth' ? 87.31 : 130.81);
    let tempo = type === 'arcade' ? 160 : (type === 'cyber' ? 220 : 280);

    bgmTimer = setInterval(() => {
        if (!gameActive) return;
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type === 'synth' ? 'sawtooth' : 'sine';
            const notesScale = [1, 1.25, 1.33, 1.5, 1.75];
            const noteOffset = notesScale[step % notesScale.length];
            
            osc.frequency.setValueAtTime(baseFreq * noteOffset, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.15);
            step++;
        } catch(e) {}
    }, tempo);
}

function playHitSound(freq) {
    try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.1);
    } catch(e) {}
}

const keyMap = ['d', 'f', 'j', 'k'];
const keyFreqs = [261.63, 329.63, 392.00, 523.25];
const laneColors = ['#f43f5e', '#3b82f6', '#3b82f6', '#f43f5e'];

const laneWidth = canvas.width / 4;
const judgeY = 540;

let notes = [];
let score = 0;
let combo = 0;
let maxCombo = 0;
let lives = 3;
let totalHits = 0;
let successfulHits = 0;
let gameActive = false;
let noteSpawnInterval = null;

let noteSpeed = 6;
let spawnRate = 450;

let keyState = [false, false, false, false];

function startGame() {
    const track = document.getElementById('track-select').value;
    const diff = document.getElementById('diff-select').value;

    if (diff === 'easy') { noteSpeed = 4.5; spawnRate = 550; }
    else if (diff === 'normal') { noteSpeed = 6.5; spawnRate = 420; }
    else if (diff === 'hard') { noteSpeed = 9; spawnRate = 280; }

    score = 0; combo = 0; maxCombo = 0; lives = 3;
    totalHits = 0; successfulHits = 0; notes = [];
    gameActive = true;

    startScreen.style.display = 'none';
    gameOverScreen.style.display = 'none';

    updateStats();
    playBGMTrack(track);

    if (noteSpawnInterval) clearInterval(noteSpawnInterval);
    noteSpawnInterval = setInterval(() => {
        if (!gameActive) return;
        const lane = Math.floor(Math.random() * 4);
        notes.push({ lane: lane, y: -30, hit: false });
    }, spawnRate);
}

function showStartScreen() {
    gameActive = false;
    if (bgmTimer) clearInterval(bgmTimer);
    if (noteSpawnInterval) clearInterval(noteSpawnInterval);
    startScreen.style.display = 'flex';
    gameOverScreen.style.display = 'none';
}

function gameOver() {
    gameActive = false;
    if (bgmTimer) clearInterval(bgmTimer);
    if (noteSpawnInterval) clearInterval(noteSpawnInterval);
    finalScoreEl.innerText = score;
    finalComboEl.innerText = maxCombo;
    gameOverScreen.style.display = 'flex';
}

document.addEventListener('keydown', (e) => {
    if (!gameActive) return;
    const key = e.key.toLowerCase();
    const laneIndex = keyMap.indexOf(key);
    if (laneIndex !== -1 && !keyState[laneIndex]) {
        keyState[laneIndex] = true;
        checkHit(laneIndex);
    }
});

document.addEventListener('keyup', (e) => {
    const key = e.key.toLowerCase();
    const laneIndex = keyMap.indexOf(key);
    if (laneIndex !== -1) keyState[laneIndex] = false;
});

function checkHit(lane) {
    let hitFound = false;
    for (let i = 0; i < notes.length; i++) {
        const note = notes[i];
        if (note.lane === lane && !note.hit) {
            const dist = Math.abs(note.y - judgeY);
            if (dist < 65) {
                hitFound = true;
                note.hit = true;
                totalHits++;
                playHitSound(keyFreqs[lane]);

                if (dist < 22) {
                    showJudgment("PERFECT", "#66fcf1");
                    score += 100; combo++;
                    successfulHits += 1.0;
                } else if (dist < 45) {
                    showJudgment("GREAT", "#38bdf8");
                    score += 50; combo++;
                    successfulHits += 0.7;
                } else {
                    showJudgment("GOOD", "#4ade80");
                    score += 20; combo++;
                    successfulHits += 0.4;
                }
                if (combo > maxCombo) maxCombo = combo;
                break;
            }
        }
    }
    updateStats();
}

function handleMiss() {
    lives--;
    combo = 0;
    totalHits++;
    showJudgment("MISS", "#ef4444");
    updateStats();

    if (lives <= 0) {
        gameOver();
    }
}

function showJudgment(text, color) {
    judgmentEl.innerText = text;
    judgmentEl.style.color = color;
    judgmentEl.style.opacity = '1';
    judgmentEl.style.transform = 'translate(-50%, -50%) scale(1.2)';
    setTimeout(() => {
        judgmentEl.style.opacity = '0';
        judgmentEl.style.transform = 'translate(-50%, -50%) scale(1.0)';
    }, 200);
}

function updateStats() {
    scoreEl.innerText = score;
    livesEl.innerText = '❤️'.repeat(Math.max(0, lives));
    comboDisplay.innerText = combo > 1 ? combo + " COMBO!" : "";
    const acc = totalHits === 0 ? 100 : Math.round((successfulHits / totalHits) * 100);
    accuracyEl.innerText = acc + "%";
}

function update() {
    if (!gameActive) return;
    for (let i = notes.length - 1; i >= 0; i--) {
        const note = notes[i];
        note.y += noteSpeed;

        if (note.y > judgeY + 55 && !note.hit) {
            notes.splice(i, 1);
            handleMiss();
        } else if (note.hit && note.y > judgeY + 20) {
            notes.splice(i, 1);
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < 4; i++) {
        ctx.strokeStyle = '#1f2833';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(i * laneWidth, 0);
        ctx.lineTo(i * laneWidth, canvas.height);
        ctx.stroke();

        if (keyState[i]) {
            ctx.fillStyle = 'rgba(102, 252, 241, 0.15)';
            ctx.fillRect(i * laneWidth, 0, laneWidth, canvas.height);
        }
    }

    ctx.strokeStyle = '#66fcf1';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(0, judgeY);
    ctx.lineTo(canvas.width, judgeY);
    ctx.stroke();

    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    for (let i = 0; i < 4; i++) {
        ctx.fillStyle = keyState[i] ? '#66fcf1' : '#c5c6c7';
        ctx.fillText(keyMap[i].toUpperCase(), i * laneWidth + laneWidth / 2, judgeY + 45);
    }

    notes.forEach(note => {
        if (!note.hit) {
            ctx.fillStyle = laneColors[note.lane];
            ctx.beginPath();
            ctx.roundRect(note.lane * laneWidth + 8, note.y - 10, laneWidth - 16, 22, 6);
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    });
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

components.html(game_html, height=680)
