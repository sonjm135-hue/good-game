import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="폐가 탈출: 어둠 속의 괴물", layout="wide")

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
            background: #050505; color: #fff; text-align: center; z-index: 20;
        }
        #start-btn {
            margin-top: 25px; padding: 15px 50px; font-size: 26px; font-weight: bold;
            color: #fff; background-color: #5a0000; border: 2px solid #8b0000;
            cursor: pointer; font-family: 'Courier New', monospace; letter-spacing: 2px;
        }
        #start-btn:hover { background-color: #8b0000; color: #ffcccc; }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 6px; height: 6px; background: rgba(255,255,255,0.8);
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
        <div>🔦 손전등: <span id="flashlight-status" style="color: #ffff00;">ON (F)</span></div>
        <div>🧍 상태: <span id="crouch-status" style="color: #ffffff;">서있음 (C)</span></div>
        <div style="font-size: 14px; color: #aaa; margin-top: 5px;">[WASD] 이동 | [C] 숙이기 | [F] 손전등/열쇠</div>
        <div id="game-status" style="color: #ff5555; margin-top: 5px;">⚠️ 개구멍은 C키로 몸을 숙여야 지나갈 수 있습니다.</div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #ff3333; font-size: 60px; margin-bottom: 0px; letter-spacing: 4px;">NIGHT MONSTER</h1>
        <p style="font-size: 16px; color: #aaa; margin-top: 15px; max-width: 500px; line-height: 1.6;">
            저택 안을 괴물이 순찰하고 있습니다.<br>
            <b>C키로 몸을 숙여 개구멍을 통과</b>하고 손전등 빛을 조심하며 열쇠를 찾으세요!
        </p>
        <button id="start-btn">PLAY</button>
    </div>

    <div id="jumpscare-overlay">
        <h1 style="font-size: 80px; color: #8b0000; letter-spacing: 4px;">YOU DIED</h1>
        <p style="font-size: 18px; color: #aaa; margin-top: 10px;">괴물에게 사냥당했습니다...</p>
        <p style="font-size: 14px; color: #666; margin-top: 30px;">F5 키를 눌러 다시 시작하세요.</p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, flashlight;
        const keys = {};
        let prevTime = performance.now();

        let isFlashlightOn = true;
        let isCrouching = false;
        let hasKey = false;
        let gameStarted = false;
        let gameOver = false;
        let gameClear = false;

        let keyMesh, doorMesh, monsterMesh, monsterEyeMat;
        let isChasing = false;

        // 개구멍 통로 영역 정의 (xMin, xMax, zMin, zMax)
        const holeBounds = { xMin: -6.5, xMax: -5.5, zMin: -5, zMax: 1 };

        // 순찰 경로 지점들
        const waypoints = [
            new THREE.Vector3(-10, 0, -10),
            new THREE.Vector3(10, 0, -10),
            new THREE.Vector3(10, 0, 10),
            new THREE.Vector3(-10, 0, 10)
        ];
        let currentWaypointIndex = 0;

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const flashlightStatus = document.getElementById('flashlight-status');
        const crouchStatus = document.getElementById('crouch-status');
        const gameStatus = document.getElementById('game-status');
        const jumpscareOverlay = document.getElementById('jumpscare-overlay');

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111115);
            scene.fog = new THREE.FogExp2(0x111115, 0.03);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 6);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0x555566);
            scene.add(ambientLight);

            flashlight = new THREE.SpotLight(0xffffff, 6, 35, Math.PI / 3, 0.4, 1);
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            // 바닥
            const floorGeo = new THREE.PlaneGeometry(35, 35);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x3a2e2b, roughness: 0.6 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            // 천장
            const ceilGeo = new THREE.PlaneGeometry(35, 35);
            const ceilMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
            const ceil = new THREE.Mesh(ceilGeo, ceilMat);
            ceil.position.y = 4.0;
            ceil.rotation.x = Math.PI / 2;
            scene.add(ceil);

            createHouseWithHole();

            // 황금 열쇠
            const keyGeo = new THREE.BoxGeometry(0.4, 0.4, 0.4);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x886600 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(12, 0.5, -12);
            scene.add(keyMesh);

            // 출구 문
            const doorGeo = new THREE.BoxGeometry(2.2, 3.5, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x663300 });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 1.75, 16.8);
            scene.add(doorMesh);

            createShadowMonster();

            window.addEventListener('keydown', (e) => {
                keys[e.code] = true;
                if (e.code === 'KeyF') interact();
                if (e.code === 'KeyC') toggleCrouch();
            });

            window.addEventListener('keyup', (e) => {
                keys[e.code] = false;
            });

            document.addEventListener('mousemove', (e) => {
                if (!gameStarted || gameOver) return;

                const sensitivity = 0.0025;
                const movementX = e.movementX || 0;
                const movementY = e.movementY || 0;

                camera.rotation.y -= movementX * sensitivity;
                camera.rotation.x -= movementY * sensitivity;
                camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));
            });

            startBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                startScreen.style.display = 'none';
                gameStarted = true;
                window.focus();
            });

            animate();
        }

        function createHouseWithHole() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x554433, roughness: 0.7 });
            
            // 일반 외벽 구조
            const walls = [
                [0, 2, -17.5, 35, 4, 0.5],
                [0, 2, 17.5, 35, 4, 0.5],
                [-17.5, 2, 0, 0.5, 4, 35],
                [17.5, 2, 0, 0.5, 4, 35],
                [6, 2, -6, 0.5, 4, 18]
            ];

            walls.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                scene.add(wall);
            });

            // 개구멍이 뚫린 중앙 벽 배치 (위쪽만 벽으로 막고 아래쪽은 구멍)
            const holeTopWallGeo = new THREE.BoxGeometry(14, 2.8, 0.5); // 아래 1.2m는 비워둠
            const holeTopWall = new THREE.Mesh(holeTopWallGeo, wallMat);
            holeTopWall.position.set(-6, 2.6, -2);
            scene.add(holeTopWall);
        }

        function createShadowMonster() {
            monsterMesh = new THREE.Group();

            const bodyGeo = new THREE.CylinderGeometry(0.5, 0.7, 2.2, 8);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.2 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 1.1;
            monsterMesh.add(body);

            const headGeo = new THREE.SphereGeometry(0.4, 8, 8);
            const headMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 2.4;
            monsterMesh.add(head);

            const eyeGeo = new THREE.SphereGeometry(0.08, 6, 6);
            monsterEyeMat = new THREE.MeshBasicMaterial({ color: 0x00ffff });
            const eye1 = new THREE.Mesh(eyeGeo, monsterEyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, monsterEyeMat);
            eye1.position.set(-0.15, 2.45, -0.32);
            eye2.position.set(0.15, 2.45, -0.32);
            monsterMesh.add(eye1);
            monsterMesh.add(eye2);

            monsterMesh.position.copy(waypoints[0]);
            scene.add(monsterMesh);
        }

        function toggleCrouch() {
            if (gameOver || gameClear) return;
            isCrouching = !isCrouching;
            crouchStatus.innerText = isCrouching ? "숙임 (C)" : "서있음 (C)";
            crouchStatus.style.color = isCrouching ? "#ffaa00" : "#ffffff";
        }

        function interact() {
            if (gameOver || gameClear) return;

            isFlashlightOn = !isFlashlightOn;
            flashlight.visible = isFlashlightOn;
            flashlightStatus.innerText = isFlashlightOn ? "ON (F)" : "OFF (F)";
            flashlightStatus.style.color = isFlashlightOn ? "#ffff00" : "#888888";

            if (!hasKey && keyMesh) {
                const distKey = camera.position.distanceTo(keyMesh.position);
                if (distKey < 3.5) {
                    hasKey = true;
                    scene.remove(keyMesh);
                    doorMesh.material.color.setHex(0x00ff00);
                    gameStatus.innerText = "🔑 열쇠 습득 완료! 출구 문으로 탈출하세요!";
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

            // 서있을 때 높이 1.6m, 숙였을 때 높이 0.7m
            const targetY = isCrouching ? 0.7 : 1.6;
            camera.position.y += (targetY - camera.position.y) * 10.0 * delta;

            // 숙였을 때 이동 속도 감소
            const moveSpeed = (isCrouching ? 2.5 : 5.0) * delta;
            
            const oldX = camera.position.x;
            const oldZ = camera.position.z;

            if (keys['KeyW'] || keys['ArrowUp']) camera.translateZ(-moveSpeed);
            if (keys['KeyS'] || keys['ArrowDown']) camera.translateZ(moveSpeed);
            if (keys['KeyA'] || keys['ArrowLeft']) camera.translateX(-moveSpeed);
            if (keys['KeyD'] || keys['ArrowRight']) camera.translateX(moveSpeed);

            // [개구멍 통과 충돌 판정]
            // 플레이어가 개구멍 구역 안에 있고, 서있는 상태(높이 1.2m 이상)라면 진입 막음
            if (
                camera.position.x > holeBounds.xMin && camera.position.x < holeBounds.xMax &&
                camera.position.z > holeBounds.zMin && camera.position.z < holeBounds.zMax
            ) {
                if (camera.position.y > 1.0) { // 서 있으면 벽에 부딪힘
                    camera.position.x = oldX;
                    camera.position.z = oldZ;
                }
            }

            camera.position.x = Math.max(-16, Math.min(16, camera.position.x));
            camera.position.z = Math.max(-16, Math.min(16, camera.position.z));

            // [괴물 AI 및 손전등 반응]
            const distToPlayer = monsterMesh.position.distanceTo(camera.position);

            if (isFlashlightOn && distToPlayer < 12.0) {
                if (!isChasing) {
                    isChasing = true;
                    monsterEyeMat.color.setHex(0xff0000);
                    gameStatus.innerText = "🚨 괴물이 손전등 빛을 느끼고 쫓아옵니다!";
                    gameStatus.style.color = "#ff0000";
                }
            } else if (!isFlashlightOn && distToPlayer > 10.0) {
                if (isChasing) {
                    isChasing = false;
                    monsterEyeMat.color.setHex(0x00ffff);
                    gameStatus.innerText = "⚠️ 괴물이 시야를 잃고 다시 순찰합니다.";
                    gameStatus.style.color = "#ffaa00";
                }
            }

            if (isChasing) {
                const dir = new THREE.Vector3().subVectors(camera.position, monsterMesh.position);
                dir.y = 0;
                dir.normalize();
                monsterMesh.position.addScaledVector(dir, 3.5 * delta);
                monsterMesh.lookAt(camera.position.x, monsterMesh.position.y, camera.position.z);
            } else {
                const targetWaypoint = waypoints[currentWaypointIndex];
                const dir = new THREE.Vector3().subVectors(targetWaypoint, monsterMesh.position);
                dir.y = 0;
                const distToWaypoint = dir.length();

                if (distToWaypoint < 0.5) {
                    currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.length;
                } else {
                    dir.normalize();
                    monsterMesh.position.addScaledVector(dir, 1.8 * delta);
                    monsterMesh.lookAt(targetWaypoint.x, monsterMesh.position.y, targetWaypoint.z);
                }
            }

            if (distToPlayer < 1.5) {
                gameOver = true;
                jumpscareOverlay.style.display = 'flex';
            }

            const distDoor = camera.position.distanceTo(doorMesh.position);
            if (distDoor < 2.5 && hasKey) {
                gameClear = true;
                alert("🎉 괴물을 피하고 무사히 탈출했습니다!");
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
