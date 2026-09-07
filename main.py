import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D 어둠 속의 탈출", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: sans-serif; color: white; }
        #canvas-container { width: 100vw; height: 100vh; }
        #ui-overlay {
            position: absolute; top: 15px; left: 15px;
            color: #fff; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px; z-index: 10;
        }
        #instructions {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: rgba(0,0,0,0.85); color: #fff; text-align: center;
            cursor: pointer; z-index: 20;
        }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 6px; height: 6px; background: rgba(255,255,255,0.8);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none; z-index: 10;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div>🔦 손전등: <span id="flashlight-status" style="color: yellow;">ON (F)</span></div>
        <div>📜 미션: <span id="game-status" style="color: #ff4444;">열쇠를 찾으세요 (F키로 습득)</span></div>
    </div>
    <div id="instructions">
        <h1 style="color: #ff3333; font-size: 40px; margin-bottom: 10px;">어둠 속의 탈출</h1>
        <p style="font-size: 22px;"><b>[ 화면을 클릭하면 게임이 시작됩니다 ]</b></p>
        <div style="margin-top: 20px; text-align: left; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px;">
            <p>🎮 <b>W, A, S, D</b> : 이동</p>
            <p>🖱️ <b>마우스</b> : 시점 회전</p>
            <p>🔦 <b>F 키</b> : 손전등 켜기/끄기 & 아이템 습득</p>
            <p>🚪 <b>ESC</b> : 마우스 해제</p>
        </div>
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
        let keyMesh;

        const instructions = document.getElementById('instructions');
        const flashlightStatus = document.getElementById('flashlight-status');
        const gameStatus = document.getElementById('game-status');

        function init() {
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x000000, 0.15);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 손전등
            flashlight = new THREE.SpotLight(0xffffff, 3, 25, Math.PI / 5, 0.5, 1);
            flashlight.castShadow = true;
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            const ambient = new THREE.AmbientLight(0x080808);
            scene.add(ambient);

            // 바닥
            const floorGeo = new THREE.PlaneGeometry(60, 60);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            createWalls();

            // 열쇠 생성
            const keyGeo = new THREE.BoxGeometry(0.4, 0.4, 0.4);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x554400 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(4, 0.5, -8);
            scene.add(keyMesh);

            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);

            // 화면 클릭으로 게임 시작
            instructions.addEventListener('click', () => {
                document.body.requestPointerLock = document.body.requestPointerLock || document.body.mozRequestPointerLock;
                document.body.requestPointerLock();
            });

            document.addEventListener('pointerlockchange', lockChangeAlert, false);

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === document.body) {
                    camera.rotation.y -= e.movementX * 0.0025;
                    camera.rotation.x -= e.movementY * 0.0025;
                    camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));
                }
            });

            window.addEventListener('resize', onWindowResize, false);
            animate();
        }

        function lockChangeAlert() {
            if (document.pointerLockElement === document.body) {
                instructions.style.display = 'none';
            } else {
                instructions.style.display = 'flex';
            }
        }

        function createWalls() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.8 });
            const walls = [
                [0, 2.5, -20, 40, 5, 1],
                [0, 2.5, 20, 40, 5, 1],
                [-20, 2.5, 0, 1, 5, 40],
                [20, 2.5, 0, 1, 5, 40],
                [-5, 2.5, -5, 10, 5, 1],
                [5, 2.5, -10, 1, 5, 15]
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

            // 열쇠 획득
            if (!hasKey && keyMesh) {
                const dist = camera.position.distanceTo(keyMesh.position);
                if (dist < 3.5) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    gameStatus.innerText = "열쇠를 찾았습니다! 탈출하세요!";
                    gameStatus.style.color = "#00ff00";
                }
            }
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
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

            if (moveForward || moveBackward) velocity.z -= direction.z * 50.0 * delta;
            if (moveLeft || moveRight) velocity.x -= direction.x * 50.0 * delta;

            camera.moveForward(-velocity.z * delta);
            camera.moveRight(velocity.x * delta);

            if (keyMesh) keyMesh.rotation.y += 0.02;

            prevTime = time;
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# Streamlit 환경에서 마우스 잠금 및 클릭 이벤트를 수용하도록 높이 설정
components.html(game_html, height=750)
