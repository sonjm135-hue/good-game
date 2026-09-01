import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 3D 1인칭 커리 농구 게임",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 3D 1인칭 농구 게임 (커리 시점)")

# 사이드바에서 경기장 선택 기능
st.sidebar.header("⚙️ 경기장 설정")
court_type = st.sidebar.selectbox(
    "홈 경기장을 선택하세요",
    ["시카고 불스 경기장 (유나이티드 센터)", "LA 레이커스 경기장 (크립토닷컴 아레나)"]
)

# 선택한 경기장에 따른 색상 구성
if "레이커스" in court_type:
    floor_color = "0xfdb927"  # 레이커스 골드
    paint_color = "0x552583"  # 레이커스 보라
    bg_color = "0x110822"
else:
    floor_color = "0xc85a17"  # 불스 우드톤
    paint_color = "0xce1141"  # 불스 레드
    bg_color = "0x1a0508"

st.caption("화면을 클릭하여 시점을 고정한 후 마우스와 키보드로 플레이하세요!")

st.markdown("""
| 동작 | 키보드 / 마우스 조작 |
| :--- | :--- |
| **시점 전환** | 게임 화면 클릭 후 **마우스 이동** (캐릭터 움직임에 따라 시점 동시 이동) |
| **이동** | `W`, `A`, `S`, `D` |
| **점프** | `Space` 키 |
| **슛 던지기** | **마우스 왼쪽 버튼 (누르고 있으면 손과 공을 모으고, 떼면 슛!)** |
""")

game_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: sans-serif; }}
        #canvas-container {{ width: 100vw; height: 80vh; display: flex; justify-content: center; align-items: center; position: relative; }}
        #ui {{ position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 4px #000; pointer-events: none; }}
        #crosshair {{ position: absolute; top: 50%; left: 50%; width: 8px; height: 8px; border: 2px solid rgba(255,255,255,0.8); border-radius: 50%; transform: translate(-50%, -50%); pointer-events: none; }}
        #power-bar-container {{ position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); width: 200px; height: 12px; border: 2px solid #fff; display: none; background: rgba(0,0,0,0.5); border-radius: 6px; overflow: hidden; }}
        #power-bar {{ width: 0%; height: 100%; background: #f39c12; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="ui">🔥 득점 점수: <span id="score">0</span></div>
        <div id="crosshair"></div>
        <div id="power-bar-container"><div id="power-bar"></div></div>
    </div>

<script>
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color({bg_color});

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / (window.innerHeight * 0.8), 0.1, 1000);
camera.position.set(0, 1.8, 8);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.75);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

const controls = new THREE.PointerLockControls(camera, renderer.domElement);
container.addEventListener('click', () => {{ controls.lock(); }});

// 조명 설정
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 30, 20);
dirLight.castShadow = true;
scene.add(dirLight);

// 경기장 생성
const courtGeo = new THREE.BoxGeometry(22, 0.2, 32);
const courtMat = new THREE.MeshStandardMaterial({{ color: {floor_color} }});
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = 0;
scene.add(court);

// 페인트 존 (선택한 팀 페인트 구역)
const paintGeo = new THREE.BoxGeometry(6, 0.22, 10);
const paintMat = new THREE.MeshStandardMaterial({{ color: {paint_color} }});
const paintArea = new THREE.Mesh(paintGeo, paintMat);
paintArea.position.set(0, 0, -11);
scene.add(paintArea);

// 골대 생성
const rimPos = new THREE.Vector3(0, 3.05, -12);
const poleGeo = new THREE.CylinderGeometry(0.12, 0.12, 4.5);
const poleMat = new THREE.MeshStandardMaterial({{ color: 0x333333 }});
const pole = new THREE.Mesh(poleGeo, poleMat);
pole.position.set(0, 2.25, -13.5);
scene.add(pole);

const boardGeo = new THREE.BoxGeometry(2.0, 1.2, 0.1);
const boardMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, transparent: true, opacity: 0.85 }});
const board = new THREE.Mesh(boardGeo, boardMat);
board.position.set(0, 3.6, -12.8);
scene.add(board);

const rimGeo = new THREE.TorusGeometry(0.45, 0.05, 12, 24);
const rimMat = new THREE.MeshStandardMaterial({{ color: 0xe74c3c }});
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.rotation.x = Math.PI / 2;
rim.position.copy(rimPos);
scene.add(rim);

// 1인칭 오른손 & 농구공 mesh (카메라 자식 요소로 등록하여 시점 따라 이동)
const handGroup = new THREE.Group();

// 오른팔 & 손
const handGeo = new THREE.CylinderGeometry(0.06, 0.08, 0.6);
const handMat = new THREE.MeshStandardMaterial({{ color: 0xd2b48c }});
const rightHand = new THREE.Mesh(handGeo, handMat);
rightHand.rotation.z = -Math.PI / 6;
rightHand.rotation.x = Math.PI / 3;
rightHand.position.set(0.35, -0.3, -0.6);
handGroup.add(rightHand);

// 지니고 있는 농구공
const heldBallGeo = new THREE.SphereGeometry(0.24, 16, 16);
const heldBallMat = new THREE.MeshStandardMaterial({{ color: 0xe67e22 }});
const heldBall = new THREE.Mesh(heldBallGeo, heldBallMat);
heldBall.position.set(0.3, -0.1, -0.6);
handGroup.add(heldBall);

camera.add(handGroup);
scene.add(camera);

// 게임 로직 데이터
let activeBalls = [];
let score = 0;
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
let velocity = new THREE.Vector3();
let canJump = true;

window.addEventListener('keydown', (e) => {{
    switch (e.code) {{
        case 'KeyW': moveForward = true; break;
        case 'KeyS': moveBackward = true; break;
        case 'KeyA': moveLeft = true; break;
        case 'KeyD': moveRight = true; break;
        case 'Space': if (canJump) {{ velocity.y += 0.16; canJump = false; }} break;
    }}
}});

window.addEventListener('keyup', (e) => {{
    switch (e.code) {{
        case 'KeyW': moveForward = false; break;
        case 'KeyS': moveBackward = false; break;
        case 'KeyA': moveLeft = false; break;
        case 'KeyD': moveRight = false; break;
    }}
}});

let isCharging = false;
let chargePower = 0;
const powerBarContainer = document.getElementById('power-bar-container');
const powerBar = document.getElementById('power-bar');

window.addEventListener('mousedown', (e) => {{
    if (controls.isLocked && e.button === 0) {{
        isCharging = true;
        chargePower = 0;
        powerBarContainer.style.display = 'block';
    }}
}});

window.addEventListener('mouseup', (e) => {{
    if (controls.isLocked && isCharging && e.button === 0) {{
        shootBall(chargePower);
        isCharging = false;
        powerBarContainer.style.display = 'none';
        
        // 슛 동작 후 손과 공 위치 복귀
        handGroup.position.set(0, 0, 0);
        heldBall.visible = true;
    }}
}});

function shootBall(power) {{
    heldBall.visible = false; // 던진 직후 지닌 공 숨김

    const ballMesh = new THREE.Mesh(heldBallGeo, heldBallMat);
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    
    // 슛 위치
    ballMesh.position.copy(camera.position).add(dir.clone().multiplyScalar(0.6));
    scene.add(ballMesh);

    const speed = 0.22 + (power / 100) * 0.28;
    const ballVelocity = dir.clone().multiplyScalar(speed);
    ballVelocity.y += 0.09 + (power / 100) * 0.05;

    activeBalls.push({{
        mesh: ballMesh,
        vel: ballVelocity,
        isScored: false
    }});

    // 0.4초 후 들고있는 공 재출현
    setTimeout(() => {{ heldBall.visible = true; }}, 400);
}}

function animate() {{
    requestAnimationFrame(animate);

    // 슛 모으기 애니메이션 (손과 공이 머리 위 슛 폼 위치로 들어올려짐)
    if (isCharging) {{
        chargePower = Math.min(100, chargePower + 2.2);
        powerBar.style.width = chargePower + '%';

        const liftAmount = (chargePower / 100) * 0.2;
        handGroup.position.y = liftAmount;
        handGroup.position.z = -liftAmount * 0.5;
    }} else {{
        handGroup.position.y *= 0.8;
        handGroup.position.z *= 0.8;
    }}

    // 이동 처리 및 카메라/시점 동시 이동
    if (controls.isLocked) {{
        velocity.x -= velocity.x * 0.1;
        velocity.z -= velocity.z * 0.1;
        velocity.y -= 0.008;

        if (moveForward) velocity.z += 0.015;
        if (moveBackward) velocity.z -= 0.015;
        if (moveLeft) velocity.x -= 0.015;
        if (moveRight) velocity.x += 0.015;

        controls.moveRight(velocity.x);
        controls.moveForward(velocity.z);
        camera.position.y += velocity.y;

        if (camera.position.y < 1.8) {{
            velocity.y = 0;
            camera.position.y = 1.8;
            canJump = true;
        }}
    }}

    // 날아가는 공 물리
    for (let i = activeBalls.length - 1; i >= 0; i--) {{
        const b = activeBalls[i];
        b.vel.y -= 0.006;
        b.mesh.position.add(b.vel);

        if (b.mesh.position.y < 0.24) {{
            b.mesh.position.y = 0.24;
            b.vel.y *= -0.55;
        }}

        const distToRim = b.mesh.position.distanceTo(rimPos);
        if (distToRim < 0.5 && b.vel.y < 0 && !b.isScored) {{
            score++;
            document.getElementById('score').innerText = score;
            b.isScored = true;
        }}

        if (b.mesh.position.z < -22 || b.mesh.position.y < 0) {{
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

components.html(game_html, height=560)
