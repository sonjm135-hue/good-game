import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="The Backrooms: Multi-Level Escape", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #d4c883; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; }
        #ui-overlay {
            position: absolute; top: 15px; left: 15px;
            color: #e6dc9c; text-shadow: 2px 2px 4px #000;
            pointer-events: none; font-size: 18px; z-index: 10;
        }
        #start-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: #18160c; color: #e6dc9c; text-align: center; z-index: 20;
        }
        #start-btn {
            margin-top: 25px; padding: 15px 50px; font-size: 26px; font-weight: bold;
            color: #18160c; background-color: #c9b044; border: 2px solid #8c7823;
            cursor: pointer; font-family: 'Courier New', monospace; letter-spacing: 2px;
        }
        #start-btn:hover { background-color: #e6dc9c; color: #000; }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 4px; height: 4px; background: rgba(255,255,255,0.8);
            border-radius: 50%; transform: translate(-50%, -50%);
            pointer-events: none; z-index: 10;
        }
        #end-screen {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: none; justify-content: center; align-items: center;
            flex-direction: column; z-index: 30; text-align: center;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    <div id="ui-overlay">
        <div>📍 <span id="level-title" style="font-weight: bold; color: #ffffa0;">LEVEL 0: THE LOBBY</span></div>
        <div>🔦 손전등: <span id="flashlight-status" style="color: #ffff00;">ON (F)</span> | 🧍 상태: <span id="crouch-status" style="color: #ffffff;">서있음 (C)</span></div>
        <div style="font-size: 14px; color: #aaa; margin-top: 5px;">[화면 클릭] 마우스 잠금 | [WASD] 이동 | [C] 숙이기 | [F] 손전등/습득</div>
        <div id="game-status" style="color: #ffcc00; margin-top: 5px; font-weight: bold;">🎯 목표: 맵 구석의 아이템을 찾아 녹색 비상문으로 탈출하세요!</div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #d1b838; font-size: 60px; margin-bottom: 0px; letter-spacing: 6px;">THE BACKROOMS</h1>
        <p style="font-size: 16px; color: #a39655; margin-top: 15px; max-width: 600px; line-height: 1.6;">
            백룸의 깊은 층으로 떨어졌습니다.<br>
            • <b>화면을 클릭하면 마우스와 시점이 일체화</b>됩니다.<br>
            • 확장된 대형 미로를 탐색하고 <b>Level 0부터 Level 3까지 탈출</b>하세요.<br>
            • <b>C키로 숙여 개구멍을 통과</b>하고 손전등 빛을 조심하세요!
        </p>
        <button id="start-btn">NOCLIP IN</button>
    </div>

    <div id="end-screen">
        <h1 id="end-title" style="font-size: 70px; letter-spacing: 4px;">YOU ESCAPED</h1>
        <p id="end-desc" style="font-size: 18px; color: #aaa; margin-top: 10px;">모든 레벨을 무사히 탈출했습니다!</p>
        <p style="font-size: 14px; color: #666; margin-top: 30px;">F5 키를 눌러 다시 시작하기</p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, flashlight;
        let mainFluorescentLight, doorLight;
        const keys = {};
        let prevTime = performance.now();

        let currentLevel = 0;
        const maxLevel = 3;

        let isFlashlightOn = true;
        let isCrouching = false;
        let hasKey = false;
        let gameStarted = false;
        let gameOver = false;
        let gameClear = false;

        let keyMesh, exitDoorMesh, monsterMesh, monsterEyeMat;
        let isChasing = false;

        // 개구멍 구역
        const holeBounds = { xMin: -11.0, xMax: -9.0, zMin: -8.0, zMax: 2.0 };

        // 확장된 대형 맵 순찰 경로
        const waypoints = [
            new THREE.Vector3(-30, 0, -30),
            new THREE.Vector3(30, 0, -30),
            new THREE.Vector3(30, 0, 30),
            new THREE.Vector3(-30, 0, 30)
        ];
        let currentWaypointIndex = 0;

        // 레벨별 색상 및 테마 정보
        const levelThemes = [
            { name: "LEVEL 0: THE LOBBY", bg: 0x2b2716, wall: 0xa89f5a, floor: 0x59522c, monsterSpeed: 3.5 },
            { name: "LEVEL 1: HABITABLE ZONE", bg: 0x11161a, wall: 0x3d484f, floor: 0x22292e, monsterSpeed: 4.2 },
            { name: "LEVEL 2: PIPE DREAMS", bg: 0x1c120c, wall: 0x593d2b, floor: 0x302116, monsterSpeed: 4.8 },
            { name: "LEVEL 3: ELECTRICAL STATION", bg: 0x0d0d0d, wall: 0x2b2b2b, floor: 0x1a1a1a, monsterSpeed: 5.5 }
        ];

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const flashlightStatus = document.getElementById('flashlight-status');
        const crouchStatus = document.getElementById('crouch-status');
        const gameStatus = document.getElementById('game-status');
        const levelTitle = document.getElementById('level-title');
        const endScreen = document.getElementById('end-screen');
        const endTitle = document.getElementById('end-title');
        const endDesc = document.getElementById('end-desc');
        const container = document.getElementById('canvas-container');

        function init() {
            scene = new THREE.Scene();

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 15);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            container.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambientLight);

            mainFluorescentLight = new THREE.PointLight(0xfff5c0, 1.5, 70);
            mainFluorescentLight.position.set(0, 4.8, 0);
            scene.add(mainFluorescentLight);

            flashlight = new THREE.SpotLight(0xfff8d6, 6, 40, Math.PI / 3.5, 0.5, 1);
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            loadLevel(0);

            // [마우스 포인터 잠금 - 화면 일체화]
            container.addEventListener('click', () => {
                if (gameStarted && !gameOver && !gameClear) {
                    container.requestPointerLock();
                }
            });

            document.addEventListener('mousemove', (e) => {
                if (document.pointerLockElement === container && gameStarted && !gameOver && !gameClear) {
                    const sensitivity = 0.0022;
                    camera.rotation.y -= e.movementX * sensitivity;
                    camera.rotation.x -= e.movementY * sensitivity;
                    camera.rotation.x = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, camera.rotation.x));
                }
            });

            window.addEventListener('keydown', (e) => {
                keys[e.code] = true;
                if (e.code === 'KeyF') interact();
                if (e.code === 'KeyC') toggleCrouch();
            });

            window.addEventListener('keyup', (e) => {
                keys[e.code] = false;
            });

            startBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                startScreen.style.display = 'none';
                gameStarted = true;
                container.requestPointerLock();
                window.focus();
            });

            animate();
        }

        function loadLevel(levelIdx) {
            currentLevel = levelIdx;
            hasKey = false;
            isChasing = false;
            
            // 기존 오브젝트 제거
            while(scene.children.length > 0){ 
                scene.remove(scene.children[0]); 
            }

            const theme = levelThemes[currentLevel];
            levelTitle.innerText = theme.name;
            scene.background = new THREE.Color(theme.bg);
            scene.fog = new THREE.FogExp2(theme.bg, 0.025);

            scene.add(camera);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
            scene.add(ambientLight);

            mainFluorescentLight = new THREE.PointLight(0xfff5c0, 1.5, 80);
            mainFluorescentLight.position.set(0, 4.8, 0);
            scene.add(mainFluorescentLight);

            // 대형 바닥 (80x80)
            const floorGeo = new THREE.PlaneGeometry(80, 80);
            const floorMat = new THREE.MeshStandardMaterial({ color: theme.floor, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            // 대형 천장
            const ceilGeo = new THREE.PlaneGeometry(80, 80);
            const ceilMat = new THREE.MeshStandardMaterial({ color: theme.bg });
            const ceil = new THREE.Mesh(ceilGeo, ceilMat);
            ceil.position.y = 5.0;
            ceil.rotation.x = Math.PI / 2;
            scene.add(ceil);

            buildLargeMaze(theme.wall);

            // 탈출 비상문
            const doorGeo = new THREE.BoxGeometry(2.5, 4.0, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x8b0000 });
            exitDoorMesh = new THREE.Mesh(doorGeo, doorMat);
            exitDoorMesh.position.set(0, 2.0, 38.8);
            scene.add(exitDoorMesh);

            doorLight = new THREE.PointLight(0xff0000, 3, 10);
            doorLight.position.set(0, 4.0, 37.5);
            scene.add(doorLight);

            // 열쇠 아이템
            const keyGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.8, 8);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffffaa, emissive: 0x888800 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(32, 0.6, -32);
            scene.add(keyMesh);

            createBacteriaEntity();

            camera.position.set(0, 1.6, 25);
            gameStatus.innerText = `🎯 [${theme.name}] 구석의 아몬드 워터를 찾은 후 비상문으로 탈출하세요!`;
            gameStatus.style.color = "#ffcc00";
        }

        // 80x80 스케일 대형 미로 구축
        function buildLargeMaze(wallColor) {
            const wallMat = new THREE.MeshStandardMaterial({ color: wallColor, roughness: 0.8 });

            const wallData = [
                // 외곽 벽
                [0, 2.5, -39.5, 80, 5, 0.5],
                [0, 2.5, 39.5, 80, 5, 0.5],
                [-39.5, 2.5, 0, 0.5, 5, 80],
                [39.5, 2.5, 0, 0.5, 5, 80],
                
                // 내부 확장 복도 벽들
                [15, 2.5, -15, 0.5, 5, 40],
                [-15, 2.5, 15, 40, 5, 0.5],
                [20, 2.5, 15, 0.5, 5, 30],
                [-20, 2.5, -15, 30, 5, 0.5],
                [0, 2.5, -25, 0.5, 5, 30]
            ];

            wallData.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                scene.add(wall);
            });

            // 개구멍 벽 (숙이기 필수)
            const holeWallGeo = new THREE.BoxGeometry(20, 3.8, 0.5);
            const holeWall = new THREE.Mesh(holeWallGeo, wallMat);
            holeWall.position.set(-10, 3.1, -3);
            scene.add(holeWall);
        }

        function createBacteriaEntity() {
            monsterMesh = new THREE.Group();

            const bodyGeo = new THREE.CylinderGeometry(0.3, 0.4, 3.2, 6);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 1.6;
            monsterMesh.add(body);

            const eyeGeo = new THREE.SphereGeometry(0.12, 6, 6);
            monsterEyeMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const eye1 = new THREE.Mesh(eyeGeo, monsterEyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, monsterEyeMat);
            eye1.position.set(-0.15, 2.9, -0.25);
            eye2.position.set(0.15, 2.9, -0.25);
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

            const distKey = keyMesh ? camera.position.distanceTo(keyMesh.position) : 999;

            if (!hasKey && keyMesh && distKey < 4.0) {
                hasKey = true;
                scene.remove(keyMesh);
                exitDoorMesh.material.color.setHex(0x00ff00);
                doorLight.color.setHex(0x00ff00);
                gameStatus.innerText = "🔑 아이템 습득 완료! 비상탈출문으로 이동하세요!";
                gameStatus.style.color = "#00ff00";
            } else {
                isFlashlightOn = !isFlashlightOn;
                flashlight.visible = isFlashlightOn;
                flashlightStatus.innerText = isFlashlightOn ? "ON (F)" : "OFF (F)";
                flashlightStatus.style.color = isFlashlightOn ? "#ffff00" : "#888888";
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

            if (Math.random() < 0.03) {
                mainFluorescentLight.intensity = Math.random() * 0.8 + 0.2;
            } else {
                mainFluorescentLight.intensity = 1.5;
            }

            const targetY = isCrouching ? 0.7 : 1.6;
            camera.position.y += (targetY - camera.position.y) * 10.0 * delta;

            const moveSpeed = (isCrouching ? 3.0 : 6.0) * delta;
            
            const oldX = camera.position.x;
            const oldZ = camera.position.z;

            if (keys['KeyW'] || keys['ArrowUp']) camera.translateZ(-moveSpeed);
            if (keys['KeyS'] || keys['ArrowDown']) camera.translateZ(moveSpeed);
            if (keys['KeyA'] || keys['ArrowLeft']) camera.translateX(-moveSpeed);
            if (keys['KeyD'] || keys['ArrowRight']) camera.translateX(moveSpeed);

            // [개구멍 판정]
            if (
                camera.position.x > holeBounds.xMin && camera.position.x < holeBounds.xMax &&
                camera.position.z > holeBounds.zMin && camera.position.z < holeBounds.zMax
            ) {
                if (camera.position.y > 1.0) {
                    camera.position.x = oldX;
                    camera.position.z = oldZ;
                }
            }

            camera.position.x = Math.max(-38, Math.min(38, camera.position.x));
            camera.position.z = Math.max(-38, Math.min(38, camera.position.z));

            // [괴물 AI]
            const distToPlayer = monsterMesh.position.distanceTo(camera.position);
            const currentSpeed = levelThemes[currentLevel].monsterSpeed;

            if (isFlashlightOn && distToPlayer < 15.0) {
                if (!isChasing) {
                    isChasing = true;
                    monsterEyeMat.color.setHex(0xff0000);
                    gameStatus.innerText = "🚨 괴물이 당신을 감지했습니다!";
                    gameStatus.style.color = "#ff0000";
                }
            } else if (!isFlashlightOn && distToPlayer > 12.0) {
                if (isChasing) {
                    isChasing = false;
                    monsterEyeMat.color.setHex(0xffffff);
                    gameStatus.innerText = "⚠️ 괴물이 시야를 잃었습니다.";
                    gameStatus.style.color = "#ffaa00";
                }
            }

            if (isChasing) {
                const dir = new THREE.Vector3().subVectors(camera.position, monsterMesh.position);
                dir.y = 0;
                dir.normalize();
                monsterMesh.position.addScaledVector(dir, currentSpeed * delta);
                monsterMesh.lookAt(camera.position.x, monsterMesh.position.y, camera.position.z);
            } else {
                const targetWaypoint = waypoints[currentWaypointIndex];
                const dir = new THREE.Vector3().subVectors(targetWaypoint, monsterMesh.position);
                dir.y = 0;
                const distToWaypoint = dir.length();

                if (distToWaypoint < 1.0) {
                    currentWaypointIndex = (currentWaypointIndex + 1) % waypoints.length;
                } else {
                    dir.normalize();
                    monsterMesh.position.addScaledVector(dir, 2.5 * delta);
                    monsterMesh.lookAt(targetWaypoint.x, monsterMesh.position.y, targetWaypoint.z);
                }
            }

            // 사망 판정
            if (distToPlayer < 1.8) {
                gameOver = true;
                document.exitPointerLock();
                endScreen.style.display = 'flex';
                endScreen.style.background = '#110000';
                endTitle.innerText = "YOU DIED";
                endTitle.style.color = "#8b0000";
                endDesc.innerText = `[${levelThemes[currentLevel].name}]에서 잡혔습니다...`;
            }

            // 레벨 클리어 / 전체 성공 조건
            const distDoor = camera.position.distanceTo(exitDoorMesh.position);
            if (distDoor < 3.0 && hasKey) {
                if (currentLevel < maxLevel) {
                    loadLevel(currentLevel + 1);
                } else {
                    gameClear = true;
                    document.exitPointerLock();
                    endScreen.style.display = 'flex';
                    endScreen.style.background = '#0a1a0a';
                    endTitle.innerText = "ALL LEVELS ESCAPED!";
                    endTitle.style.color = "#00ff00";
                    endDesc.innerText = "🎉 모든 레벨을 돌파하고 백룸에서 최종 탈출했습니다!";
                }
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
