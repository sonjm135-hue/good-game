import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 Real Rule 2P Basketball with Block & Animations",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Real Rule 2P Full Court Basketball")

st.markdown("""
### 🎮 실제 농구 규칙 & 애니메이션 적용
* **🛡️ 완벽한 블락 시스템**: 수비수가 슛/덩크 타이밍에 블락(`Space` / `Enter`)하면 공이 튕겨나가며 **득점이 완전히 불인정**됩니다!
* **🏀 단일 공 & 소유권**: 블락되거나 튀어 나간 공은 바닥에 떨어지며, 공에 먼저 닿는 플레이어가 공을 빼앗습니다.
* **🏃 동작 애니메이션**: 달리기, 슛(체중 이동 & 팔 뻗기), 슬로우 모션 덩크, 블락 포즈 모션이 모두 구체화되었습니다.
""")

game_real_rule_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #111; font-family: 'Impact', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }
        canvas { background: #181822; border: 4px solid #fff; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        
        #hud {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 24px;
            background: rgba(0,0,0,0.85); padding: 8px 24px; border-radius: 6px; border: 2px solid #555;
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
            <div style="font-size:18px; color:#aaa;">REAL RULE 1-ON-1</div>
            <div>2P (JORDAN): <span id="score2" style="color:#e74c3c;">0</span></div>
        </div>
        <div id="green-splash">BLOCKED! NO GOAL! 🛡️</div>
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
        osc.frequency.setValueAtTime(120, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.3);
    }
}

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const greenSplash = document.getElementById('green-splash');
const score1El = document.getElementById('score1');
const score2El = document.getElementById('score2');

let score1 = 0;
let score2 = 0;

// 양쪽 골대
const hoops = {
    left: { x: 80, y: 190, rimX: 115, rimY: 220, rimR: 16 },
    right: { x: 1020, y: 190, rimX: 985, rimY: 220, rimR: 16 }
};

// 단일 공 (Single Ball Physics)
const ball = {
    x: 200,
    y: 390,
    vx: 0,
    vy: 0,
    r: 10,
    holder: 1, // 1: 1P, 2: 2P, null: 공중/바닥
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
        blockCooldown: 0,
        shootAnimTimer: 0 // 슛 모션 후폭풍 연출
    };
}

const p1 = createPlayer(1, 200, '#fdb927', '#552583', '24', 'right');
const p2 = createPlayer(2, 900, '#ce1141', '#111111', '23', 'left');

const keys = {};

window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    keys[k] = true;
    if (e.key === 'ArrowLeft') keys['arrowleft'] = true;
    if (e.key === 'ArrowRight') keys['arrowright'] = true;
    if (e.key === 'ArrowUp') keys['arrowup'] = true;
    if (e.key === 'Enter') keys['enter'] = true;
    if (e.code === 'Space') keys['space'] = true;

    if (k === 'f' && ball.holder === 1) handleShootOrDunkPress(p1);
    if (k === 'l' && ball.holder === 2) handleShootOrDunkPress(p2);

    if (e.code === 'Space' && ball.holder === 2) triggerBlock(p1, p2);
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

// 블락 시스템 (실제 농구 규칙 적용: 공이 튕겨나가며 득점 미인정)
function triggerBlock(defender, attacker) {
    if (defender.blockCooldown > 0) return;

    defender.isBlocking = true;
    defender.blockCooldown = 40;
    setTimeout(() => { defender.isBlocking = false; }, 350);

    const dist = Math.hypot(defender.x - attacker.x, defender.y - attacker.y);

    if (dist < 65 && (attacker.isCharging || attacker.isDunking || attacker.isJumping || ball.holder === attacker.id)) {
        triggerSplash("REJECTED! BLOCKED! 🛡️ (NO GOAL)");
        playSound('block');

        // 공격 및 덩크 상태 즉시 해제 (득점 취소)
        attacker.isCharging = false;
        attacker.isDunking = false;
        attacker.dunkScored = true; // 덩크 득점 방지 플래그

        // 공 떨어뜨리기 (바닥으로 튕김)
        ball.holder = null;
        ball.isFlying = true;
        ball.isScored = true; // 불인정 처리
        ball.vx = (defender.x < attacker.x) ? -7 : 7;
        ball.vy = -6;
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
        p.shootAnimTimer = 15; // 슛 한 직후 팔 뻗는 모션
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
        const startY = p.y - 15;
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

// 득점 후 실점팀에게 공 주어짐
function resetAfterScore(scoredPlayerId) {
    p1.isDunking = false; p2.isDunking = false;
    p1.isCharging = false; p2.isCharging = false;

    if (scoredPlayerId === 1) { // 1P 득점 -> 2P 실점 후 인바운드
        p1.x = 800; p1.y = 375;
        p2.x = 180; p2.y = 375;
        ball.holder = 2;
    } else { // 2P 득점 -> 1P 실점 후 인바운드
        p1.x = 920; p1.y = 375;
        p2.x = 300; p2.y = 375;
        ball.holder = 1;
    }
    ball.isFlying = false;
    ball.vx = 0; ball.vy = 0;
}

function updatePlayer(p, leftKey, rightKey, jumpKey) {
    p.isMoving = false;
    if (p.blockCooldown > 0) p.blockCooldown--;
    if (p.shootAnimTimer > 0) p.shootAnimTimer--;

    if (p.isDunking) {
        const hoop = hoops[p.targetHoopKey];
        p.dunkProgress += 0.018;

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

    if (p.isMoving || p.isJumping) p.animFrame += 0.25;
    if (p.isCharging) p.power = Math.min(100, p.power + 2.3);
}

function update() {
    updatePlayer(p1, 'a', 'd', 'w');
    updatePlayer(p2, 'arrowleft', 'arrowright', 'arrowup');

    // 공 물리 및 루즈볼 잡기
    if (ball.holder === 1) {
        ball.x = p1.x + (p1.targetHoopKey === 'right' ? 28 : -8);
        ball.y = p1.y + 12;
    } else if (ball.holder === 2) {
        ball.x = p2.x + (p2.targetHoopKey === 'left' ? -8 : 28);
        ball.y = p2.y + 12;
    } else if (ball.isFlying) {
        ball.x += ball.vx;
        ball.y += ball.vy;
        ball.vy += 0.42;

        if (ball.y >= 410) {
            ball.y = 410;
            ball.vy *= -0.55;
            ball.vx *= 0.8;
        }

        // 떨어진 공 다시 줍기
        const d1 = Math.hypot(ball.x - (p1.x + 18), ball.y - p1.y);
        const d2 = Math.hypot(ball.x - (p2.x + 18), ball.y - p2.y);
        if (d1 < 38) { ball.holder = 1; ball.isFlying = false; }
        else if (d2 < 38) { ball.holder = 2; ball.isFlying = false; }

        // 링 통과 (득점)
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

// 애니메이션이 강화된 플레이어 그리기
function drawPlayer(p) {
    const runBounce = p.isMoving ? Math.sin(p.animFrame * 2) * 3 : 0;
    const legAngle = Math.sin(p.animFrame) * 18;
    const armAngle = Math.cos(p.animFrame) * 20;

    const bodyY = p.y + runBounce;

    // 1. 다리 걷기/뛰기 애니메이션
    ctx.fillStyle = '#3d2314';
    ctx.save();
    ctx.translate(p.x + 9, bodyY + 34);
    ctx.rotate((p.isMoving ? legAngle : 0) * Math.PI / 180);
    ctx.fillRect(-3, 0, 6, 11);
    ctx.fillStyle = '#fff'; ctx.fillRect(-4, 9, 8, 4);
    ctx.restore();

    ctx.fillStyle = '#3d2314';
    ctx.save();
    ctx.translate(p.x + 27, bodyY + 34);
    ctx.rotate((p.isMoving ? -legAngle : 0) * Math.PI / 180);
    ctx.fillRect(-3, 0, 6, 11);
    ctx.fillStyle = '#fff'; ctx.fillRect(-4, 9, 8, 4);
    ctx.restore();

    // 2. 몸통 (유니폼)
    ctx.fillStyle = p.color1;
    ctx.fillRect(p.x, bodyY, p.w, 24);
    ctx.fillStyle = p.color2;
    ctx.fillRect(p.x, bodyY + 24, p.w, 10);

    ctx.fillStyle = p.color2;
    ctx.font = 'bold 12px Impact';
    ctx.fillText(p.number, p.x + 11, bodyY + 17);

    // 3. 팔 & 슛/덩크/블락 모션 애니메이션
    ctx.fillStyle = '#3d2314';

    if (p.isBlocking) { // 블락 모션 (양손 하늘로)
        ctx.fillRect(p.x - 4, bodyY - 16, 6, 22);
        ctx.fillRect(p.x + 34, bodyY - 16, 6, 22);
    } else if (p.isDunking) { // 덩크 모션 (한 손 위로 강하게)
        const dunkDir = p.targetHoopKey === 'right' ? 32 : -6;
        ctx.fillRect(p.x + dunkDir, bodyY - 18, 7, 22);
    } else if (p.isCharging) { // 슛 모으는 모션 (팔을 뒤로 젖힘)
        ctx.fillRect(p.x + 6, bodyY - 10, 6, 16);
        ctx.fillRect(p.x + 24, bodyY - 10, 6, 16);
    } else if (p.shootAnimTimer > 0) { // 슛 쏜 직후 팔 뻗는 모션 (Follow-through)
        const shootDir = p.targetHoopKey === 'right' ? 34 : -8;
        ctx.fillRect(p.x + shootDir, bodyY - 15, 6, 20);
    } else { // 기본 런 애니메이션
        ctx.save();
        ctx.translate(p.x - 2, bodyY + 8);
        ctx.rotate((p.isMoving ? -armAngle : 0) * Math.PI / 180);
        ctx.fillRect(-3, 0, 6, 12);
        ctx.restore();

        ctx.save();
        ctx.translate(p.x + 38, bodyY + 8);
        ctx.rotate((p.isMoving ? armAngle : 0) * Math.PI / 180);
        ctx.fillRect(-3, 0, 6, 12);
        ctx.restore();
    }

    // 4. 머리
    ctx.fillStyle = '#3d2314';
    ctx.beginPath();
    ctx.arc(p.x + 18, bodyY - 14, 18, 0, Math.PI * 2);
    ctx.fill();

    // 5. 슛 게이지 HUD
    if (p.isCharging) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(p.x - 8, bodyY - 58, 52, 11);
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(p.x + 28, bodyY - 58, 9, 11);
        const isGreenZone = p.power >= 70 && p.power <= 88;
        ctx.fillStyle = isGreenZone ? '#2ecc71' : '#f39c12';
        ctx.fillRect(p.x - 8, bodyY - 58, (p.power / 100) * 52, 11);
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 1;
        ctx.strokeRect(p.x - 8, bodyY - 58, 52, 11);
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 풀코트
    ctx.fillStyle = '#c85a17';
    ctx.fillRect(0, 415, 1100, 85);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 413, 1100, 4);

    // 센터 라인
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

    // 농구공
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

components.html(game_real_rule_html, height=580)
