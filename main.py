import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D 어둠 속의 탈출", layout="wide")

# 게임 메인 HTML 및 Three.js 스크립트
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: sans-serif; color: white; }
        #canvas-container { width: 100vw; height: 100vh; }
        #ui-overlay {
            position: absolute; top: 10px; left: 10px;
            color: #fff; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px;
        }
        #instructions {
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #fff; text-align: center; font-size: 20px;
            background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;
            cursor: pointer;
        }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 8px; height: 8px; background: rgba(255,255,255,0.5);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div> flashlight: <span id="flashlight-status" style="color: yellow;">ON (F)</span></div>
        <div> status: <span id="game-status">Find the Key (F)</span></div>
    </div>
    <div id="instructions">
        <h2>화면을 클릭하여 시작하세요</h2>
        <p><b>W, A, S, D</b>: 이동</p>
        <p><b>마우스</b>: 시점 회전</p>
        <p><b>F</b>: 손전등 켜기/끄기 및 아이템 습득</p>
        <p><b>ESC</b>: 마우스 커서 해제</p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, flashlight;
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let prevTime = performance.now();
        const velocity = new THREE.Vector3();
        const direction = new THREE.Vector3();

        let isFlashlightOn = true;
        let hasKey = false;
        let keyMesh, monsterMesh;

        const instructions = document.getElementById('instructions');
        const flashlightStatus = document.getElementById('flashlight-status');
        const gameStatus = document.getElementById('game-status');

        function init() {
            // 씬 생성
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x000000, 0.15); // 공포 분위기 안개

            // 카메라 생성
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 0); // 플레이어 눈높이

            // 렌더러
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 손전등 (SpotLight)
            flashlight = new THREE.SpotLight(0xffffff, 2, 20, Math.PI / 6, 0.5, 1);
            flashlight.castShadow = true;
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            // 약한 ambient 조명 (완전한 암흑 방지)
            const ambient = new THREE.AmbientLight(0x050505);
            scene.add(ambient);

            // 바닥 생성
            const floorGeo = new THREE.PlaneGeometry(50, 50);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            // 미로 벽 생성
            createWalls();

            // 열쇠 생성
            const keyGeo = new THREE.BoxGeometry(0.3, 0.3, 0.3);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x332200 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(5, 0.5, -10);
            scene.add(keyMesh);

            // 이벤트 리스너 등록
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);
            
            // Pointer Lock (마우스 가두기 및 1인칭 조작)
            instructions.addEventListener('click', () => {
                document.body.requestPointerLock();
            });

            document.addEventListener('pointerlockchange', () => {
                if (document.pointerLockElement === document.body) {
                    instructions.style.display = 'none';
                } else {
                    instructions.style.display = 'block';
                }
            });

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === document.body) {
                    camera.rotation.y -= e.movementX * 0.002;
                    camera.rotation.x -= e.movementY * 0.002;
                    camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));
                }
            });

            animate();
        }

        function createWalls() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.9 });
            const walls = [
                [0, 2.5, -25, 50, 5, 1],
                [0, 2.5, 25, 50, 5, 1],
                [-25, 2.5, 0, 1, 5, 50],
                [25, 2.5, 0, 1, 5, 50],
                [-5, 2.5, -5, 10, 5, 1],
                [5, 2.5, -12, 1, 5, 15]
            ];

            walls.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                wall.castShadow = true;
                wall.receiveShadow = true;
                scene.add(wall);
            });
        }

        function onKeyDown(e) {
            switch (e.code) {
                case 'KeyW': moveForward = true; break;
                case 'KeyS': moveBackward = true; break;
                case 'KeyA': moveLeft = true; break;
                case 'KeyD': moveRight = true; break;
                case 'KeyF': interact(); break;
            }
        }

        function onKeyUp(e) {
            switch (e.code) {
                case 'KeyW': moveForward = false; break;
                case 'KeyS': moveBackward = false; break;
                case 'KeyA': moveLeft = false; break;
                case 'KeyD': moveRight = false; break;
            }
        }

        function interact() {
            // 손전등 토글
            isFlashlightOn = !isFlashlightOn;
            flashlight.visible = isFlashlightOn;
            flashlightStatus.innerText = isFlashlightOn ? "ON (F)" : "OFF (F)";
            flashlightStatus.style.color = isFlashlightOn ? "yellow" : "gray";

            // 열쇠 습득 로직 (가까이 있을 때)
            if (!hasKey && keyMesh) {
                const dist = camera.position.distanceTo(keyMesh.position);
                if (dist < 3) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    gameStatus.innerText = "Key Picked Up! Escape to Door!";
                    gameStatus.style.color = "lime";
                }
            }
        }

        function animate() {
            requestAnimationFrame(animate);

            const time = performance.now();
            const delta = (time - prevTime) / 1000;

            velocity.x -= velocity.x * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;

            direction.z = Number(moveForward) - Number(moveBackward);
            direction.x = Number(moveRight) - Number(moveLeft);
            direction.normalize();

            if (moveForward || moveBackward) velocity.z -= direction.z * 40.0 * delta;
            if (moveLeft || moveRight) velocity.x -= direction.x * 40.0 * delta;

            camera.moveForward(-velocity.z * delta);
            camera.moveRight(velocity.x * delta);

            // 열쇠 회전 효과
            if (keyMesh) keyMesh.rotation.y += 0.02;

            prevTime = time;
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# Streamlit 내에 Fullscreen HTML 렌더링
components.html(game_html, height=800, scrolling=False)
