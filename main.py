import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 NBA 2K Streamlit Edition",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 NBA 2K Streamlit Edition")

# 경기장 및 팀 선택
st.sidebar.header("⚙️ NBA 2K Game Settings")
team_choice = st.sidebar.selectbox(
    "SELECT HOME ARENA",
    ["LA LAKERS (Crypto.com Arena)", "CHICAGO BULLS (United Center)"]
)

if "LAKERS" in team_choice:
    floor_color = "0xfdb927"
    paint_color = "0x552583"
    accent_color = "0xfdb927"
    arena_name = "CRYPTO.COM ARENA"
else:
    floor_color = "0xc85a17"
    paint_color = "0xce1141"
    accent_color = "0xd80027"
    arena_name = "UNITED CENTER"

st.markdown("""
### 🎮 NBA 2K Controls
* **이동 (Move)**: `W`, `A`, `S`, `D` — **2K 방송 카메라가 캐릭터를 다이나믹하게 트래킹합니다.**
* **방향 회전 (Turn)**: `Q` (Left), `E` (Right)
* **점프 (Jump)**: `Space`
* **2K 릴리즈 슛 (Shot Release)**: **`J` 키 또는 마우스 클릭**
  * **🎯 Green Release Tip**: 게이지가 **초록색 타이밍 존(80~95%)**에 도달했을 때 손을 떼면 **EXCELLENT RELEASE (클린 슛)**가 발동합니다!
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
            border-left: 5px solid #f39c12; border-radius: 4px; padding: 10px 20px;
            color: #fff; font-size: 20px; letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6); pointer-events: none;
        }}
        #arena-label {{ font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 2px; }}

        /* 2K Perfect Release Splash Overlay */
        #splash-text {{
            position: absolute; top: 35%; left: 50%; transform: translate(-50%, -50%);
            font-size: 42px; font-weight: 900; font-style: italic;
            text-shadow: 0 0 20px #2ecc71, 2px 2px 4px #000;
            color: #2ecc71; opacity: 0; transition: opacity 0.2s ease-in-out;
            pointer-events: none; text-transform: uppercase;
        }}

        /* 2K Player Feet Shot Meter */
        #meter-container {{
            position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
            width: 240px; height: 16px; background: rgba(0,0,0,0.7);
            border: 2px solid #fff; border-radius: 8px; overflow: hidden; display: none;
        }}
        #meter-bg {{ width: 100%; height: 100%; position: relative; }}
        #meter-green-zone {{ position: absolute; left: 75%; width: 15%; height: 100%; background: #2ecc71; opacity: 0.8; }}
        #meter-fill {{ width: 0%; height: 100%; background: #f39c12; transition: background 0.1s; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="scoreboard">
            <div id="arena-label">{arena_name}</div>
            <div>PTS: <span id="score" style="color: #f1c40f;">0</span> | FGM: <span id="fgm">0</span></div>
        </div>
        <div id="splash-text">GREEN RELEASE! 🔥</div>
        <div id="meter-container">
            <div id="meter-bg">
                <div id="meter-green-zone"></div>
                <div id="meter-fill"></div>
            </div>
        </div>
    </div>

<script>
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050508);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / (window.innerHeight * 0.78), 0.1, 1000);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.75);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// 조명 (2K 조명 셋업)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const arenaLight = new THREE.SpotLight(0xffffff, 1.2);
arenaLight.position.set(0, 30, 0);
arenaLight.castShadow = true;
arenaLight.shadow.mapSize.width = 1024;
arenaLight.shadow.mapSize.height = 1024;
scene.add(arenaLight);

// 경기장 & 라인
const courtGeo = new THREE.BoxGeometry(22, 0.2, 32);
const courtMat = new THREE.MeshStandardMaterial({{ color: {floor_color}, roughness: 0.3, metalness: 0.1 }});
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = 0;
court.receiveShadow = true;
scene.add(court);

const paintGeo = new THREE.BoxGeometry(5.8, 0.22, 10);
const paintMat = new THREE.MeshStandardMaterial({{ color: {paint_color} }});
const paintArea = new THREE.Mesh(paintGeo, paintMat);
paintArea.position.set(0, 0, -10.5);
paintArea.receiveShadow = true;
scene.add(paintArea);

// 골대 및 백보드
const rimPos = new THREE.Vector3(0, 3.05, -12);
const rimRadius = 0.45;
const ballRadius = 0.22;

const poleGeo = new THREE.CylinderGeometry(0.12, 0.12, 4.8);
const poleMat = new THREE.MeshStandardMaterial({{ color: 0x222222 }});
const pole = new THREE.Mesh(poleGeo, poleMat);
pole.position.set(0, 2.4, -13.6);
scene.add(pole);

const boardGeo = new THREE.BoxGeometry(1.9, 1.15, 0.08);
const boardMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, transparent: true, opacity: 0.85 }});
const board = new THREE.Mesh(boardGeo, boardMat);
board.position.set(0, 3.6, -12.8);
scene.add(board);

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

// 디테일 팔 & 손
const skinMat = new THREE.MeshStandardMaterial({{ color: 0xd2b48c, roughness: 0.5 }});
const handGroup = new THREE.Group();

const armGeo = new THREE.CylinderGeometry(0.06, 0.08, 0.45);
const armMesh = new THREE.Mesh(armGeo, skinMat);
handGroup.add(armMesh);

const palmGeo = new THREE.BoxGeometry(0.12, 0.15, 0.05);
const palmMesh = new THREE.Mesh(palmGeo, skinMat);
palmMesh.position.set(0, 0.25, 0);
handGroup.add(palmMesh);

function createFinger(x, y, z, rotZ) {{
    const fGeo = new THREE.CylinderGeometry(0.018, 0.015, 0.1);
    const fMesh = new THREE.Mesh(fGeo, skinMat);
    fMesh.position.set(x, y, z);
    fMesh.rotation.z = rotZ;
    return fMesh;
}}
handGroup.add(
    createFinger(-0.06, 0.22, 0.02, Math.PI/4),
    createFinger(-0.03, 0.35, 0.01, -0.05),
    createFinger(0, 0.36, 0, 0),
    createFinger(0.03, 0.34, 0, 0.05),
    createFinger(0.06, 0.31, -0.01, 0.1)
);

handGroup.position.set(0.3, 0.1, 0.2);
handGroup.rotation.x = Math.PI / 3;
playerGroup.add(handGroup);

// 농구공 Mesh
const heldBallGeo = new THREE.SphereGeometry(ballRadius, 24, 24);
const heldBallMat = new THREE.MeshStandardMaterial({{ color: 0xe67e22, roughness: 0.4 }});
const heldBall = new THREE.Mesh(heldBallGeo, heldBallMat);
heldBall.position.set(0.3, 0.48, 0.25);
heldBall.castShadow = true;
playerGroup.add(heldBall);

// 키 조작 이벤트
const keys = {{ w: false, a: false, s: false, d: false, q: false, e: false, space: false }};

window.addEventListener('keydown', (evt) => {{
    const k = evt.key.toLowerCase();
    if (k in keys) keys[k] = true;
    if (evt.code === 'Space') keys.space = true;
    if (k === 'j') startCharging();
}});

window.addEventListener('keyup', (evt) => {{
    const k = evt.key.toLowerCase();
    if (k in keys) keys[k] = false;
    if (evt.code === 'Space') keys.space = false;
    if (k === 'j') releaseShoot();
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
let dribbleTime = 0;

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

function showSplash(text, color) {{
    splashText.innerText = text;
    splashText.style.color = color;
    splashText.style.opacity = '1';
    setTimeout(() => {{ splashText.style.opacity = '0'; }}, 1200);
}}

function shootBall(power) {{
    const ballMesh = new THREE.Mesh(heldBallGeo, heldBallMat);
    ballMesh.castShadow = true;
    const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(playerGroup.quaternion).normalize();
    
    ballMesh.position.copy(playerGroup.position).add(new THREE.Vector3(0, 0.6, 0));
    scene.add(ballMesh);

    let speed = 0.21 + (power / 100) * 0.23;
    let isGreen = false;

    // 2K Green Release 판정 (75% ~ 90% 사이라고 가늠)
    if (power >= 75 && power <= 90) {{
        isGreen = true;
        speed = 0.31; // 완벽한 궤적 파워
        showSplash("GREEN RELEASE! 🔥", "#2ecc71");
    }} else if (power < 50) {{
        showSplash("EARLY RELEASE ⚠️", "#e74c3c");
    }} else {{
        showSplash("LATE RELEASE ⚠️", "#e74c3c");
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

    // 1. 이동 및 드리블 애니메이션
    const moveSpeed = 0.10;
    const rotSpeed = 0.03;
    let isMoving = false;

    if (keys.q) playerGroup.rotation.y += rotSpeed;
    if (keys.e) playerGroup.rotation.y -= rotSpeed;

    const moveDir = new THREE.Vector3();
    if (keys.w) {{ moveDir.z -= moveSpeed; isMoving = true; }}
    if (keys.s) {{ moveDir.z += moveSpeed; isMoving = true; }}
    if (keys.a) {{ moveDir.x -= moveSpeed; isMoving = true; }}
    if (keys.d) {{ moveDir.x += moveSpeed; isMoving = true; }}

    moveDir.applyQuaternion(playerGroup.quaternion);
    playerGroup.position.add(moveDir);

    // 드리블 바운스 모션
    if (isMoving && !isCharging && !isJumping) {{
        dribbleTime += 0.2;
        heldBall.position.y = 0.48 + Math.abs(Math.sin(dribbleTime)) * 0.2;
    }} else if (!isCharging) {{
        heldBall.position.y = 0.48;
    }}

    // 2. 점프
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

    // 3. 2K 방송 트래킹 카메라
    const camOffset = new THREE.Vector3(0, 1.0, 0.6).applyQuaternion(playerGroup.quaternion);
    camera.position.copy(playerGroup.position).add(camOffset);
    const lookTarget = playerGroup.position.clone().add(new THREE.Vector3(0, 0.4, -4.5).applyQuaternion(playerGroup.quaternion));
    camera.lookAt(lookTarget);

    // 4. 2K 슈팅 게이지
    if (isCharging) {{
        chargePower = Math.min(100, chargePower + 2.2);
        meterFill.style.width = chargePower + '%';

        if (chargePower >= 75 && chargePower <= 90) {{
            meterFill.style.background = '#2ecc71'; // Green zone
        }} else {{
            meterFill.style.background = '#f39c12';
        }}

        heldBall.position.y = 0.48 + (chargePower / 100) * 0.25;
        handGroup.rotation.x = Math.PI / 3 - (chargePower / 100) * 0.4;
    }} else {{
        handGroup.rotation.x = Math.PI / 3;
    }}

    // 5. 공 물리, 리바운드 & 득점 판정
    for (let i = activeBalls.length - 1; i >= 0; i--) {{
        const b = activeBalls[i];
        b.vel.y -= 0.006;
        b.mesh.position.add(b.vel);

        const pos = b.mesh.position;

        // 백보드 반발
        if (pos.z <= -12.72 && pos.z >= -12.88 && Math.abs(pos.x) < 0.95 && pos.y >= 2.95 && pos.y <= 4.10) {{
            b.vel.z *= -0.6;
            pos.z = -12.70;
        }}

        // 림 테두리 반발 (Green Release가 아닐 때만 튕김 발생)
        const distToRimCenter = Math.hypot(pos.x - rimPos.x, pos.z - rimPos.z);
        if (!b.isGreen && Math.abs(pos.y - rimPos.y) < 0.15 && Math.abs(distToRimCenter - rimRadius) < 0.12) {{
            const bounceDir = new THREE.Vector3(pos.x - rimPos.x, 0.2, pos.z - rimPos.z).normalize();
            b.vel.x = bounceDir.x * 0.08;
            b.vel.z = bounceDir.z * 0.08;
            b.vel.y = Math.abs(b.vel.y) * 0.5;
        }}

        // 바닥 바운드
        if (pos.y < 0.22) {{
            pos.y = 0.22;
            b.vel.y *= -0.55;
        }}

        // 득점 판정
        if (distToRimCenter < (rimRadius - 0.05) && Math.abs(pos.y - rimPos.y) < 0.18 && b.vel.y < 0 && !b.isScored) {{
            score += 2;
            fgm += 1;
            document.getElementById('score').innerText = score;
            document.getElementById('fgm').innerText = fgm;
            b.isScored = true;
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
