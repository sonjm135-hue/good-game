import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🏀 3D 1인칭 커리 슛 연습장",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 3D 1인칭 농구 게임 (커리 시점)")
st.caption("화면을 클릭하여 시점을 전환하고, 마우스 왼쪽 클릭으로 슛을 쏴보세요!")

st.markdown("""
| 동작 | 키보드 / 마우스 조작 |
| :--- | :--- |
| **시점 전환** | 게임 화면 클릭 후 **마우스 이동** |
| **이동** | `W`, `A`, `S`, `D` |
| **점프** | `Space` 키 |
| **슛 던지기** | **마우스 왼쪽 버튼 (길게 누를수록 파워 증가)** |
""")

game_1st_person_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background-color: #000; font-family: sans-serif; }
        #canvas-container { width: 100vw; height: 80vh; display: flex; justify-content: center; align-items: center; position: relative; }
        #ui { position: absolute; top: 20px; left: 20px; color: white; font-size: 24px; font-weight: bold; text-shadow: 2px 2px 4px #000; pointer-events: none; }
        #crosshair { position: absolute; top: 50%; left: 50%; width: 10px; height: 10px; border: 2px solid rgba(255,255,255,0.8); border-radius: 50%; transform: translate(-50%, -50%); pointer-events: none; }
        #power-bar-container { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); width: 200px; height: 15px; border: 2px solid #fff; display: none; background: rgba(0,0,0,0.5); }
        #power-bar { width: 0%; height: 100%; background: #e74c3c; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
</head>
<body>
    <div id="canvas-container">
        <div id="ui">🔥 SUCCESS SCORE: <span id="score">0</span></div>
        <div id="crosshair"></div>
        <div id="power-bar-container"><div id="power-bar"></div></div>
    </div>

<script>
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / (window.innerHeight * 0.8), 0.1, 1000);
camera.position.set(0, 2, 8); // 카메라이자 플레이어의 위치

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth * 0.95, window.innerHeight * 0.75);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

// 포인터 락 조작 (1인칭 시점)
const controls = new THREE.PointerLockControls(camera, renderer.domElement);
container.addEventListener('click', () => { controls.lock(); });

// 조명
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 30, 20);
dirLight.castShadow = true;
scene.add(dirLight);

// 코트
const courtGeo = new THREE.BoxGeometry(20, 0.2, 30);
const courtMat = new THREE.MeshStandardMaterial({ color: 0xd35400 });
const court = new THREE.Mesh(courtGeo, courtMat);
court.position.y = 0;
scene.add(court);

// 골대 생성
const rimPos = new THREE.Vector3(0, 3.05, -12); // 표준 골대 높이/위치
const poleGeo = new THREE.CylinderGeometry(0.1, 0.1, 4);
const poleMat = new THREE.MeshStandardMaterial({ color: 0x7f8c8d });
const pole = new THREE.Mesh(poleGeo, poleMat);
pole.position.set(0, 2, -13);
scene.add(pole);

const boardGeo = new THREE.BoxGeometry(1.8, 1.05, 0.1);
const boardMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
const board = new THREE.Mesh(boardGeo, boardMat);
board.position.set(0, 3.5, -12.8);
scene.add(board);

const rimGeo = new THREE.TorusGeometry(0.45, 0.05, 12, 24);
const rimMat = new THREE.MeshStandardMaterial({ color: 0xe74c3c });
const rim = new THREE.Mesh(rimGeo, rimMat);
rim.rotation.x = Math.PI / 2;
rim.position.copy(rimPos);
scene.add(rim);

// 공 객체들
const ballGeo = new THREE.SphereGeometry(0.24, 16, 16);
const ballMat = new THREE.MeshStandardMaterial({ color: 0xe67e22 });

let activeBalls = [];
let score = 0;

// 조작 키
let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
let velocity = new THREE.Vector3();
let canJump = true;

window.addEventListener('keydown', (e) => {
    switch (e.code) {
        case 'KeyW': moveForward = true; break;
        case 'KeyS': moveBackward = true; break;
        case 'KeyA': moveLeft = true; break;
        case 'KeyD': moveRight = true; break;
        case 'Space': if (canJump) velocity.y += 0.15; canJump = false; break;
    }
});

window.addEventListener('keyup', (e) => {
    switch (e.code) {
        case 'KeyW': moveForward = false; break;
        case 'KeyS': moveBackward = false; break;
        case 'KeyA': moveLeft = false; break;
        case 'KeyD': moveRight = false; break;
    }
});

// 슛 게이지
let isCharging = false;
let chargePower = 0;
const powerBarContainer = document.getElementById('power-bar-container');
const powerBar = document.getElementById('power-bar');

window.addEventListener('mousedown', (e) => {
    if (controls.isLocked && e.button === 0) {
        isCharging = true;
        chargePower = 0;
        powerBarContainer.style.display = 'block';
    }
});

window.addEventListener('mouseup', (e) => {
    if (controls.isLocked && isCharging && e.button === 0) {
        shootBall(chargePower);
        isCharging = false;
        powerBarContainer.style.display = 'none';
    }
});

function shootBall(power) {
    const ballMesh = new THREE.Mesh(ballGeo, ballMat);
    
    // 시점 바로 앞에서 발사
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    
    ballMesh.position.copy(camera.position
