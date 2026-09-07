import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Granny: 폐가의 살인마", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: sans-serif; color: white; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; }
        #ui-overlay {
            position: absolute; top: 15px; left: 15px;
            color: #ffcccc; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px; z-index: 10;
        }
        #start-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: rgba(0,0,0,0.9); color: #fff; text-align: center; z-index: 20;
        }
        #start-btn {
            margin-top: 20px; padding: 15px 45px; font-size: 24px; font-weight: bold;
            color: #fff; background-color: #8b0000; border: 2px solid #ff3333; border-radius: 4px;
            cursor: pointer; box-shadow: 0 0 15px #ff0000;
        }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 6px; height: 6px; background: rgba(255,255,255,0.8);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none; z-index: 10;
        }
        #jumpscare-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; display: none; justify-content: center; align-items: center;
            flex-direction: column; z-index: 30;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div>🩸 손전등: <span id="flashlight-status" style="color: #ff3333;">ON (F)</span></div>
        <div>📜 상태: <span id="game-status" style="color: #ffaaaa;">열쇠를 찾아 탈출하세요 (F키 상호작용)</span></div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #ff0000; font-size: 45px; margin-bottom: 5px; text-shadow: 0 0 10px red;">GRANNY: THE ESCAPE</h1>
        <p style="font-size: 16px; color: #aaa; max-width: 500px; line-height: 1.6;">
            눈을 뜬 곳은 핏자국으로 가득한 기괴한 목조 저택입니다.<br>
            살인마를 피해 황금 열쇠를 찾아 탈출하세요!
        </p>
        <button id="start-btn">게임 시작하기</button>
        <div style="margin-top: 20px; text-align: left; background: rgba(50,0,0,0.5); border: 1px solid #550000; padding: 15px; border-radius: 8px; font-size: 14px;">
            <p style="margin: 5px 0;">🎮 <b>W, A, S, D</b> : 이동</p>
            <p style="margin: 5px 0;">🖱️ <b>마우스 이동/드래그</b> : 화면 회전</p>
            <p style="margin: 5px 0;">🩸 <b>F 키</b> : 손전등 ON/OFF 및 열쇠 습득</p>
        </div>
    </div>

    <div id="jumpscare-overlay">
        <div style="font-size: 100px; filter: drop-shadow(0 0 20px red);">👵🩸</div>
        <h1 style="font-size: 50px; color: red; margin: 10px 0;">YOU DIED</h1>
        <h2 style="font-size: 22px; color: white;">그래니에게 잡혔습니다...</h2>
        <p style="font-size: 16px; color: yellow; margin-top: 20px;">F5 키를 눌러 다시 도전하세요.</p>
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
        let grannySpeed = 2.5;

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const flashlightStatus = document.getElementById('flashlight-status');
        const gameStatus = document.getElementById('game-status');
        const jumpscareOverlay = document.getElementById('jumpscare-overlay');

        let isMouseDown = false;
        let previousMousePosition = { x: 0, y: 0 };

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x050505);
            scene.fog = new THREE.FogExp2(0x050505, 0.08);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 5);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 기본 조명
            const ambientLight = new THREE.AmbientLight(0x333333);
            scene.add(ambientLight);

            // 손전등
            flashlight = new THREE.SpotLight(0xffeedd, 3, 20, Math.PI / 4, 0.5, 1);
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            // 바닥
            const floorGeo = new THREE.PlaneGeometry(30, 30);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x2b1810, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            // 천장
            const ceilGeo = new THREE.PlaneGeometry(30, 30);
            const ceilMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
            const ceil = new THREE.Mesh(ceilGeo, ceilMat);
            ceil.position.y = 4;
            ceil.rotation.x = Math.PI / 2;
            scene.add(ceil);

            createHouse();

            // 황금 열쇠
            const keyGeo = new THREE.BoxGeometry(0.4, 0.4, 0.4);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x886600 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(8, 0.5, -8);
            scene.add(keyMesh);

            // 문
            const doorGeo = new THREE.BoxGeometry(2, 3.5, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x552200 });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 1.75, 14.5);
            scene.add(doorMesh);

            // 그래니
            createGrannyMonster();

            // 이벤트
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);

            startBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                startScreen.style.display = 'none';
                gameStarted = true;
            });

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
                if (gameStarted && !gameOver && document.body.requestPointerLock) {
                    document.body.requestPointerLock();
                }
            });

            animate();
        }

        function createGrannyMonster() {
            grannyMesh = new THREE.Group();

            const bodyGeo = new THREE.CylinderGeometry(0.4, 0.5, 1.8, 8);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x3a2b22 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 0.9;
            grannyMesh.add(body);

            const headGeo = new THREE.SphereGeometry(0.35, 8, 8);
            const headMat = new THREE.MeshStandardMaterial({ color: 0x778866 });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 2.0;
            grannyMesh.add(head);

            const eyeGeo = new THREE.SphereGeometry(0.08, 6, 6);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const eye1 = new THREE.Mesh(eyeGeo, eyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, eyeMat);
            eye1.position.set(-0.12, 2.05, -0.3);
            eye2.position.set(0.12, 2.05, -0.3);
            grannyMesh.add(eye1);
            grannyMesh.add(eye2);

            grannyMesh.position.set(-8, 0, -8);
            scene.add(grannyMesh);
        }

        function createHouse() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x4a3222, roughness: 0.9 });
            const walls = [
                [0, 2, -15, 30, 4, 0.5],
                [0, 2, 15, 30, 4, 0.5],
                [-15, 2, 0, 0.5, 4, 30],
                [15, 2, 0, 0.5, 4, 30],
                [-5, 2, -2, 10, 4, 0.5],
                [5, 2, -5, 0.5, 4, 15]
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

            isFlashlightOn = !isFlashlightOn;
            flashlight.visible = isFlashlightOn;
            flashlightStatus.innerText = isFlashlightOn ? "ON (F)" : "OFF (F)";
            flashlightStatus.style.color = isFlashlightOn ? "#ff3333" : "gray";

            if (!hasKey && keyMesh) {
                const distKey = camera.position.distanceTo(keyMesh.position);
                if (distKey < 3.5) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    doorMesh.material.color.setHex(0x00ff00);
                    gameStatus.innerText = "열쇠 습득! 문으로 탈출하세요!";
                    gameStatus.style.color = "#00ff00";
                }
            }
        }

        function animate() {
            requestAnimationFrame(animate);

            if (!gameStarted || gameOver || gameClear) {
                renderer.render(scene, camera);
                return;
            }

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

            camera.position.x = Math.max(-14, Math.min(14, camera.position.x));
            camera.position.z = Math.max(-14, Math.min(14, camera.position.z));

            // 그래니 추적
            const dirToPlayer = new THREE.Vector3().subVectors(camera.position, grannyMesh.position);
            dirToPlayer.y = 0;
            const distToPlayer = dirToPlayer.length();

            if (distToPlayer > 0.1) {
                dirToPlayer.normalize();
                grannyMesh.position.addScaledVector(dirToPlayer, grannySpeed * delta);
                grannyMesh.lookAt(camera.position.x, grannyMesh.position.y, camera.position.z);
            }

            // 점프스케어
            if (distToPlayer < 1.6) {
                gameOver = true;
                if (document.exitPointerLock) document.exitPointerLock();
                jumpscareOverlay.style.display = 'flex';
            }

            // 탈출
            const distDoor = camera.position.distanceTo(doorMesh.position);
            if (distDoor < 2.5 && hasKey) {
                gameClear = true;
                if (document.exitPointerLock) document.exitPointerLock();
                alert("🎉 성공적으로 탈출했습니다!");
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
