import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 Real NBA 3D Basketball Game",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Real NBA 3D 농구 게임")

# 경기장 및 팀 선택
st.sidebar.header("⚙️ NBA 경기장 설정")
team_choice = st.sidebar.selectbox(
    "SELECT HOME ARENA",
    ["CHICAGO BULLS (United Center)", "LA LAKERS (Crypto.com Arena)"]
)

if "LAKERS" in team_choice:
    floor_color = "0xfdb927"
    paint_color = "0x552583"
    arena_name = "CRYPTO.COM ARENA"
else:
    floor_color = "0xc85a17"
    paint_color = "0xce1141"
    arena_name = "UNITED CENTER"

st.markdown("""
### 🎮 NBA 2K Controls
* **이동 (Move)**: `W`, `A`, `S`, `D` — **카메라가 플레이어를 추적합니다.**
* **방향 회전 (Turn)**: `Q` (Left), `E` (Right)
* **점프 (Jump)**: `Space`
* **슛 던지기 (Shoot)**: **`F` 키 또는 마우스 클릭** (누르고 있으면 파워 장전, 떼면 슛!)
* **🔥 득점 효과**: 슛을 넣으면 **"Ho Ho Ho Green Giant!"** 사운드가 출력됩니다!
""")

game_2k_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background-color: #050505; font-family: 'Arial Black', Impact, sans-serif; user-select: none; }}
        #canvas-container {{ width: 100vw; height: 78vh; display: flex; justify-content: center; align-items: center; position: relative; }}
        
        /* 2K Broadcast Scoreboard HUD */
        #scoreboard {{
            position: absolute; top: 20px; left: 20px;
            background: linear-gradient(135deg, rgba(0,0,0,0.85), rgba(20,20,20,0.95));
            border-left: 5px solid #2ecc71; border-radius: 4px; padding: 10px 20px;
            color: #fff; font-size: 20px; letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6); pointer-events: none;
        }}
        #arena-label {{ font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 2px; }}

        /* Green Release Text */
        #splash-text {{
            position: absolute; top: 35%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; font-weight: 900; font-style: italic;
            text-shadow: 0 0 20px #2ecc71, 2px 2px 4px #000;
            color: #2ecc71; opacity: 0; transition: opacity 0.2s ease-in-out;
            pointer-events: none; text-transform: uppercase;
        }}

        /* Shot Meter */
        #meter-container {{
            position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
            width: 240px; height: 16px; background: rgba(0,0,0,0.7);
            border: 2px solid #fff; border-radius: 8px; overflow: hidden; display: none;
        }}
        #meter-bg {{ width: 100%; height: 100%; position: relative; }}
        #meter-green-zone {{ position: absolute; left: 75%; width: 15%; height: 100%; background: #2ecc71; opacity: 0.8; }}
        #meter-fill {{ width: 0%; height: 100%; background: #f39c12; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="scoreboard">
            <div id="arena-label">{arena_name}</div>
            <div>PTS: <span id="score" style="color: #2ecc71;">0</span> | FGM: <span id="fgm">0</span></div>
        </div>
        <div id="splash-text">HO HO HO! GREEN GIANT! 🔥</div>
        <div id="meter-container">
            <div id="meter-bg">
                <div id="meter-green-zone"></div>
                <div id="meter-fill"></div>
            </div>
        </div>
    </div>

<script>
// Green Giant 사운드 Web Audio API 오디오 데이터 (득점 시 바로 재생)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playGreenGiantSound() {{
    const audio = new Audio('https://www.soundboard.com/handler/gettrack.ashx?id=516543'); // Green Giant 음성
    audio.play().catch(() => {{
        // 브라우저 정책 차단 시 오디오 컨텍스트 이용
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.frequency.setValueAtTime(440, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.5);
    }});
}}

const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a0f);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / (window.innerHeight * 0.78), 0.1, 1000);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.75);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// 조명 (경기장 조명)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

const arenaLight = new THREE.SpotLight(0xffffff, 1.3);
arenaLight.position.set(0, 35, 0);
arenaLight.castShadow = true;
scene.add(arenaLight);

// 1. 디테일한 경기장 구현
const courtGeo = new THREE.BoxGeometry(22, 0.2, 32);
const courtMat = new THREE.MeshStandardMaterial({{ color: {floor_color}, roughness: 0.25, metalness: 0.1 }});
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = 0;
court.receiveShadow = true;
scene.add(court);

// 페인트 존
const paintGeo = new THREE.BoxGeometry(5.8, 0.22, 10);
const paintMat = new THREE.MeshStandardMaterial({{ color: {paint_color} }});
const paintArea = new THREE.Mesh(paintGeo, paintMat);
paintArea.position.set(0, 0, -10.5);
paintArea.receiveShadow = true;
scene.add(paintArea);

// 코트 라인 구현
function createCourtLine(w, h, x, z) {{
    const lineGeo = new THREE.PlaneGeometry(w, h);
    const lineMat = new THREE.MeshBasicMaterial({{ color: 0xffffff, side: THREE.DoubleSide }});
    const line = new THREE.Mesh(lineGeo, lineMat);
    line.rotation.x = Math.PI / 2;
    line.position.set(x, 0.12, z);
    scene.add(line);
}}
createCourtLine(21, 0.15, 0, 15.5); // 베이스라인
createCourtLine(0.15, 31, -10.5, 0); // 사이드라인
createCourtLine(0.15, 31, 10.5, 0);

// 2. 디테일한 백보드 및 골대 구현
const rimPos = new THREE.Vector3(0, 3.05, -12);
const rimRadius = 0.45;
const ballRadius = 0.22;

// 기둥
const poleGeo = new THREE.CylinderGeometry(0.12, 0.12, 4.8);
const poleMat = new THREE.MeshStandardMaterial({{ color: 0x222222 }});
const pole = new THREE.Mesh(poleGeo, poleMat);
pole.position.set(0, 2.4, -13.6);
scene.add(pole);

// 백보드 유리판 & 타겟 박스
const boardGroup = new THREE.Group();
const boardGlassGeo = new THREE.BoxGeometry(2.2, 1.3, 0.06);
const boardGlassMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, transparent: true, opacity: 0.75, roughness: 0.1 }});
const boardGlass = new THREE.Mesh(boardGlassGeo, boardGlassMat);

const innerBoxGeo = new THREE.BoxGeometry(0.7, 0.55, 0.08);
const innerBoxMat = new THREE.MeshStandardMaterial({{ color: 0xcc0000 }});
const innerBox = new THREE.Mesh(innerBoxGeo, innerBoxMat);
innerBox.position.set(0, -0.15, 0.01);

boardGroup.add(boardGlass, innerBox);
boardGroup.position.set(0, 3.65, -12.8);
scene.add(boardGroup);

// 림 & 그물
const rimGeo = new THREE.TorusGeometry(rimRadius, 0.04, 12, 24);
const rimMat = new THREE.MeshStandardMaterial({{ color: 0xee3300, roughness: 0.2 }});
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.rotation.x = Math.PI / 2;
rim.position.copy(rimPos);
scene.add(rim);

// 플레이어 3D 모델 그룹
const playerGroup = new THREE.Group();
playerGroup.position.set(0, 1.0, 5);
scene.add(playerGroup);

// 오른손 모델
const skinMat = new THREE.MeshStandardMaterial({{ color: 0xd2b48c, roughness: 0.5 }});
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
const heldBallGeo = new THREE.SphereGeometry(ballRadius, 24, 24);
const heldBallMat = new THREE.MeshStandardMaterial({{ color: 0xe67e22, roughness: 0.4 }});
const heldBall = new THREE.Mesh(heldBallGeo, heldBallMat);
heldBall.position.set(0.3, 0.48, 0.25);
heldBall.castShadow = true;
playerGroup.add(heldBall);

// 키 조작 이벤트 (F 키 슛 추가)
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

const meterContainer = document.getElementById('meter-container');
const meterFill = document.getElementById('meter-fill');
const splashText = document.getElementById('splash-text');

function startCharging() {{
    if (!isCharging) {{
        isCharging = true;
        chargePower = 0;
        meterContainer.style.display = 'block';
    }}
}}

function releaseShoot() {{
    if (isCharging) {{
        shootBall(chargePower);
        isCharging = false;
        meterContainer.style.display = 'none';
        heldBall.visible = false;
        setTimeout(() => {{ heldBall.visible = true; }}, 600);
    }}
}}

function showSplash(text) {{
    splashText.innerText = text;
    splashText.style.opacity = '1';
    setTimeout(() => {{ splashText.style.opacity = '0'; }}, 1500);
}}

function shootBall(power) {{
    const ballMesh = new THREE.Mesh(heldBallGeo, heldBallMat);
    ballMesh.castShadow = true;
    const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(playerGroup.quaternion).normalize();
    
    ballMesh.position.copy(playerGroup.position).add(new THREE.Vector3(0, 0.6, 0));
    scene.add(ballMesh);

    let speed = 0.21 + (power / 100) * 0.23;
    let isGreen = false;

    if (power >= 72 && power <= 90) {{
        isGreen = true;
        speed = 0.31;
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

    // 카메라 추적
    const camOffset = new THREE.Vector3(0, 1.0, 0.6).applyQuaternion(playerGroup.quaternion);
    camera.position.copy(playerGroup.position).add(camOffset);
    const lookTarget = playerGroup.position.clone().add(new THREE.Vector3(0, 0.4, -4.5).applyQuaternion(playerGroup.quaternion));
    camera.lookAt(lookTarget);

    // F키 슛 게이지
    if (isCharging) {{
        chargePower = Math.min(100, chargePower + 2.2);
        meterFill.style.width = chargePower + '%';

        if (chargePower >= 72 && chargePower <= 90) {{
            meterFill.style.background = '#2ecc71';
        }} else {{
            meterFill.style.background = '#f39c12';
        }}

        heldBall.position.y = 0.48 + (chargePower / 100) * 0.25;
        handGroup.rotation.x = Math.PI / 3 - (chargePower / 100) * 0.4;
    }} else {{
        handGroup.rotation.x = Math.PI / 3;
    }}

    // 공 물리 및 득점 효과음
    for (let i = activeBalls.length - 1; i >= 0; i--) {{
        const b = activeBalls[i];
        b.vel.y -= 0.006;
        b.mesh.position.add(b.vel);

        const pos = b.mesh.position;

        // 백보드 충돌
        if (pos.z <= -12.72 && pos.z >= -12.88 && Math.abs(pos.x) < 1.1 && pos.y >= 2.95 && pos.y <= 4.25) {{
            b.vel.z *= -0.65;
            pos.z = -12.70;
        }}

        // 림 충돌
        const distToRimCenter = Math.hypot(pos.x - rimPos.x, pos.z - rimPos.z);
        if (!b.isGreen && Math.abs(pos.y - rimPos.y) < 0.15 && Math.abs(distToRimCenter - rimRadius) < 0.12) {{
            const bounceDir = new THREE.Vector3(pos.x - rimPos.x, 0.2, pos.z - rimPos.z).normalize();
            b.vel.x = bounceDir.x * 0.08;
            b.vel.z = bounceDir.z * 0.08;
            b.vel.y = Math.abs(b.vel.y) * 0.5;
        }}

        // 바닥 충돌
        if (pos.y < 0.22) {{
            pos.y = 0.22;
            b.vel.y *= -0.55;
        }}

        // 득점 판정 & GREEN GIANT 음성 재생
        if (distToRimCenter < (rimRadius - 0.05) && Math.abs(pos.y - rimPos.y) < 0.18 && b.vel.y < 0 && !b.isScored) {{
            score += 2;
            fgm += 1;
            document.getElementById('score').innerText = score;
            document.getElementById('fgm').innerText = fgm;
            b.isScored = true;

            showSplash("HO HO HO! GREEN GIANT! 🔥");
            playGreenGiantSound(); // 득점 음성 출력
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

components.html(game_2k_html, height=600)
