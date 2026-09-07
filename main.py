import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GRANNY", layout="wide")

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
            color: #ccc; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px; z-index: 10;
        }
        #start-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: #000; color: #fff; text-align: center; z-index: 20;
        }
        #start-btn {
            margin-top: 25px; padding: 15px 50px; font-size: 28px; font-weight: bold;
            color: #fff; background-color: #5a0000; border: 2px solid #8b0000;
            cursor: pointer; font-family: 'Courier New', monospace; letter-spacing: 2px;
        }
        #start-btn:hover { background-color: #8b0000; color: #ffcccc; }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 4px; height: 4px; background: rgba(255,255,255,0.7);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none; z-index: 10;
        }
        #jumpscare-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: #110000; display: none; justify-content: center; align-items: center;
            flex-direction: column; z-index: 30;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div>Day 1</div>
        <div style="font-size: 14px; color: #888; margin-top: 5px;">[W,A,S,D] 이동 | [마우스] 시점 | [F] 열쇠 습득</div>
        <div id="game-status" style="color: #ff5555; margin-top: 5px;">Find the Master Key to Escape</div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #fff; font-size: 70px; margin-bottom: 0px; letter-spacing: 8px; font-weight: normal;">GRANNY</h1>
        <p style="font-size: 16px; color: #666; margin-top: 10px;">Welcome to Granny's House.</p>
        <button id="start-btn">PLAY</button>
    </div>

    <div id="jumpscare-overlay">
        <h1 style="font-size: 80px; color: #8b0000; font-weight: normal; letter-spacing: 4px;">YOU DIED</h1>
        <p style="font-size: 18px; color: #aaa; margin-top: 10px;">Granny found you...</p>
        <p style="font-size: 14px; color: #666; margin-top: 30px;">Press F5 to restart Day 1</p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, flashlight;
        const keys = {};
        let prevTime = performance.now();

        let hasKey = false;
        let gameStarted = false;
        let gameOver = false;
        let gameClear = false;

        let keyMesh, doorMesh, grannyMesh;
        let grannySpeed = 2.8;

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const gameStatus = document.getElementById('game-status');
        const jumpscareOverlay = document.getElementById('jumpscare-overlay');

        let isMouseDown = false;
        let previousMousePosition = { x: 0, y: 0 };

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x020202);
            scene.fog = new THREE.FogExp2(0x020202, 0.12);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 6);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 어두운 분위기 조명 (Granny 스타일)
            const ambientLight = new THREE.AmbientLight(0x222222);
            scene.add(ambientLight);

            flashlight = new THREE.SpotLight(0xffeedd, 2.5, 15, Math.PI / 4, 0.5, 1);
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            // 나무 바닥
            const floorGeo = new THREE.PlaneGeometry(30, 30);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x1f140e, roughness: 0.9 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            // 천장
            const ceilGeo = new THREE.PlaneGeometry(30, 30);
            const ceilMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a });
            const ceil = new THREE.Mesh(ceilGeo, ceilMat);
            ceil.position.y = 3.5;
            ceil.rotation.x = Math.PI / 2;
            scene.add(ceil);

            createHouse();

            // 열쇠 (Padlock Key)
            const keyGeo = new THREE.BoxGeometry(0.3, 0.3, 0.3);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xcc9900, emissive: 0x332200 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(9, 0.4, -9);
            scene.add(keyMesh);

            // 메인 현관문 (Main Door)
            const doorGeo = new THREE.BoxGeometry(2, 3.2, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x331a00 });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 1.6, 14.5);
            scene.add(doorMesh);

            createGrannyMonster();

            // [키보드 누름/뗌 키 상태 저장 - 키 입력 문제 해결]
            window.addEventListener('keydown', (e) => {
                keys[e.code] = true;
                if (e.code === 'KeyF') interact();
            });

            window.addEventListener('keyup', (e) => {
                keys[e.code] = false;
            });

            // 게임 시작 처리 및 캔버스 포커스 강제 지정
            startBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                startScreen.style.display = 'none';
                gameStarted = true;
                window.focus(); // 키보드 입력 활성화
            });

            const canvasContainer = document.getElementById('canvas-container');

            canvasContainer.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                previousMousePosition = { x: e.clientX, y: e.clientY };
                window.focus(); // 클릭할 때 포커스 유지
            });

            document.addEventListener('mouseup', () => { isMouseDown = false; });

            // 마우스 이동 시 시점 회전
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

            // 피묻은 드레스 (Granny)
            const bodyGeo = new THREE.CylinderGeometry(0.35, 0.5, 1.7, 8);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x443333 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 0.85;
            grannyMesh.add(body);

            // 머리
            const headGeo = new THREE.SphereGeometry(0.3, 8, 8);
            const headMat = new THREE.MeshStandardMaterial({ color: 0x667755 });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 1.8;
            grannyMesh.add(head);

            // 붉은 눈
            const eyeGeo = new THREE.SphereGeometry(0.06, 6, 6);
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const eye1 = new THREE.Mesh(eyeGeo, eyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, eyeMat);
            eye1.position.set(-0.1, 1.85, -0.25);
            eye2.position.set(0.1, 1.85, -0.25);
            grannyMesh.add(eye1);
            grannyMesh.add(eye2);

            grannyMesh.position.set(-9, 0, -9);
            scene.add(grannyMesh);
        }

        function createHouse() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x2d1f15, roughness: 0.9 });
            const walls = [
                [0, 1.75, -15, 30, 3.5, 0.5],
                [0, 1.75, 15, 30, 3.5, 0.5],
                [-15, 1.75, 0, 0.5, 3.5, 30],
                [15, 1.75, 0, 0.5, 3.5, 30],
                [-5, 1.75, -2, 10, 3.5, 0.5],
                [5, 1.75, -5, 0.5, 3.5, 15]
            ];

            walls.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                scene.add(wall);
            });
        }

        function interact() {
            if (gameOver || gameClear) return;

            if (!hasKey && keyMesh) {
                const distKey = camera.position.distanceTo(keyMesh.position);
                if (distKey < 3.0) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    doorMesh.material.color.setHex(0x00aa00);
                    gameStatus.innerText = "Key Collected! Escape through the Main Door!";
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

            // 이동 처리 (WASD 지속 입력 지원)
            const moveSpeed = 4.0 * delta;

            if (keys['KeyW'] || keys['ArrowUp']) camera.translateZ(-moveSpeed);
            if (keys['KeyS'] || keys['ArrowDown']) camera.translateZ(moveSpeed);
            if (keys['KeyA'] || keys['ArrowLeft']) camera.translateX(-moveSpeed);
            if (keys['KeyD'] || keys['ArrowRight']) camera.translateX(moveSpeed);

            // 높이 고정 및 이동 범위 제한
            camera.position.y = 1.6;
            camera.position.x = Math.max(-14, Math.min(14, camera.position.x));
            camera.position.z = Math.max(-14, Math.min(14, camera.position.z));

            // Granny 추적 AI
            const dirToPlayer = new THREE.Vector3().subVectors(camera.position, grannyMesh.position);
            dirToPlayer.y = 0;
            const distToPlayer = dirToPlayer.length();

            if (distToPlayer > 0.1) {
                dirToPlayer.normalize();
                grannyMesh.position.addScaledVector(dirToPlayer, grannySpeed * delta);
                grannyMesh.lookAt(camera.position.x, grannyMesh.position.y, camera.position.z);
            }

            // 그래니와 접촉 시 사망 (YOU DIED)
            if (distToPlayer < 1.5) {
                gameOver = true;
                if (document.exitPointerLock) document.exitPointerLock();
                jumpscareOverlay.style.display = 'flex';
            }

            // 문 탈출 검사
            const distDoor = camera.position.distanceTo(doorMesh.position);
            if (distDoor < 2.2 && hasKey) {
                gameClear = true;
                if (document.exitPointerLock) document.exitPointerLock();
                alert("🎉 You Escaped Granny's House!");
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
