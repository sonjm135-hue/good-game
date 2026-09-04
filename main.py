import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 2P Full Court Basketball with Block",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 2P Full Court Basketball (Single Ball & Block Mechanic)")

st.markdown("""
### 🎮 2인용 풀코트 대전 규칙 & 조작법
* **공격 방법**: 공을 소지한 채 상대방 골대로 이동하여 슛 또는 덩크를 성공시키세요!
* **실점 후 리스타트**: 득점 발생 시, **실점한 플레이어**의 진영에서 공이 우선 주어집니다.
* **🛡️ 수비 & 블락 (Block)**: 상대가 슛/덩크를 할 때 가까이 다가가 **블락 키**를 누르면 쳐낼 수 있습니다!

| 플레이어 | 이동 | 점프 | 슛 / 덩크 | 🛡️ 블락 (Block) | 공격 목표 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1P (Kobe #24)** | `A` (좌), `D` (우) | `W` | **`F` 키** | **`Space` (스페이스)** | **오른쪽 골대** |
| **2P (Jordan #23)** | `←` (좌), `→` (우) | `↑` | **`L` 키** | **`Enter` (엔터)** | **왼쪽 골대** |
""")

game_fullcourt_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: 'Impact', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #181822; border: 4px solid #fff; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        
        #hud {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 24px;
            background: rgba(0,0,0,0.8); padding: 8px 24px; border-radius: 6px; border: 2px solid #555;
            display: flex; gap: 30px; align-items: center;
        }
        #green-splash {
            position: absolute; top: 25%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; color: #2ecc71; text-shadow: 0 0 20px #2ecc71, 2px 2px #000;
            opacity: 0; transition: opacity 0.2s; pointer-events: none; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="hud">
            <div>1P (KOBE): <span id="score1" style="color:#f1c40f;">0</span></div>
            <div style="font-size:18px; color:#aaa;">FULL COURT 1-ON-1</div>
            <div>2P (JORDAN): <span id="score2" style="color:#e74c3c;">0</span></div>
        </div>
        <div id="green-splash">HO HO HO! GREEN GIANT! 🔥</div>
        <canvas id="gameCanvas" width="1100" height="500"></canvas>
    </div>

<script>
// Sound System
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSound(type) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === 'swish') {
        osc.frequency.setValueAtTime(520, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.3);
    } else if (type === 'block') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.25);
    }
}

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const greenSplash = document.getElementById('green-splash');
const score1El = document.getElementById('score1');
const score2El = document.getElementById('score2');

let score1 = 0;
let score2 = 0;

// 양쪽 골대 (Left Hoop, Right Hoop)
const hoops = {
    left: { x: 80, y: 190, rimX: 115, rimY: 220, rimR: 16 },
    right: { x: 1020, y: 190, rimX: 985, rimY: 220, rimR: 16 }
};

// 단일 공 (Single Ball)
const ball = {
    x: 200,
    y: 390,
    vx: 0,
    vy: 0,
    r: 10,
    holder: 1, // 1: 1P소유, 2: 2P소유, null: 공중에 있음
    isFlying: false,
    isGreen: false,
    isScored: false,
    targetHoop: 'right'
};

function createPlayer(id, x, color1, color2, number, targetHoopKey) {
    return {
        id: id,
        x: x,
        y: 375,
        w: 36,
        h: 40,
        vx: 0,
        vy: 0,
        color1: color1,
        color2: color2,
        number: number,
        targetHoopKey: targetHoopKey,
        isJumping: false,
        isDunking: false,
        dunkProgress: 0,
        dunkScored: false,
        isCharging: false,
        power: 0,
        animFrame: 0,
        isMoving: false,
        isBlocking: false,
        blockCooldown: 0
    };
}

const p1 = createPlayer(1, 200, '#fdb927', '#552583', '24', 'right'); // 1P: 오른쪽 골대로 공격
const p2 = createPlayer(2, 900, '#ce1141', '#111111', '23', 'left');  // 2P: 왼쪽 골대로 공격

const keys = {};

window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    keys[k] = true;
    if (e.key === 'ArrowLeft') keys['arrowleft'] = true;
    if (e.key === 'ArrowRight') keys['arrowright'] = true;
    if (e.key === 'ArrowUp') keys['arrowup'] = true;
    if (e.key === 'Enter') keys['enter'] = true;
    if (e.code === 'Space') keys['space'] = true;

    // 1P 슛/덩크
    if (k === 'f' && ball.holder === 1) handleShootOrDunkPress(p1);
    // 2P 슛/덩크
    if (k === 'l' && ball.holder === 2) handleShootOrDunkPress(p2);

    // 1P 블락
    if (e.code === 'Space' && ball.holder === 2) triggerBlock(p1, p2);
    // 2P 블락
    if (e.key === 'Enter' && ball.holder === 1) triggerBlock(p2, p1);
});

window.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    keys[k] = false;
    if (e.key === 'ArrowLeft') keys['arrowleft'] = false;
    if (e.key === 'ArrowRight') keys['arrowright'] = false;
    if (e.key === 'ArrowUp') keys['arrowup'] = false;
    if (e.key === 'Enter') keys['enter'] = false;
    if (e.code === 'Space') keys['space'] = false;

    if (k === 'f' && ball.holder === 1) releaseShoot(p1);
    if (k === 'l' && ball.holder === 2) releaseShoot(p2);
});

// 블락 시도 함수
function triggerBlock(defender, attacker) {
    if (defender.blockCooldown > 0) return;
    
    defender.isBlocking = true;
    defender.blockCooldown = 40; // 쿨타임
    setTimeout(() => { defender.isBlocking = false; }, 300);

    const dist = Math.hypot(defender.x - attacker.x, defender.y - attacker.y);
    
    // 공격수와 거리가 가깝고, 점프 중이거나 슛/덩크 시도 중일 때 블락 성공
    if (dist < 60 && (attacker.isCharging || attacker.isDunking || attacker.isJumping)) {
        triggerSplash("REJECTED! BLOCKED! 🛡️");
        playSound('block');

        // 공격 무산 및 공 피치 밖으로 튕김
        attacker.isCharging = false;
        attacker.isDunking = false;
        ball.holder = null;
        ball.isFlying = true;
        ball.vx = (defender.x < attacker.x) ? 6 : -6;
        ball.vy = -7;
    }
}

function handleShootOrDunkPress(p) {
    const targetRimX = hoops[p.targetHoopKey].rimX;
    const isNearHoop = Math.abs(p.x - targetRimX) < 220;

    if (isNearHoop && p.isMoving && !p.isDunking) {
        p.isDunking = true;
        p.dunkProgress = 0;
        p.dunkScored = false;
        p.isJumping = true;
        p.isCharging = false;
    } else if (!p.isCharging && !p.isDunking) {
        p.isCharging = true;
        p.power = 0;
    }
}

function releaseShoot(p) {
    if (p.isCharging && !p.isDunking) {
        shootBall(p);
        p.isCharging = false;
    }
}

function triggerSplash(text) {
    greenSplash.innerText = text;
    greenSplash.style.opacity = '1';
    setTimeout(() => { greenSplash.style.opacity = '0'; }, 1300);
}

function shootBall(p) {
    ball.holder = null;
    ball.isFlying = true;
    ball.isScored = false;
    ball.targetHoop = p.targetHoopKey;

    const hoop = hoops[p.targetHoopKey];
    let isGreen = false;

    if (p.power >= 70 && p.power <= 88) {
        isGreen = true;
        const startX = p.x + 20;
        const startY = p.y;
        const targetX = hoop.rimX;
        const targetY = hoop.rimY;

        const gravity = 0.42;
        const time = 38;
        ball.vx = (targetX - startX) / time;
        ball.vy = (targetY - startY - 0.5 * gravity * time * time) / time;
    } else {
        const dir = p.targetHoopKey === 'right' ? 1 : -1;
        ball.vx = dir * (6 + (p.power / 100) * 8);
        ball.vy = -8 - (p.power / 100) * 4;
    }

    ball.isGreen = isGreen;
}

// 득점 발생 시, 점수를 먹힌(실점한) 사람에게 공 부여 및 위치 리셋
function resetAfterScore(scoredPlayerId) {
    p1.isDunking = false; p2.isDunking = false;
    p1.isCharging = false; p2.isCharging = false;
    
    if (scoredPlayerId === 1) { // 1P가 득점 -> 2P에게 공 부여
        p1.x = 800; p1.y = 375;
        p2.x = 200; p2.y = 375; // 2P 리스폰
        ball.holder = 2;
    } else { // 2P가 득점 -> 1P에게 공 부여
        p1.x = 900; p1.y = 375; // 1P 리스폰
        p2.x = 300; p2.y = 375;
        ball.holder = 1;
    }
    ball.isFlying = false;
    ball.vx = 0; ball.vy = 0;
}

function updatePlayer(p, leftKey, rightKey, jumpKey) {
    p.isMoving = false;
    if (p.blockCooldown > 0) p.blockCooldown--;

    if (p.isDunking) {
        const hoop = hoops[p.targetHoopKey];
        p.dunkProgress += 0.02;

        const startX = p.targetHoopKey === 'right' ? hoop.rimX - 180 : hoop.rimX + 180;
        p.x = startX + p.dunkProgress * (hoop.rimX - startX);
        p.y = 375 - Math.sin(p.dunkProgress * Math.PI) * 160;

        if (p.dunkProgress >= 0.88 && !p.dunkScored) {
            p.dunkScored = true;
            if (p.id === 1) score1 += 2; else score2 += 2;
            score1El.innerText = score1;
            score2El.innerText = score2;

            triggerSplash(`${p.id === 1 ? 'KOBE' : 'JORDAN'} POWER DUNK! 🔥`);
            playSound('swish');

            setTimeout(() => resetAfterScore(p.id), 800);
        }

        if (p.dunkProgress >= 1.0) {
            p.isDunking = false;
            p.y = 375;
            p.isJumping = false;
        }
    } else {
        if (keys[leftKey]) { p.x -= 4; p.isMoving = true; }
        if (keys[rightKey]) { p.x += 4; p.isMoving = true; }
        if (keys[jumpKey] && !p.isJumping) {
            p.vy = -11;
            p.isJumping = true;
        }

        p.y += p.vy;
        p.vy += 0.55;

        if (p.y >= 375) {
            p.y = 375;
            p.isJumping = false;
        }

        if (p.x < 30) p.x = 30;
        if (p.x > 1030) p.x = 1030;
    }

    if (p.isMoving || p.isJumping) p.animFrame += 0.2;
    if (p.isCharging) p.power = Math.min(100, p.power + 2.3);
}

function update() {
    updatePlayer(p1, 'a', 'd', 'w');
    updatePlayer(p2, 'arrowleft', 'arrowright', 'arrowup');

    // 공 위치 & 소유권 물리
    if (ball.holder === 1) {
        ball.x = p1.x + 28;
        ball.y = p1.y + 15;
    } else if (ball.holder === 2) {
        ball.x = p2.x + 8;
        ball.y = p2.y + 15;
    } else if (ball.isFlying) {
        ball.x += ball.vx;
        ball.y += ball.vy;
        ball.vy += 0.42;

        if (ball.y >= 410) {
            ball.y = 410;
            ball.vy *= -0.5;
            ball.vx *= 0.8;
        }

        // 루즈볼 루팡 (바닥에 튄 공 줍기)
        const d1 = Math.hypot(ball.x - p1.x, ball.y - p1.y);
        const d2 = Math.hypot(ball.x - p2.x, ball.y - p2.y);
        if (d1 < 35) { ball.holder = 1; ball.isFlying = false; }
        else if (d2 < 35) { ball.holder = 2; ball.isFlying = false; }

        // 링 판정
        const hoop = hoops[ball.targetHoop];
        const distToRim = Math.hypot(ball.x - hoop.rimX, ball.y - hoop.rimY);

        if (distToRim < hoop.rimR && ball.vy > 0 && !ball.isScored) {
            ball.isScored = true;
            const scorerId = (ball.targetHoop === 'right') ? 1 : 2;
            if (scorerId === 1) score1 += 2; else score2 += 2;
            score1El.innerText = score1;
            score2El.innerText = score2;

            triggerSplash(ball.isGreen ? "PERFECT GREEN RELEASE! 🔥" : "SWISH! GOAL! 🔥");
            playSound('swish');

            setTimeout(() => resetAfterScore(scorerId), 800);
        }
    }
}

function drawPlayer(p) {
    const legAngle = Math.sin(p.animFrame) * 12;
    const armAngle = Math.cos(p.animFrame) * 15;

    // 다리
    ctx.fillStyle = '#3d2314';
    ctx.save();
    ctx.translate(p.x + 9, p.y + 34);
    ctx.rotate((p.isMoving ? legAngle : 0) * Math.PI / 180);
    ctx.fillRect(-3, 0, 6, 11);
    ctx.fillStyle = '#fff'; ctx.fillRect(-4, 9, 8, 4);
    ctx.restore();

    ctx.fillStyle = '#3d2314';
    ctx.save();
    ctx.translate(p.x + 27, p.y + 34);
    ctx.rotate((p.isMoving ? -legAngle : 0) * Math.PI / 180);
    ctx.fillRect(-3, 0, 6, 11);
    ctx.fillStyle = '#fff'; ctx.fillRect(-4, 9, 8, 4);
    ctx.restore();

    // 몸통
    ctx.fillStyle = p.color1;
    ctx.fillRect(p.x, p.y, p.w, 24);
    ctx.fillStyle = p.color2;
    ctx.fillRect(p.x, p.y + 24, p.w, 10);

    ctx.fillStyle = p.color2;
    ctx.font = 'bold 12px Impact';
    ctx.fillText(p.number, p.x + 11, p.y + 17);

    // 팔 (블락 모션 반영)
    ctx.fillStyle = '#3d2314';
    if (p.isBlocking) {
        ctx.fillRect(p.x - 2, p.y - 15, 6, 20); // 블락 손 들어올리기
        ctx.fillRect(p.x + 32, p.y - 15, 6, 20);
    } else if (p.isDunking) {
        ctx.fillRect(p.x + 28, p.y - 12, 6, 16);
    } else {
        ctx.save();
        ctx.translate(p.x - 2, p.y + 8);
        ctx.rotate((p.isMoving ? -armAngle : 0) * Math.PI / 180);
        ctx.fillRect(-3, 0, 6, 12);
        ctx.restore();

        ctx.save();
        ctx.translate(p.x + 38, p.y + 8);
        ctx.rotate((p.isMoving ? armAngle : 0) * Math.PI / 180);
        ctx.fillRect(-3, 0, 6, 12);
        ctx.restore();
    }

    // 머리
    ctx.fillStyle = '#3d2314';
    ctx.beginPath();
    ctx.arc(p.x + 18, p.y - 14, 18, 0, Math.PI * 2);
    ctx.fill();

    // 슛 게이지
    if (p.isCharging) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(p.x - 8, p.y - 58, 52, 11);
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(p.x + 28, p.y - 58, 9, 11);
        const isGreenZone = p.power >= 70 && p.power <= 88;
        ctx.fillStyle = isGreenZone ? '#2ecc71' : '#f39c12';
        ctx.fillRect(p.x - 8, p.y - 58, (p.power / 100) * 52, 11);
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 1;
        ctx.strokeRect(p.x - 8, p.y - 58, 52, 11);
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 풀코트 바닥
    ctx.fillStyle = '#c85a17';
    ctx.fillRect(0, 415, 1100, 85);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 413, 1100, 4);

    // 중앙선
    ctx.fillRect(548, 413, 4, 87);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(550, 415, 70, Math.PI, 2 * Math.PI);
    ctx.stroke();

    // 양쪽 백보드 및 림
    ['left', 'right'].forEach(key => {
        const h = hoops[key];
        const isLeft = key === 'left';
        ctx.fillStyle = '#222';
        ctx.fillRect(isLeft ? 60 : 1020, 190, 12, 225);
        ctx.fillStyle = 'rgba(255,255,255,0.85)';
        ctx.fillRect(isLeft ? 70 : 1010, 140, 10, 100);
        ctx.strokeStyle = '#ce1141';
        ctx.strokeRect(isLeft ? 72 : 1012, 170, 6, 40);
        ctx.strokeStyle = '#e67e22';
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(h.rimX, h.rimY);
        ctx.lineTo(isLeft ? 75 : 1015, h.rimY);
        ctx.stroke();
    });

    drawPlayer(p1);
    drawPlayer(p2);

    // 공 그리기
    ctx.fillStyle = '#e67e22';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#000'; ctx.lineWidth = 1;
    ctx.stroke();
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

components.html(game_fullcourt_html, height=580)
