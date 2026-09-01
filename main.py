import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 3D 커리 vs 르브론 1v1 배틀",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 3D 스트리트 농구 배틀: 커리 vs 르브론")
st.caption("Three.js 3D 엔진으로 구현된 실시간 2인용 농구 게임!")

st.markdown("""
| 선수 | 3D 캐릭터 | 이동 키 | 슛 키 |
| :--- | :--- | :--- | :--- |
| **🔴 P1 (왼쪽)** | **스테판 커리** | `W`, `A`, `S`, `D` | `F` |
| **🔵 P2 (오른쪽)** | **르브론 제임스** | `↑`, `←`, `↓`, `→` | `Enter` |
""")

game_3d_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: sans-serif; }
        #canvas-container { width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }
        #ui { position: absolute; top: 20px; width: 100%; display: flex; justify-content: space-around; color: white; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 4px #000; pointer-events: none; }
    </style>
    <!-- Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="ui">
        <div id="p1-score">🔥 커리: 0</div>
        <div id="p2-score">👑 르브론: 0</div>
    </div>
    <div id="canvas-container"></div>

<script>
// 1. 씬, 카메라, 렌더러 설정
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 15, 30);
camera.lookAt(0, 5, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(800, 450);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

// 2. 조명 설정
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 30, 20);
dirLight.castShadow = true;
scene.add(dirLight);

// 3. 3D 농구 코트 및 골대 생성
// 코트 바닥
const courtGeo = new THREE.BoxGeometry(30, 0.5, 16);
const courtMat = new THREE.MeshStandardMaterial({ color: 0xd35400 });
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = -0.25;
court.receiveShadow = true;
scene.add(court);

// 골대 생성 함수
function createHoop(x, isLeft) {
    const group = new THREE.Group();
    // 기둥
    const poleGeo = new THREE.CylinderGeometry(0.2, 0.2, 8);
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d });
    const pole = new THREE.Mesh(poleGeo, poleMat);
    pole.position.set(x, 4, 0);
    group.add(pole);

    // 백보드
    const boardGeo = new THREE.BoxGeometry(0.2, 3, 4);
    const boardMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const board = new THREE.Mesh(boardGeo, boardMat);
    board.position.set(x, 7, 0);
    group.add(board);

    // 림 (골대 고리)
    const rimGeo = new THREE.TorusGeometry(1, 0.1, 8, 24);
    const rimMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c });
    const rim = new THREE.Mesh(rimGeo, rimMat);
    rim.rotation.x = Math.PI / 2;
    rim.position.set(isLeft ? x + 1.2 : x - 1.2, 6, 0);
    group.add(rim);

    scene.add(group);
    return rim.position;
}

const leftRimPos = createHoop(-14, true);
const rightRimPos = createHoop(14, false);

// 4. 3D 캐릭터 생성 (커리 & 르브론)
function createPlayer(color) {
    const group = new THREE.Group();
    // 몸통
    const bodyGeo = new THREE.BoxGeometry(1.5, 2, 1);
    const bodyMat = new THREE.MeshStandardMaterial({ color: color });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 1;
    body.castShadow = true;
    group.add(body);

    // 머리
    const headGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
    const headMat = new THREE.MeshStandardMaterial({ color: 0xffdbac });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 2.6;
    head.castShadow = true;
    group.add(head);

    scene.add(group);
    return group;
}

const p1Mesh = createPlayer(0xf1c40f); // 커리 (골든스테이트 노란색)
const p2Mesh = createPlayer(0x551a8b); // 르브론 (레이커스 보라색)

// 5. 3D 농구공 생성
const ballGeo = new THREE.SphereGeometry(0.6, 16, 16);
const ballMat = new THREE.MeshStandardMaterial({ color: 0xe67e22 });
const ballMesh = new THREE.Mesh(ballGeo, ballMat);
ballMesh.castShadow = true;
scene.add(ballMesh);

// 게임 데이터 상태
let p1 = { x: -8, y: 0, z: 0, vx: 0, vy: 0, vz: 0, score: 0, mesh: p1Mesh };
let p2 = { x: 8, y: 0, z: 0, vx: 0, vy: 0, vz: 0, score: 0, mesh: p2Mesh };
let ball = { x: 0, y: 5, z: 0, vx: 0, vy: 0, vz: 0, holder: null, mesh: ballMesh };

const gravity = -0.015;
const speed = 0.15;
const jump = 0.35;

const keys = {};
window.addEventListener('keydown', e => { 
    keys[e.key] = true; 
    if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Enter"].indexOf(e.key) > -1) e.preventDefault();
});
window.addEventListener('keyup', e => { keys[e.key] = false; });

// 6. 물리 및 게임 루프
function update() {
    // P1 (커리) WASD 이동
    p1.vx = 0; p1.vz = 0;
    if (keys['a'] || keys['A']) p1.vx = -speed;
    if (keys['d'] || keys['D']) p1.vx = speed;
    if (keys['w'] || keys['W']) p1.vz = -speed;
    if (keys['s'] || keys['S']) p1.vz = speed;
    if ((keys['f'] || keys['F']) && p1.y <= 0 && ball.holder === p1) shootBall(p1, 1);

    // P2 (르브론) 화살표 이동
    p2.vx = 0; p2.vz = 0;
    if (keys['ArrowLeft']) p2.vx = -speed;
    if (keys['ArrowRight']) p2.vx = speed;
    if (keys['ArrowUp']) p2.vz = -speed;
    if (keys['ArrowDown']) p2.vz = speed;
    if (keys['Enter'] && p2.y <= 0 && ball.holder === p2) shootBall(p2, -1);

    // 위치 업데이트 및 3D 매핑
    [p1, p2].forEach(p => {
        p.x += p.vx;
        p.z += p.vz;
        // 코트 경계 제한
        p.x = Math.max(-13, Math.min(13, p.x));
        p.z = Math.max(-6, Math.min(6, p.z));

        p.mesh.position.set(p.x, p.y, p.z);
    });

    // 공 물리
    if (ball.holder) {
        ball.x = ball.holder.x;
        ball.y = ball.holder.y + 2;
        ball.z = ball.holder.z;
    } else {
        ball.vy += gravity;
        ball.x += ball.vx;
        ball.y += ball.vy;
        ball.z += ball.vz;

        // 바닥 바운드
        if (ball.y < 0.6) {
            ball.y = 0.6;
            ball.vy *= -0.6;
        }

        // 공 소유 판정
        [p1, p2].forEach(p => {
            let dist = Math.hypot(p.x - ball.x, p.z - ball.z);
            if (dist < 1.8 && Math.abs(p.y - ball.y) < 2) {
                ball.holder = p;
            }
        });

        // 득점 판정
        if (ball.vy < 0) {
            if (Math.hypot(ball.x - leftRimPos.x, ball.z - leftRimPos.z) < 1.5 && Math.abs(ball.y - leftRimPos.y) < 1) {
                p2.score += 2;
                document.getElementById('p2-score').innerText = `👑 르브론: ${p2.score}`;
                resetBall();
            }
            if (Math.hypot(ball.x - rightRimPos.x, ball.z - rightRimPos.z) < 1.5 && Math.abs(ball.y - rightRimPos.y) < 1) {
                p1.score += 2;
                document.getElementById('p1-score').innerText = `🔥 커리: ${p1.score}`;
                resetBall();
            }
        }
    }

    ball.mesh.position.set(ball.x, ball.y, ball.z);
}

function shootBall(player, dir) {
    ball.holder = null;
    ball.vx = dir * 0.3;
    ball.vy = 0.45;
    ball.vz = (0 - player.z) * 0.05;
}

function resetBall() {
    ball.holder = null;
    ball.x = 0; ball.y = 6; ball.z = 0;
    ball.vx = 0; ball.vy = 0; ball.vz = 0;
}

function animate() {
    requestAnimationFrame(animate);
    update();
    renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
"""

components.html(game_3d_html, height=500)
