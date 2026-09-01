import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NBA 2K Streamlit Ultra",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 NBA 2K Ultra Edition")

# 사이드바 설정
st.sidebar.header("⚙️ ARENA & TEAM SELECTION")
team_choice = st.sidebar.selectbox(
    "SELECT TEAM",
    ["CHICAGO BULLS (United Center)", "LA LAKERS (Crypto.com Arena)"]
)

if "LAKERS" in team_choice:
    floor_color = "0xfdb927"
    paint_color = "0x552583"
    arena_name = "CRYPTO.COM ARENA"
    team_code = "LAL"
else:
    floor_color = "0xc85a17"
    paint_color = "0xce1141"
    arena_name = "UNITED CENTER"
    team_code = "CHI"

st.markdown("""
### 🎮 NBA 2K 조작키
* **이동 (Move)**: `W`, `A`, `S`, `D` — **2K Broadcast 액션 카메라가 플레이어를 정밀 추적합니다.**
* **방향 회전 (Turn)**: `Q` (Left), `E` (Right)
* **점프 (Jump)**: `Space`
* **2K Shot Meter (Shoot)**: **`F` 키 또는 마우스 클릭**
  * **🎯 Green Light Shot**: 원형 게이지가 **Top 화살표(80~92%)**에 맞춰질 때 떼면 **Perfect Release + Green Giant 사운드**가 발동합니다!
""")

game_ultra_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background-color: #030305; font-family: 'Impact', 'Arial Black', sans-serif; user-select: none; }}
        #canvas-container {{ width: 100vw; height: 78vh; display: flex; justify-content: center; align-items: center; position: relative; }}
        
        /* NBA 2K Broadcast Scorebug (상단 방송 전광판) */
        #scorebug {{
            position: absolute; top: 20px; left: 25px; display: flex; align-items: center;
            background: linear-gradient(180deg, rgba(15,15,20,0.95) 0%, rgba(5,5,8,0.98) 100%);
            border: 1px solid rgba(255,255,255,0.15); border-left: 6px solid #ce1141;
            border-radius: 6px; padding: 10px 22px; color: #fff;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8); pointer-events: none;
        }}
        .team-badge {{ font-size: 22px; font-weight: 900; letter-spacing: 2px; color: #f1c40f; margin-right: 15px; }}
        .score-info {{ font-size: 18px; color: #ddd; letter-spacing: 1px; }}
        .score-num {{ font-size: 26px; color: #2ecc71; font-weight: bold; margin: 0 8px; }}

        /* NBA 2K Perfect Green Release Splash Effect */
        #green-splash {{
            position: absolute; top: 32%; left: 50%; transform: translate(-50%, -50%) scale(0.8);
            font-size: 50px; font-weight: 900; font-style: italic;
            color: #2ecc71; text-shadow: 0 0 25px #2ecc71, 3px 3px 6px #000;
            opacity: 0; transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: none; text-transform: uppercase; letter-spacing: 3px;
        }}

        /* 2K Circular Shot Meter UI (선수 머리/발 옆 2K 시그니처 게이지) */
        #shot-meter-ring {{
            position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%);
            width: 80px; height: 80px; border-radius: 50%;
            background: rgba(0,0,0,0.65); border: 3px solid rgba(255,255,255,0.3);
            display: none; box-shadow: 0 0 15px rgba(0,0,0,0.8);
        }}
        #meter-pointer {{
            position: absolute; top: 5%; left: 50%; width: 6px; height: 38px;
            background: #f39c12; transform-origin: bottom center; transform: translateX(-50%) rotate(0deg);
            border-radius: 3px; box-shadow: 0 0 8px #f39c12;
        }}
        #meter-green-mark {{
            position: absolute; top: 4px; left: 50%; transform: translateX(-50%);
            width: 12px; height: 12px; background: #2ecc71; border-radius: 50%;
            box-shadow: 0 0 10px #2ecc71;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="scorebug">
            <div class="team-badge">{team_code}</div>
            <div class="score-info">PTS <span class="score-num" id="score">0</span> | FGM <span class="score-num" style="color:#fff;" id="fgm">0</span></div>
        </div>
        
        <div id="green-splash">EXCELLENT! GREEN LIGHT 🔥</div>

        <div id="shot-meter-ring">
            <div id="meter-green-mark"></div>
            <div id="meter-pointer"></div>
        </div>
    </div>

<script>
// Green Giant Audio System
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playGreenGiantSound() {{
    const audio = new Audio('https://www.soundboard.com/handler/gettrack.ashx?id=516543');
    audio.play().catch(() => {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.frequency.setValueAtTime(523.25, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.4);
    }});
}}

const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x040406);
scene.fog = new THREE.FogExp2(0x040406, 0.018); // 2K 아레나 안개/조명 분위기

const camera = new THREE.PerspectiveCamera(58, window.innerWidth / (window.innerHeight * 0.78), 0.1, 1000);

const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.75);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
container.appendChild(renderer.domElement);

// 2K 아레나 3점 조명 스팟
const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambientLight);

const centerSpot = new THREE.SpotLight(0xffffff, 1.8);
centerSpot.position.set(0, 40, 0);
centerSpot.angle = Math.PI / 3;
centerSpot.penumbra = 0.5;
centerSpot.castShadow = true;
scene.add(centerSpot);

// 1. 코트 패널 & 광택 재질
const courtGeo = new THREE.BoxGeometry(22, 0.2, 32);
const courtMat = new THREE.MeshStandardMaterial({{ color: {floor_color}, roughness: 0.2, metalness: 0.15 }});
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = 0;
court.receiveShadow = true;
scene.add(court);

// 페인트존
const paintGeo = new THREE.BoxGeometry(5.8, 0.22, 10);
const paintMat = new THREE.MeshStandardMaterial({{ color: {paint_color}, roughness: 0.3 }});
const paintArea = new THREE.Mesh(paintGeo, paintMat);
paintArea.position.set(0, 0, -10.5);
paintArea.receiveShadow = true;
scene.add(paintArea);

// 3D 3점선 곡선 라인 생성
const arcShape = new THREE.Shape();
arcShape.absarc(0, -11, 6.75, 0, Math.PI, false);
const arcPoints = arcShape.getPoints(32);
const arcGeo = new THREE.BufferGeometry().setFromPoints(arcPoints);
const arcMat = new THREE.LineBasicMaterial({{ color: 0xffffff, linewidth: 3 }});
const threePointLine = new THREE.Line(arcGeo, arcMat);
threePointLine.rotation.x = Math.PI / 2;
threePointLine.position.y = 0.12;
scene.add(threePointLine);

// 2. 백보드 프레임 및 타겟 박스
const rimPos = new THREE.Vector3(0, 3.05, -12);
const rimRadius = 0.45;
const ballRadius = 0.22;

const poleGeo = new THREE.CylinderGeometry(0.12, 0.15, 4.8);
const poleMat = new THREE.MeshStandardMaterial({{ color: 0x111111, metalness: 0.8 }});
const pole = new THREE.Mesh(poleGeo, poleMat);
pole.position.set(0, 2.4, -13.6);
scene.add(pole);

// 백보드 아크릴
const boardGroup = new THREE.Group();
const boardGlassGeo = new THREE.BoxGeometry(2.2, 1.3, 0.06);
const boardGlassMat = new THREE.MeshPhysicalMaterial({{ 0: 0xffffff, transparent: true, opacity: 0.7, roughness: 0.1, transmission: 0.9 }});
const boardGlass = new THREE.Mesh(boardGlassGeo, boardGlassMat);

const innerBoxGeo = new THREE.BoxGeometry(0.7, 0.55, 0.08);
const innerBoxMat = new THREE.MeshStandardMaterial({{ color: 0xcc0000 }});
const innerBox = new THREE.Mesh(innerBoxGeo, innerBoxMat);
innerBox.position.set(0, -0.15, 0.01);

boardGroup.add(boardGlass, innerBox);
boardGroup.position.set(0, 3.65, -12.8);
scene.add(boardGroup);

const rimGeo = new THREE.TorusGeometry(rimRadius, 0.04, 16, 32);
const rimMat = new THREE.MeshStandardMaterial({{ color: 0xff3300, roughness: 0.2, metalness: 0.5 }});
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.rotation.x = Math.PI / 2;
rim.position.copy(rimPos);
scene.add(rim);

// 3. 2K 캐릭터 플레이어 & 발밑 Indicator Ring
const playerGroup = new THREE.Group();
playerGroup.position.set(0, 1.0, 5);
scene.add(playerGroup);

// 발밑 2K Indicator Ring
const ringGeo = new THREE.RingGeometry(0.5, 0.6, 32);
const ringMat = new THREE.MeshBasicMaterial({{ color: 0x2ecc71, side: THREE.DoubleSide }});
const playerRing = new THREE.Mesh(ringGeo, ringMat);
playerRing.rotation.x = Math.PI / 2;
playerRing.position.y = -0.88;
playerGroup.add(playerRing);

// 디테일 팔/손
const skinMat = new THREE.MeshStandardMaterial({{ color: 0x3d2314, roughness: 0.6 }});
const handGroup = new THREE.Group();
const armGeo = new THREE.CylinderGeometry(0.06, 0.08, 0.45);
const armMesh = new THREE.Mesh(armGeo, skinMat);
handGroup.add(armMesh);

const palmGeo = new THREE.BoxGeometry(0.12, 0.15, 0.05);
const palmMesh = new THREE.Mesh(palmGeo, skinMat);
palmMesh.position.set(0, 0.25, 0);
handGroup.add(palmMesh);

handGroup.position.set(0.3, 0.1, 0.2);
handGroup.rotation.x = Math.PI / 3;
playerGroup.add(handGroup);

// 농구공
const heldBallGeo = new THREE.SphereGeometry(ballRadius, 32, 32);
const heldBallMat = new THREE.MeshStandardMaterial({{ color: 0xd35400, roughness: 0.45 }});
const heldBall = new THREE.Mesh(heldBallGeo, heldBallMat);
heldBall.position.set(0.3, 0.48, 0.25);
heldBall.castShadow = true;
playerGroup.add(heldBall);

// 키 조작 (F키 슛)
const keys = {{ w: false, a: false, s: false, d: false, q: false, e: false, space: false }};

window.addEventListener('keydown', (evt) => {{
    const k = evt.key.toLowerCase();
    if (k in keys) keys[k] = true;
    if (evt.code === 'Space') keys.space = true;
    if (k === 'f') startCharging();
}});

window.addEventListener('keyup', (evt) => {{
    const k = evt.key.toLowerCase();
    if (k in keys) keys[k] = false;
    if (evt.code === 'Space') keys.space = false;
    if (k === 'f') releaseShoot();
}});

window.addEventListener('mousedown', () => {{ startCharging(); }});
window.addEventListener('mouseup', () => {{ releaseShoot(); }});

let isCharging = false;
let chargePower = 0;
let playerPosY = 1.0;
let jumpVel = 0;
let isJumping = false;
let activeBalls = [];
let score = 0;
let fgm = 0;

const meterRing = document.getElementById('shot-meter-ring');
const meterPointer = document.getElementById('meter-pointer');
const greenSplash = document.getElementById('green-splash');

function startCharging() {{
    if (!isCharging) {{
        isCharging = true;
        chargePower = 0;
        meterRing.style.display = 'block';
    }}
}}

function releaseShoot() {{
    if (isCharging) {{
        shootBall(chargePower);
        isCharging = false;
        meterRing.style.display = 'none';
        heldBall.visible = false;
        setTimeout(() => {{ heldBall.visible = true; }}, 600);
    }}
}}

function triggerGreenSplash() {{
    greenSplash.style.opacity = '1';
    greenSplash.style.transform = 'translate(-50%, -50%) scale(1.1)';
    setTimeout(() => {{
        greenSplash.style.opacity = '0';
        greenSplash.style.transform = 'translate(-50%, -50%) scale(0.8)';
    }}, 1400);
}}

function shootBall(power) {{
    const ballMesh = new THREE.Mesh(heldBallGeo, heldBallMat);
    ballMesh.castShadow = true;
    const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(playerGroup.quaternion).normalize();
    
    ballMesh.position.copy(playerGroup.position).add(new THREE.Vector3(0, 0.6, 0));
    scene.add(ballMesh);

    let speed = 0.21 + (power / 100) * 0.23;
    let isGreen = false;

    // Green Release 타이밍 (80% ~ 92%)
    if (power >= 80 && power <= 92) {{
        isGreen = true;
        speed = 0.312; // Perfect trajectory
    }}

    const ballVelocity = dir.clone().multiplyScalar(speed);
    ballVelocity.y += 0.12 + (power / 100) * 0.05;

    activeBalls.push({{
        mesh: ballMesh,
        vel: ballVelocity,
        isGreen: isGreen,
        isScored: false
    }});
}}

function animate() {{
    requestAnimationFrame(animate);

    // 이동
    const moveSpeed = 0.10;
    const rotSpeed = 0.03;

    if (keys.q) playerGroup.rotation.y += rotSpeed;
    if (keys.e) playerGroup.rotation.y -= rotSpeed;

    const moveDir = new THREE.Vector3();
    if (keys.w) moveDir.z -= moveSpeed;
    if (keys.s) moveDir.z += moveSpeed;
    if (keys.a) moveDir.x -= moveSpeed;
    if (keys.d) moveDir.x += moveSpeed;

    moveDir.applyQuaternion(playerGroup.quaternion);
    playerGroup.position.add(moveDir);

    // 점프
    if (keys.space && !isJumping) {{
        jumpVel = 0.14;
        isJumping = true;
    }}
    if (isJumping) {{
        playerPosY += jumpVel;
        jumpVel -= 0.008;
        if (playerPosY <= 1.0) {{
            playerPosY = 1.0;
            isJumping = false;
        }}
    }}
    playerGroup.position.y = playerPosY;

    // 2K Broadcast 카메라 회전 & 트래킹
    const camOffset = new THREE.Vector3(0, 1.1, 0.7).applyQuaternion(playerGroup.quaternion);
    camera.position.copy(playerGroup.position).add(camOffset);
    const lookTarget = playerGroup.position.clone().add(new THREE.Vector3(0, 0.4, -4.5).applyQuaternion(playerGroup.quaternion));
    camera.lookAt(lookTarget);

    // 2K Circular Shot Meter 회전 애니메이션
    if (isCharging) {{
        chargePower = Math.min(100, chargePower + 2.3);
        const angle = (chargePower / 100) * 180 - 90; // -90도에서 90도까지 회전
        meterPointer.style.transform = `translateX(-50%) rotate(${{angle}}deg)`;

        if (chargePower >= 80 && chargePower <= 92) {{
            meterPointer.style.background = '#2ecc71';
        }} else {{
            meterPointer.style.background = '#f39c12';
        }}

        heldBall.position.y = 0.48 + (chargePower / 100) * 0.25;
        handGroup.rotation.x = Math.PI / 3 - (chargePower / 100) * 0.4;
    }} else {{
        handGroup.rotation.x = Math.PI / 3;
    }}

    // 공 물리 & Green Release sound
    for (let i = activeBalls.length - 1; i >= 0; i--) {{
        const b = activeBalls[i];
        b.vel.y -= 0.006;
        b.mesh.position.add(b.vel);

        const pos = b.mesh.position;

        // 백보드 반발
        if (pos.z <= -12.72 && pos.z >= -12.88 && Math.abs(pos.x) < 1.1 && pos.y >= 2.95 && pos.y <= 4.25) {{
            b.vel.z *= -0.65;
            pos.z = -12.70;
        }}

        // 림 반발 (Green Light가 아닐 때)
        const distToRimCenter = Math.hypot(pos.x - rimPos.x, pos.z - rimPos.z);
        if (!b.isGreen && Math.abs(pos.y - rimPos.y) < 0.15 && Math.abs(distToRimCenter - rimRadius) < 0.12) {{
            const bounceDir = new THREE.Vector3(pos.x - rimPos.x, 0.2, pos.z - rimPos.z).normalize();
            b.vel.x = bounceDir.x * 0.08;
            b.vel.z = bounceDir.z * 0.08;
            b.vel.y = Math.abs(b.vel.y) * 0.5;
        }}

        // 바닥 튕김
        if (pos.y < 0.22) {{
            pos.y = 0.22;
            b.vel.y *= -0.55;
        }}

        // 득점 및 Green Light 효과음
        if (distToRimCenter < (rimRadius - 0.05) && Math.abs(pos.y - rimPos.y) < 0.18 && b.vel.y < 0 && !b.isScored) {{
            score += 2;
            fgm += 1;
            document.getElementById('score').innerText = score;
            document.getElementById('fgm').innerText = fgm;
            b.isScored = true;

            triggerGreenSplash();
            playGreenGiantSound();
        }}

        if (pos.z < -20 || pos.y < 0) {{
            scene.remove(b.mesh);
            activeBalls.splice(i, 1);
        }}
    }}

    renderer.render(scene, camera);
}}

animate();
</script>
</body>
</html>"""

components.html(game_ultra_html, height=600)
