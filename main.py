import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="The Backrooms: Escape Level 0", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Courier New', monospace; color: #d4c883; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; cursor: crosshair; }
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
            width: 4px; height: 4px; background: rgba(255,255,255,0.7);
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
        <div>📍 LEVEL 0: THE LOBBY</div>
        <div>🔦 손전등: <span id="flashlight-status" style="color: #ffff00;">ON (F)</span> | 🧍 상태: <span id="crouch-status" style="color: #ffffff;">서있음 (C)</span></div>
        <div style="font-size: 14px; color: #aaa; margin-top: 5px;">[WASD] 이동 | [C] 숙이기 | [F] 손전등/습득</div>
        <div id="game-status" style="color: #ffcc00; margin-top: 5px; font-weight: bold;">🎯 목표: 미로 구석에서 '아몬드 워터'를 찾아 빨간 비상문을 열어 탈출하세요!</div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #d1b838; font-size: 60px; margin-bottom: 0px; letter-spacing: 6px;">THE BACKROOMS</h1>
        <p style="font-size: 16px; color: #a39655; margin-top: 15px; max-width: 550px; line-height: 1.6;">
            현실의 틈새로 떨어져 백룸에 갇혔습니다.<br>
            1. 미로 끝에 있는 <b>아몬드 워터</b>를 구하세요.<br>
            2. <b>C키로 개구멍을 숙여 통과</b>하며 박테리아 괴물을 피하세요.<br>
            3. 열린 <b>비상문</b>을 통해 탈출하세요!
        </p>
        <button id="start-btn">NOCLIP IN</button>
    </div>

    <!-- 게임 오버 / 클리어 화면 -->
    <div id="end-screen">
        <h1 id="end-title" style="font-size: 70px; letter-spacing: 4px;">YOU ESCAPED</h1>
        <p id="end-desc" style="font-size: 18px; color: #aaa; margin-top: 10px;">무사히 백룸 Level 0을 탈출했습니다!</p>
        <p style="font-size: 14px; color: #666; margin-top: 30px;">F5 키를 눌러 다시 플레이하기</p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, flashlight;
        let mainFluorescentLight, exitSignLight;
        const keys = {};
        let prevTime = performance.now();

        let isFlashlightOn = true;
        let isCrouching = false;
        let hasKey = false;
        let gameStarted = false;
        let gameOver = false;
        let gameClear = false;

        let keyMesh, exitDoorMesh, monsterMesh, monsterEyeMat, doorLight;
        let isChasing = false;

        const holeBounds = { xMin: -7.0, xMax: -5.0, zMin: -5.0, zMax: 1.0 };

        const waypoints = [
            new THREE.Vector3(-12, 0, -12),
            new THREE.Vector3(12, 0, -12),
            new THREE.Vector3(12, 0, 12),
            new THREE.Vector3(-12, 0, 12)
        ];
        let currentWaypointIndex = 0;

        const startScreen = document.getElementById('start-screen');
        const startBtn = document.getElementById('start-btn');
        const flashlightStatus = document.getElementById('flashlight-status');
        const crouchStatus = document.getElementById('crouch-status');
        const gameStatus = document.getElementById('game-status');
        const endScreen = document.getElementById('end-screen');
        const endTitle = document.getElementById('end-title');
        const endDesc = document.getElementById('end-desc');

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x2b2716);
            scene.fog = new THREE.FogExp2(0x2b2716, 0.035);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 1.6, 8);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0x7d7343, 0.8);
            scene.add(ambientLight);

            mainFluorescentLight = new THREE.PointLight(0xfff5c0, 1.5, 40);
            mainFluorescentLight.position.set(0, 3.8, 0);
            scene.add(mainFluorescentLight);

            flashlight = new THREE.SpotLight(0xfff8d6, 5, 30, Math.PI / 3.5, 0.5, 1);
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);
            scene.add(camera);

            const floorGeo = new THREE.PlaneGeometry(40, 40);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x59522c, roughness: 0.9 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            const ceilGeo = new THREE.PlaneGeometry(40, 40);
            const ceilMat = new THREE.MeshStandardMaterial({ color: 0x8c8352, roughness: 0.5 });
            const ceil = new THREE.Mesh(ceilGeo, ceilMat);
            ceil.position.y = 4.0;
            ceil.rotation.x = Math.PI / 2;
            scene.add(ceil);

            buildBackroomsMaze();

            // [탈출 비상문 시스템]
            const doorGeo = new THREE.BoxGeometry(2.2, 3.5, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x8b0000 });
            exitDoorMesh = new THREE.Mesh(doorGeo, doorMat);
            exitDoorMesh.position.set(0, 1.75, 18.8);
            scene.add(exitDoorMesh);

            // 문 위 표시등 (잠김: 빨간색, 열림: 초록색)
            doorLight = new THREE.PointLight(0xff0000, 3, 8);
            doorLight.position.set(0, 3.5, 18.0);
            scene.add(doorLight);

            // [탈출 키 - 아몬드 워터]
            const keyGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.6, 8);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffffaa, emissive: 0x888800 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(14, 0.5, -14);
            scene.add(keyMesh);

            createBacteriaEntity();

            window.addEventListener('keydown', (e) => {
                keys[e.code] = true;
                if (e.code === 'KeyF') interact();
                if (e.code === 'KeyC') toggleCrouch();
            });

            window.addEventListener('keyup', (e) => {
                keys[e.code] = false;
            });

            document.addEventListener('mousemove', (e) => {
                if (!gameStarted || gameOver || gameClear) return;

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

        function buildBackroomsMaze() {
            const wallMat = new THREE.MeshStandardMaterial({ color: 0xa89f5a, roughness: 0.8 });

            const wallData = [
                [0, 2, -19.5, 40, 4, 0.5],
                [0, 2, 19.5, 40, 4, 0.5],
                [-19.5, 2, 0, 0.5, 4, 40],
                [19.5, 2, 0, 0.5, 4, 40],
                [6, 2, -6, 0.5, 4, 20],
                [-8, 2, 8, 18, 4, 0.5],
                [10, 2, 6, 0.5, 4, 16],
                [-10, 2, -10, 12, 4, 0.5]
            ];

            wallData.forEach(w => {
                const geo = new THREE.BoxGeometry(w[3], w[4], w[5]);
                const wall = new THREE.Mesh(geo, wallMat);
                wall.position.set(w[0], w[1], w[2]);
                scene.add(wall);
            });

            const holeWallGeo = new THREE.BoxGeometry(14, 2.8, 0.5);
            const holeWall = new THREE.Mesh(holeWallGeo, wallMat);
            holeWall.position.set(-6, 2.6, -2);
            scene.add(holeWall);
        }

        function createBacteriaEntity() {
            monsterMesh = new THREE.Group();

            const bodyGeo = new THREE.CylinderGeometry(0.2, 0.3, 2.8, 6);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.1 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 1.4;
            monsterMesh.add(body);

            const armGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.2);
            const arm1 = new THREE.Mesh(armGeo, bodyMat);
            const arm2 = new THREE.Mesh(armGeo, bodyMat);
            arm1.position.set(-0.4, 1.2, 0);
            arm1.rotation.z = Math.PI / 6;
            arm2.position.set(0.4, 1.2, 0);
            arm2.rotation.z = -Math.PI / 6;
            monsterMesh.add(arm1);
            monsterMesh.add(arm2);

            const eyeGeo = new THREE.SphereGeometry(0.09, 6, 6);
            monsterEyeMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const eye1 = new THREE.Mesh(eyeGeo, monsterEyeMat);
            const eye2 = new THREE.Mesh(eyeGeo, monsterEyeMat);
            eye1.position.set(-0.12, 2.6, -0.2);
            eye2.position.set(0.12, 2.6, -0.2);
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

            // F 키 손전등 Toggle 및 아이템 습득
            const distKey = keyMesh ? camera.position.distanceTo(keyMesh.position) : 999;

            if (!hasKey && keyMesh && distKey < 3.5) {
                // 아이템 습득
                hasKey = true;
                scene.remove(keyMesh);
                exitDoorMesh.material.color.setHex(0x00ff00);
                doorLight.color.setHex(0x00ff00);
                gameStatus.innerText = "🔑 아몬드 워터를 얻었습니다! 녹색 불빛이 켜진 비상문으로 탈출하세요!";
                gameStatus.style.color = "#00ff00";
            } else {
                // 손전등 Toggle
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

            const moveSpeed = (isCrouching ? 2.5 : 5.0) * delta;
            
            const oldX = camera.position.x;
            const oldZ = camera.position.z;

            if (keys['KeyW'] || keys['ArrowUp']) camera.translateZ(-moveSpeed);
            if (keys['KeyS'] || keys['ArrowDown']) camera.translateZ(moveSpeed);
            if (keys['KeyA'] || keys['ArrowLeft']) camera.translateX(-moveSpeed);
            if (keys['KeyD'] || keys['ArrowRight']) camera.translateX(moveSpeed);

            if (
                camera.position.x > holeBounds.xMin && camera.position.x < holeBounds.xMax &&
                camera.position.z > holeBounds.zMin && camera.position.z < holeBounds.zMax
            ) {
                if (camera.position.y > 1.0) {
                    camera.position.x = oldX;
                    camera.position.z = oldZ;
                }
            }

            camera.position.x = Math.max(-18, Math.min(18, camera.position.x));
            camera.position.z = Math.max(-18, Math.min(18, camera.position.z));

            // [박테리아 괴물 AI]
            const distToPlayer = monsterMesh.position.distanceTo(camera.position);

            if (isFlashlightOn && distToPlayer < 13.0) {
                if (!isChasing) {
                    isChasing = true;
                    monsterEyeMat.color.setHex(0xff0000);
                    gameStatus.innerText = "🚨 박테리아 괴물이 손전등 빛을 발견하고 쫓아옵니다!";
                    gameStatus.style.color = "#ff0000";
                }
            } else if (!isFlashlightOn && distToPlayer > 10.0) {
                if (isChasing) {
                    isChasing = false;
                    monsterEyeMat.color.setHex(0xffffff);
                    gameStatus.innerText = "⚠️ 괴물이 추적을 멈췄습니다.";
                    gameStatus.style.color = "#ffaa00";
                }
            }

            if (isChasing) {
                const dir = new THREE.Vector3().subVectors(camera.position, monsterMesh.position);
                dir.y = 0;
                dir.normalize();
                monsterMesh.position.addScaledVector(dir, 3.8 * delta);
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
                    monsterMesh.position.addScaledVector(dir, 2.0 * delta);
                    monsterMesh.lookAt(targetWaypoint.x, monsterMesh.position.y, targetWaypoint.z);
                }
            }

            // [사망 조건]
            if (distToPlayer < 1.5) {
                gameOver = true;
                endScreen.style.display = 'flex';
                endScreen.style.background = '#110000';
                endTitle.innerText = "YOU LOST YOUR SANITY";
                endTitle.style.color = "#8b0000";
                endDesc.innerText = "박테리아 괴물에게 사냥당했습니다...";
            }

            // [탈출 성공 조건]
            const distDoor = camera.position.distanceTo(exitDoorMesh.position);
            if (distDoor < 2.5 && hasKey) {
                gameClear = true;
                endScreen.style.display = 'flex';
                endScreen.style.background = '#0a1a0a';
                endTitle.innerText = "SUCCESSFUL ESCAPE!";
                endTitle.style.color = "#00ff00";
                endDesc.innerText = "🎉 백룸 Level 0에서 무사히 탈출했습니다!";
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
