import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🎵 Rhythm Beat Game",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 박자 맞추기 리듬 게임")

st.markdown("""
### 🕹️ 조작 방법
* **키보드 라인**: `D` | `F` | `J` | `K`
* 위에서 떨어지는 노트가 아래 **판정 선(라인)**에 맞춰 내려왔을 때 해당 키를 누르세요!
* 타이밍 정확도에 따라 **PERFECT(100점)**, **GREAT(50점)**, **MISS(콤보 끊김)** 판정을 받습니다.
""")

game_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0; padding: 0; background-color: #0d0e15; font-family: 'Arial', sans-serif;
            color: #fff; user-select: none; display: flex; justify-content: center; align-items: center; height: 100vh;
        }
        #game-container {
            width: 450px; height: 600px; background: #161925; border: 4px solid #8b5cf6;
            border-radius: 12px; box-shadow: 0 0 30px rgba(139, 92, 246, 0.4); position: relative; overflow: hidden;
        }
        #hud {
            position: absolute; top: 15px; left: 0; width: 100%; display: flex; justify-content: space-around;
            font-size: 18px; font-weight: bold; z-index: 10; background: rgba(0,0,0,0.5); padding: 8px 0;
        }
        #judgment {
            position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
            font-size: 36px; font-weight: 900; opacity: 0; transition: opacity 0.15s, transform 0.15s;
            pointer-events: none; z-index: 10; text-shadow: 0 0 10px rgba(255,255,255,0.8);
        }
        #combo-display {
            position: absolute; top: 48%; left: 50%; transform: translateX(-50%);
            font-size: 22px; font-weight: bold; color: #facc15; z-index: 10; pointer-events: none;
        }
        canvas { background: #11131f; display: block; }
    </style>
</head>
<body>
    <div id="game-container">
        <div id="hud">
            <div>SCORE: <span id="score" style="color:#a855f7;">0</span></div>
            <div>ACCURACY: <span id="accuracy" style="color:#38bdf8;">100%</span></div>
        </div>
        <div id="judgment">PERFECT</div>
        <div id="combo-display"></div>
        <canvas id="gameCanvas" width="450" height="600"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const scoreEl = document.getElementById('score');
const accuracyEl = document.getElementById('accuracy');
const judgmentEl = document.getElementById('judgment');
const comboDisplay = document.getElementById('combo-display');

// 오디오 효과음 생성 함수
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playHitSound(freq) {
    try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.1);
    } catch(e) {}
}

const keyMap = ['d', 'f', 'j', 'k'];
const keyFreqs = [261.63, 329.63, 392.00, 523.25]; // C, E, G, C(음계)
const laneColors = ['#f43f5e', '#3b82f6', '#3b82f6', '#f43f5e'];

const laneWidth = canvas.width / 4;
const judgeY = 510; // 판정 선 Y 위치
const noteSpeed = 6;

let notes = [];
let score = 0;
let combo = 0;
let maxCombo = 0;
let totalHits = 0;
let successfulHits = 0;

let keyState = [false, false, false, false];

// 랜덤 노트 생성 타이머
setInterval(() => {
    const lane = Math.floor(Math.random() * 4);
    notes.push({
        lane: lane,
        y: -30,
        hit: false
    });
}, 450);

document.addEventListener('keydown', (e) => {
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
    if (laneIndex !== -1) {
        keyState[laneIndex] = false;
    }
});

function checkHit(lane) {
    let hitFound = false;

    for (let i = 0; i < notes.length; i++) {
        const note = notes[i];
        if (note.lane === lane && !note.hit) {
            const dist = Math.abs(note.y - judgeY);

            if (dist < 60) {
                hitFound = true;
                note.hit = true;
                totalHits++;
                playHitSound(keyFreqs[lane]);

                if (dist < 20) {
                    showJudgment("PERFECT", "#a855f7");
                    score += 100;
                    combo++;
                    successfulHits += 1.0;
                } else if (dist < 42) {
                    showJudgment("GREAT", "#38bdf8");
                    score += 50;
                    combo++;
                    successfulHits += 0.7;
                } else {
                    showJudgment("GOOD", "#4ade80");
                    score += 20;
                    combo++;
                    successfulHits += 0.4;
                }
                break;
            }
        }
    }

    if (!hitFound) {
        // 비어있는 곳을 눌렀을 때
    }

    updateStats();
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
    if (combo > 1) {
        comboDisplay.innerText = combo + " COMBO!";
    } else {
        comboDisplay.innerText = "";
    }

    const acc = totalHits === 0 ? 100 : Math.round((successfulHits / totalHits) * 100);
    accuracyEl.innerText = acc + "%";
}

function update() {
    for (let i = notes.length - 1; i >= 0; i--) {
        const note = notes[i];
        note.y += noteSpeed;

        // 판정 선을 지나쳐 무시된 경우 (MISS)
        if (note.y > judgeY + 50 && !note.hit) {
            notes.splice(i, 1);
            combo = 0;
            totalHits++;
            showJudgment("MISS", "#ef4444");
            updateStats();
        } else if (note.hit && note.y > judgeY + 20) {
            notes.splice(i, 1);
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 트랙 라인 그리기
    for (let i = 0; i < 4; i++) {
        ctx.strokeStyle = '#22263a';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(i * laneWidth, 0);
        ctx.lineTo(i * laneWidth, canvas.height);
        ctx.stroke();

        // 키 버튼 눌림 효과
        if (keyState[i]) {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.fillRect(i * laneWidth, 0, laneWidth, canvas.height);
        }
    }

    // 판정 라인 그리기
    ctx.strokeStyle = '#facc15';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(0, judgeY);
    ctx.lineTo(canvas.width, judgeY);
    ctx.stroke();

    // 키 가이드 텍스트
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    for (let i = 0; i < 4; i++) {
        ctx.fillStyle = keyState[i] ? '#fff' : '#64748b';
        ctx.fillText(keyMap[i].toUpperCase(), i * laneWidth + laneWidth / 2, judgeY + 45);
    }

    // 노트 그리기
    notes.forEach(note => {
        if (!note.hit) {
            ctx.fillStyle = laneColors[note.lane];
            ctx.beginPath();
            ctx.roundRect(note.lane * laneWidth + 8, note.y - 10, laneWidth - 16, 20, 6);
            ctx.fill();

            // 노트 테두리 빛 효과
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

components.html(game_html, height=640)
