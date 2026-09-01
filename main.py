import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 NBA 3D Basketball Game",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 NBA 3D 농구 게임")

# 사이드바 경기장 선택
st.sidebar.header("⚙️ 경기장 설정")
court_type = st.sidebar.selectbox(
    "홈 경기장을 선택하세요",
    ["시카고 불스 경기장 (유나이티드 센터)", "LA 레이커스 경기장 (크립토닷컴 아레나)"]
)

if "레이커스" in court_type:
    floor_color = "0xfdb927"
    paint_color = "0x552583"
    bg_color = "0x0a0512"
else:
    floor_color = "0xc85a17"
    paint_color = "0xce1141"
    bg_color = "0x120406"

st.markdown("""
### 🎮 NBA 컨트롤러 조작법
* **이동**: `W` (앞), `S` (뒤), `A` (왼쪽), `D` (오른쪽) — **캐릭터가 움직이면 화면(카메라)이 NBA 게임처럼 함께 따라갑니다.**
* **시점 회전**: `Q` (좌회전), `E` (우회전)
* **점프**: `Space` 키
* **슛 던지기**: **`J` 키 또는 마우스 클릭** (길게 누르고 있으면 슛 폼을 잡으며 게이지가 차오르고, 떼면 슛!)
""")

game_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: sans-serif; user-select: none; }}
        #canvas-container {{ width: 100vw; height: 75vh; display: flex; justify-content: center; align-items: center; position: relative; }}
        #ui {{ position: absolute; top: 15px; left: 20px; color: #fff; font-size: 22px; font-weight: bold; text-shadow: 2px 2px 4px #000; pointer-events: none; }}
        #power-bar-container {{ position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); width: 220px; height: 14px; border: 2px solid #fff; display: none; background: rgba(0,0,0,0.6); border-radius: 7px; overflow: hidden; }}
        #power-bar {{ width: 0%; height: 100%; background: linear-gradient(90deg, #f39c12, #e74c3c); }}
        #guide-text {{ position: absolute; bottom: 10px; color: rgba(255,255,255,0.7); font-size: 14px; pointer-events: none; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="ui">🔥 SCORE: <span id="score">0</span></div>
        <div id="power-bar-container"><div id="power-bar"></div></div>
        <div id="guide-text">WASD: 이동 | Q/E: 시점 회전 | J / 마우스: 슛</div>
    </div>

<script>
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg_color});

// 카메라 설정 (NBA 3인칭/1인칭 추적 카메라)
const camera = new THREE.PerspectiveCamera(65, window.innerWidth / (window.innerHeight * 0.75), 0.1, 1000);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.72);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

// 조명
const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
dirLight.position.set(10, 25, 15);
dirLight.castShadow = true;
scene.add(dirLight);

// 경기장 바닥
const courtGeo = new THREE.BoxGeometry(20, 0.2, 28);
const courtMat = new THREE.MeshStandardMaterial({{ color: {floor_color} }});
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = 0;
scene.add(court);

// 페인트 존
const paintGeo = new THREE.BoxGeometry(5.5, 0.22, 9);
const paintMat = new THREE.MeshStandardMaterial({{ color: {paint_color} }});
const paintArea = new THREE.Mesh(paintGeo, paintMat);
paintArea.position.set(0, 0, -9.5);
scene.add(paintArea);

// 골대
const rimPos = new THREE.Vector3(0, 3.05, -11);
const poleGeo = new THREE.CylinderGeometry(0.1, 0.1, 4.5);
const poleMat = new THREE.MeshStandardMaterial({{ color: 0x333333 }});
const pole = new THREE.Mesh(poleGeo, poleMat);
pole.position.set(0, 2.25, -12.5);
scene.add(pole);

const boardGeo = new THREE.BoxGeometry(1.8, 1.1, 0.08);
const boardMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, transparent: true, opacity: 0.85 }});
const board = new THREE.Mesh(boardGeo, boardMat);
board.position.set(0, 3.5, -11.8);
scene.add(board);

const rimGeo = new THREE.TorusGeometry(0.42, 0.04, 12, 24);
const rimMat = new THREE.MeshStandardMaterial({{ color: 0xdd2c00 }});
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.rotation.x = Math.PI / 2;
rim.position.copy(rimPos);
scene.add(rim);

// 플레이어 캐릭터 그룹 (위치 & 회전)
const playerGroup = new THREE.Group();
playerGroup.position.set(0, 1.0, 5);
scene.add(playerGroup);

// 오른손 & 지닌 농구공
const handGeo = new THREE.CylinderGeometry(0.05, 0.06, 0.5);
const handMat = new THREE.MeshStandardMaterial({{ color: 0x333333 }});
const rightArm = new THREE.Mesh(handGeo, handMat);
rightArm.rotation.z = -Math.PI / 6;
rightArm.rotation.x = Math.PI / 4;
rightArm.position.set(0.3, 0.2, 0.2);
playerGroup.add(rightArm);

const heldBallGeo = new THREE.SphereGeometry(0.22, 16, 16);
const heldBallMat = new THREE.MeshStandardMaterial({{ color: 0xe67e22 }});
const heldBall = new THREE.Mesh(heldBallGeo, heldBallMat);
heldBall.position.set(0.3, 0.45, 0.35);
playerGroup.add(heldBall);

// 키보드 상태 관리
const keys = {{ w: false, a: false, s: false, d: false, q: false, e: false, space: false, shoot: false }};

window.addEventListener('keydown', (evt) => {{
    const k = evt.key.toLowerCase();
    if (k === 'w') keys.w = true;
    if (k === 's') keys.s = true;
    if (k === 'a') keys.a = true;
    if (k === 'd') keys.d = true;
    if (k === 'q') keys.q = true;
    if (k === 'e') keys.e = true;
    if (evt.code === 'Space') keys.space = true;
    if (k === 'j') startCharging();
}});

window.addEventListener('keyup', (evt) => {{
    const k = evt.key.toLowerCase();
    if (k === 'w') keys.w = false;
    if (k === 's') keys.s = false;
    if (k === 'a') keys.a = false;
    if (k === 'd') keys.d = false;
    if (k === 'q') keys.q = false;
    if (k === 'e') keys.e = false;
    if (evt.code === 'Space') keys.space = false;
    if (k === 'j') releaseShoot();
}});

// 마우스 클릭으로도 슛 가능하도록 지원
window.addEventListener('mousedown', () => {{ startCharging(); }});
window.addEventListener('mouseup', () => {{ releaseShoot(); }});

let isCharging = false;
let chargePower = 0;
let playerPosY = 1.0;
let jumpVel = 0;
let isJumping = false;
let activeBalls = [];
let score = 0;

const powerBarContainer = document.getElementById('power-bar-container');
const powerBar = document.getElementById('power-bar');

function startCharging() {{
    if (!isCharging) {{
        isCharging = true;
        chargePower = 0;
        powerBarContainer.style.display = 'block';
    }}
}}

function releaseShoot() {{
    if (isCharging) {{
        shootBall(chargePower);
        isCharging = false;
        powerBarContainer.style.display = 'none';
        heldBall.visible = false;
        setTimeout(() => {{ heldBall.visible = true; }}, 500);
    }}
}}

function shootBall(power) {{
    const ballMesh = new THREE.Mesh(heldBallGeo, heldBallMat);
    
    // 플레이어의 전방 방향 계산
    const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(playerGroup.quaternion).normalize();
    
    ballMesh.position.copy(playerGroup.position).add(new THREE.Vector3(0, 0.5, 0));
    scene.add(ballMesh);

    const speed = 0.20 + (power / 100) * 0.25;
    const ballVelocity = dir.clone().multiplyScalar(speed);
    ballVelocity.y += 0.12 + (power / 100) * 0.06;

    activeBalls.push({{
        mesh: ballMesh,
        vel: ballVelocity,
        isScored: false
    }});
}}

function animate() {{
    requestAnimationFrame(animate);

    // 1. 이동 및 시점 회전 (WASD / QE)
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

    // 2. 점프 처리
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

    // 3. NBA 화면 추적 카메라 (캐릭터 위치와 회전에 맞춰 카메라가 부드럽게 추종)
    const camOffset = new THREE.Vector3(0, 0.8, 0.5).applyQuaternion(playerGroup.quaternion);
    camera.position.copy(playerGroup.position).add(camOffset);
    
    const lookTarget = playerGroup.position.clone().add(
        new THREE.Vector3(0, 0.4, -4).applyQuaternion(playerGroup.quaternion)
    );
    camera.lookAt(lookTarget);

    // 4. 슛 모션 & 게이지
    if (isCharging) {{
        chargePower = Math.min(100, chargePower + 2.5);
        powerBar.style.width = chargePower + '%';
        heldBall.position.y = 0.45 + (chargePower / 100) * 0.25;
        rightArm.rotation.x = Math.PI / 4 - (chargePower / 100) * 0.3;
    }} else {{
        heldBall.position.y = 0.45;
        rightArm.rotation.x = Math.PI / 4;
    }}

    // 5. 공 물리 및 득점 판정
    for (let i = activeBalls.length - 1; i >= 0; i--) {{
        const b = activeBalls[i];
        b.vel.y -= 0.006;
        b.mesh.position.add(b.vel);

        // 바닥 튕김
        if (b.mesh.position.y < 0.22) {{
            b.mesh.position.y = 0.22;
            b.vel.y *= -0.5;
        }}

        // 림 통과 판정
        const distToRim = b.mesh.position.distanceTo(rimPos);
        if (distToRim < 0.48 && b.vel.y < 0 && !b.isScored) {{
            score++;
            document.getElementById('score').innerText = score;
            b.isScored = true;
        }}

        // 경기장 밖 아웃 처리
        if (b.mesh.position.z < -20 || b.mesh.position.y < 0) {{
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

components.html(game_html, height=580)
