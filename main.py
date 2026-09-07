import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Granny: 폐가의 살인마", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: white; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; cursor: crosshair; }
        #ui-overlay {
            position: absolute; top: 15px; left: 15px;
            color: #ffcccc; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px; z-index: 10;
        }
        #start-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: radial-gradient(circle, #220000 0%, #000000 90%); color: #fff; text-align: center; z-index: 20;
        }
        #start-btn {
            margin-top: 20px; padding: 15px 45px; font-size: 26px; font-weight: bold;
            color: #fff; background-color: #8b0000; border: 2px solid #ff3333; border-radius: 4px;
            cursor: pointer; transition: 0.2s; box-shadow: 0 0 15px #ff0000;
        }
        #start-btn:hover { background-color: #ff0000; box-shadow: 0 0 25px #ff0000; }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 8px; height: 8px; background: rgba(255,0,0,0.7);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none; z-index: 10; box-shadow: 0 0 5px red;
        }
        #jumpscare-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; display: none; justify-content: center; align-items: center;
            flex-direction: column; z-index: 30;
        }
        #granny-face {
            font-size: 120px; animation: shake 0.05s infinite; filter: drop-shadow(0 0 20px red);
        }
        @keyframes shake {
            0% { transform: translate(2px, 2px) rotate(0deg); }
            20% { transform: translate(-3px, 0px) rotate(3deg); }
            40% { transform: translate(1px, -1px) rotate(-3deg); }
            60% { transform: translate(-2px, 1px) rotate(0deg); }
            80% { transform: translate(2px, 1px) rotate(2deg); }
            100% { transform: translate(1px, -2px) rotate(-1deg); }
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div>🩸 손전등: <span id="flashlight-status" style="color: #ff3333;">ON (F)</span></div>
        <div>📜 상태: <span id="game-status" style="color: #ffaaaa;">열쇠를 찾아 탈출하세요 (F키로 상호작용)</span></div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #ff0000; font-size: 50px; margin-bottom: 5px; text-shadow: 0 0 10px red;">GRANNY: THE ESCAPE</h1>
        <p style="font-size: 16px; color: #aaa; max-width: 550px; line-height: 1.6;">
            기절 후 눈을 뜬 곳은 핏자국으로 가득한 기괴한 목조 저택입니다.<br>
            살인마가 당신의 소리를 듣고 쫓아옵니다. 열쇠를 찾아 탈출하세요!
        </p>
        <button id="start-btn">저택 진입하기</button>
        <div style="margin-top: 25px; text-align: left; background: rgba(50,0,0,0.5); border: 1px solid #550000; padding: 18px; border-radius: 8px; font-size: 14px;">
            <p style="margin: 5px 0;">🎮 <b>W, A, S, D</b> : 이동</p>
            <p style="margin: 5px 0;">🖱️ <b>화면 드래그/마우스 이동</b> : 시점 전환</p>
            <p style="margin: 5px 0;">🩸 <b>F 키</b> : 손전등 ON/OFF 및 열쇠 습득</p>
        </div>
    </div>

    <div id="jumpscare-overlay">
        <div id="granny-face">👵🩸</div>
        <h1 style="font-size: 55px; color: red; text-shadow: 0 0 15px black; margin: 10px 0;">YOU DIED</h1>
        <h2 style="font-size: 25px; color: white;">그래니에게 잡혔습니다...</h2>
        <p style="font-size: 18px; color: yellow; margin-top: 20px;">F5 키를 눌러 다시 도전하세요.</p>
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

        let keyMesh, doorMesh, grannyMesh;
        let grannySpeed = 3.2;

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const flashlightStatus = document.getElementById('flashlight-status');
        const gameStatus = document.getElementById('game-status');
        const jumpscareOverlay = document.getElementById('jumpscare-overlay');

        let isMouseDown = false;
        let previousMousePosition = { x: 0, y: 0 };

        function init() {
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x050000, 0.16); // 피빛 안개 효과

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 9);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 손전등 (노란 어두운 조명)
            flashlight = new THREE.SpotLight(0xffccaa, 4, 18, Math.PI / 5, 0.5, 1);
            flashlight.castShadow = true;
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            const ambient = new THREE.AmbientLight(0x1a0505);
            scene.add(ambient);

            // Granny 스타일 나무 바닥
            const floorGeo = new THREE.PlaneGeometry(32, 32);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x2b1810, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            createGrannyHouse();

            // 황금 열쇠
            const keyGeo = new THREE.BoxGeometry(0.35, 0.35, 0.35);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x664400 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(11, 0.4, -11);
            scene.add(keyMesh);

            // 탈출용 목조 문
            const doorGeo = new THREE.BoxGeometry(2.2, 3.8, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x3d1f0d });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 1.9, 15.8);
            scene.add(doorMesh);

            // 그래니 (Granny) 모티브 몬스터 디자인
            createGrannyMonster();

            // 이벤트 등록
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);

            startBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                startScreen.style.display = 'none';
                gameStarted = true;
            });

            // 마우스 드래그 및 이동으로 360도 자유 시점 전환
            const canvasContainer = document.getElementById('canvas-container');
            
            canvasContainer.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
            });

            document.addEventListener('mouseup', () => { isMouseDown = false; });

            document.addEventListener('mousemove', (e) => {
                if (!gameStarted || gameOver) return;

                let deltaX = 0, deltaY = 0;

                if (document.pointerLockElement === document.body) {
                    deltaX = e.movementX;
                    deltaY = e.movementY;
                } else if (isMouseDown) {
                    deltaX = e.clientX - previousMousePosition.x;
                    deltaY = e.clientY - previousMousePosition.y;
                    previousMousePosition = { x: e.clientX, y: e.clientY };
                }

                camera.rotation.y -= deltaX * 0.003;
                camera.rotation.x -= deltaY * 0.003;
                camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));
            });

            canvasContainer.addEventListener('click', () => {
                if (gameStarted && !gameOver) {
                    document.body.requestPointerLock = document.body.requestPointerLock || document.body.mozRequestPointerLock;
                    if (document.body.requestPointerLock) document.body.requestPointerLock();
                }
            });

            animate();
        }

        function createGrannyMonster() {
            grannyMesh = new THREE.Group();

            // 몸통 (핏빛 드레스)
            const bodyGeo = new THREE.CylinderGeometry(0.4, 0.6, 2.0, 8);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x4a3b32 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 1.0;
            grannyMesh.add(body);

            // 머리
            const headGeo = new THREE.SphereGeometry(0.35, 8, 8);
            const headMat = new THREE.MeshStandardMaterial({ color: 0x889977 });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 2.1;
            grannyMesh.add(head);

            // 섬뜩한 붉은 눈
            const eyeGeo = new THREE.SphereGeometry(0.08, 6, 6);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const eye1 = new THREE.Mesh(eyeGeo, eyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, eyeMat);
            eye1.position.set(-0.12, 2.15, -0.3);
            eye2.position.set(0.12, 2.15, -0.3);
            grannyMesh.add(eye1);
            grannyMesh.add(eye2);

            grannyMesh.position.set(-11, 0, -11);
            scene.add(grannyMesh);
        }

        function createGrannyHouse() {
            // 피묻은 목조 벽면
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x3a2518, roughness: 0.9 });
            const bloodMat = new THREE.MeshStandardMaterial({ color: 0x550000, roughness: 0.5 });

            const walls = [
                [0, 2.5, -16, 32, 5, 0.5],
                [0, 2.5, 16, 32, 5, 0.5],
                [-16, 2.5, 0, 0.5, 5, 32],
                [16, 2.5, 0, 0.5, 5, 32],
                [-6, 2.5, -2, 12, 5, 0.5],
                [6, 2.5, -6, 0.5, 5, 16]
            ];

            walls.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                scene.add(wall);
            });

            // 핏자국 디테일 표현
            const bloodDecal = new THREE.Mesh(new THREE.PlaneGeometry(3, 3), bloodMat);
            bloodDecal.position.set(-5, 1.5, -15.7);
            scene.add(bloodDecal);
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
            flashlightStatus.style.color = isFlashlightOn ? "#ff3333" : "gray";

            // 열쇠 습득
            if (!hasKey && keyMesh) {
                const distKey = camera.position.distanceTo(keyMesh.position);
                if (distKey < 3.5) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    doorMesh.material.color.setHex(0x00ff00);
                    gameStatus.innerText = "열쇠 습득! 탈출구 문으로 달아나세요!";
                    gameStatus.style.color = "#00ff00";
                }
            }
        }

        function triggerJumpscare() {
            gameOver = true;
            if (document.exitPointerLock) document.exitPointerLock();
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

            camera.position.x = Math.max(-15, Math.min(15, camera.position.x));
            camera.position.z = Math.max(-15, Math.min(15, camera.position.z));

            // 그래니 추적 AI
            const dirToPlayer = new THREE.Vector3().subVectors(camera.position, grannyMesh.position);
            dirToPlayer.y = 0;
            const distToPlayer = dirToPlayer.length();

            if (distToPlayer > 0.1) {
                dirToPlayer.normalize();
                grannyMesh.position.addScaledVector(dirToPlayer, grannySpeed * delta);
                grannyMesh.lookAt(camera.position.x, grannyMesh.position.y, camera.position.z);
            }

            // 그래니 기괴한 요동 연출
            grannyMesh.position.y = Math.sin(time * 0.01) * 0.1;

            // 점프스케어 (그래니와 접촉 시)
            if (distToPlayer < 1.8) {
                triggerJumpscare();
            }

            // 탈출
            const distDoor = camera.position.distanceTo(doorMesh.position);
            if (distDoor < 2.5 && hasKey) {
                gameClear = true;
                if (document.exitPointerLock) document.exitPointerLock();
                alert("🎉 그래니의 집에서 성공적으로 탈출했습니다!");
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
