import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="폐가 탈출: 살인마의 집", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: sans-serif; color: white; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; cursor: crosshair; }
        #ui-overlay {
            position: absolute; top: 15px; left: 15px;
            color: #fff; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px; z-index: 10;
        }
        #start-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: rgba(0,0,0,0.92); color: #fff; text-align: center; z-index: 20;
        }
        #start-btn {
            margin-top: 20px; padding: 15px 40px; font-size: 24px; font-weight: bold;
            color: #fff; background-color: #b71c1c; border: none; border-radius: 8px;
            cursor: pointer; transition: 0.2s;
        }
        #start-btn:hover { background-color: #ff1744; }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 8px; height: 8px; background: rgba(255,255,255,0.8);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none; z-index: 10;
        }
        #jumpscare-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: red; display: none; justify-content: center; align-items: center;
            flex-direction: column; z-index: 30; animation: flash 0.1s infinite;
        }
        @keyframes flash {
            0% { background-color: #ff0000; }
            50% { background-color: #000000; }
            100% { background-color: #550000; }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div>🔦 손전등: <span id="flashlight-status" style="color: yellow;">ON (F)</span></div>
        <div>📜 미션: <span id="game-status" style="color: #ff4444;">열쇠를 찾아 탈출하세요 (F키로 습득)</span></div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #ff3333; font-size: 45px; margin-bottom: 10px;">🏚️ 폐가 탈출: 살인마의 집</h1>
        <p style="font-size: 18px; color: #ccc; max-width: 550px; line-height: 1.6;">
            폐가를 탐방하던 중 출구 문이 쾅 닫히며 잠겼습니다.<br>
            어둠 속에서 살인마가 당신을 쫓아옵니다!
        </p>
        <button id="start-btn">게임 시작하기</button>
        <div style="margin-top: 25px; text-align: left; background: rgba(255,255,255,0.08); padding: 18px; border-radius: 8px; font-size: 15px;">
            <p style="margin: 5px 0;">🎮 <b>W, A, S, D</b> : 이동</p>
            <p style="margin: 5px 0;">🖱️ <b>마우스 이동</b> : 화면 회전</p>
            <p style="margin: 5px 0;">🔦 <b>F 키</b> : 손전등 ON/OFF & 열쇠 습득</p>
        </div>
    </div>

    <div id="jumpscare-overlay">
        <h1 style="font-size: 70px; color: black; text-shadow: 0 0 20px white;">😱 으아악!</h1>
        <h2 style="font-size: 35px; color: white;">살인마에게 잡혔습니다...</h2>
        <p style="font-size: 20px; color: yellow; margin-top: 15px;">새로그물(F5)을 눌러 다시 도전하세요.</p>
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
        let gameStarted = false;
        let gameOver = false;
        let gameClear = false;

        let keyMesh, doorMesh, killerMesh;
        let killerSpeed = 2.8;

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const flashlightStatus = document.getElementById('flashlight-status');
        const gameStatus = document.getElementById('game-status');
        const jumpscareOverlay = document.getElementById('jumpscare-overlay');

        let mouseX = 0, mouseY = 0;

        function init() {
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x000000, 0.18);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 8);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 손전등
            flashlight = new THREE.SpotLight(0xffffff, 4, 20, Math.PI / 5, 0.5, 1);
            flashlight.castShadow = true;
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            const ambient = new THREE.AmbientLight(0x050505);
            scene.add(ambient);

            // 바닥
            const floorGeo = new THREE.PlaneGeometry(30, 30);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x1a110b, roughness: 0.9 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            createHouse();

            // 황금 열쇠
            const keyGeo = new THREE.BoxGeometry(0.35, 0.35, 0.35);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x554400 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(10, 0.4, -10);
            scene.add(keyMesh);

            // 출구 문
            const doorGeo = new THREE.BoxGeometry(2, 3.5, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x550000 });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 1.75, 14.8);
            scene.add(doorMesh);

            // 살인마
            const killerGeo = new THREE.BoxGeometry(1, 2.2, 1);
            const killerMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
            killerMesh = new THREE.Mesh(killerGeo, killerMat);
            
            const eyeGeo = new THREE.BoxGeometry(0.2, 0.1, 0.1);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const eye1 = new THREE.Mesh(eyeGeo, eyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, eyeMat);
            eye1.position.set(-0.25, 0.7, -0.5);
            eye2.position.set(0.25, 0.7, -0.5);
            killerMesh.add(eye1);
            killerMesh.add(eye2);

            killerMesh.position.set(-10, 1.1, -10);
            scene.add(killerMesh);

            // 이벤트 등록
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);

            // 시작 버튼 클릭
            startBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                startScreen.style.display = 'none';
                gameStarted = true;
            });

            // 마우스 이동 시 시점 회전 (PointerLock 제한 회피 방식)
            document.addEventListener('mousemove', (e) => {
                if (!gameStarted || gameOver) return;
                
                const movementX = e.movementX || 0;
                const movementY = e.movementY || 0;

                camera.rotation.y -= movementX * 0.003;
                camera.rotation.x -= movementY * 0.003;
                camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));
            });

            animate();
        }

        function createHouse() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.9 });
            const walls = [
                [0, 2.5, -15, 30, 5, 0.5],
                [0, 2.5, 15, 30, 5, 0.5],
                [-15, 2.5, 0, 0.5, 5, 30],
                [15, 2.5, 0, 0.5, 5, 30],
                [-5, 2.5, 0, 10, 5, 0.5],
                [5, 2.5, -5, 0.5, 5, 15]
            ];

            walls.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                scene.add(wall);
            });
        }

        function onKeyDown(e) {
            if (!gameStarted || gameOver) return;
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
            if (gameOver || gameClear) return;

            // 손전등 Toggle
            isFlashlightOn = !isFlashlightOn;
            flashlight.visible = isFlashlightOn;
            flashlightStatus.innerText = isFlashlightOn ? "ON (F)" : "OFF (F)";
            flashlightStatus.style.color = isFlashlightOn ? "yellow" : "gray";

            // 열쇠 습득
            if (!hasKey && keyMesh) {
                const distKey = camera.position.distanceTo(keyMesh.position);
                if (distKey < 3.5) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    doorMesh.material.color.setHex(0x00ff00);
                    gameStatus.innerText = "열쇠 습득 완료! 출구 문으로 탈출하세요!";
                    gameStatus.style.color = "#00ff00";
                }
            }
        }

        function triggerJumpscare() {
            gameOver = true;
            jumpscareOverlay.style.display = 'flex';
        }

        function animate() {
            requestAnimationFrame(animate);

            if (!gameStarted || gameOver || gameClear) return;

            const time = performance.now();
            const delta = (time - prevTime) / 1000;

            // 플레이어 이동
            velocity.x -= velocity.x * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;

            direction.z = Number(moveForward) - Number(moveBackward);
            direction.x = Number(moveRight) - Number(moveLeft);
            direction.normalize();

            if (moveForward || moveBackward) velocity.z -= direction.z * 45.0 * delta;
            if (moveLeft || moveRight) velocity.x -= direction.x * 45.0 * delta;

            camera.moveForward(-velocity.z * delta);
            camera.moveRight(velocity.x * delta);

            camera.position.x = Math.max(-14, Math.min(14, camera.position.x));
            camera.position.z = Math.max(-14, Math.min(14, camera.position.z));

            // 살인마 AI 추적
            const dirToPlayer = new THREE.Vector3().subVectors(camera.position, killerMesh.position);
            dirToPlayer.y = 0;
            const distToPlayer = dirToPlayer.length();

            if (distToPlayer > 0.1) {
                dirToPlayer.normalize();
                killerMesh.position.addScaledVector(dirToPlayer, killerSpeed * delta);
                killerMesh.lookAt(camera.position.x, killerMesh.position.y, camera.position.z);
            }

            // 갑툭튀
            if (distToPlayer < 1.8) {
                triggerJumpscare();
            }

            // 탈출 성공
            const distDoor = camera.position.distanceTo(doorMesh.position);
            if (distDoor < 2.5 && hasKey) {
                gameClear = true;
                alert("🎉 폐가에서 성공적으로 탈출했습니다!");
            }

            if (keyMesh) keyMesh.rotation.y += 0.02;

            prevTime = time;
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

components.html(game_html, height=750)
