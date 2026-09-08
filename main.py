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
        <div style="font-size: 14px; color: #aaa; margin-top: 5px;">[WASD] 이동 | [Q / E] 시점 회전 | [C] 숙이기 | [F] 손전등/습득</div>
        <div id="game-status" style="color: #ffcc00; margin-top: 5px; font-weight: bold;">🎯 목표: 맵 구석의 아이템을 찾아 녹색 비상문으로 탈출하세요!</div>
    </div>
    
    <div id="start-screen">
        <h1 style="color: #d1b838; font-size: 60px; margin-bottom: 0px; letter-spacing: 6px;">THE BACKROOMS</h1>
        <p style="font-size: 16px; color: #a39655; margin-top: 15px; max-width: 600px; line-height: 1.6;">
            백룸의 깊은 층으로 떨어졌습니다.<br>
            • <b>[Q] / [E] 키로 시점을 회전</b>하세요.<br>
            • 각 레벨마다 달라지는 <b>괴물과 맵 구조</b>를 파악하세요.<br>
            • 벽에 부딪히지 않게 조심하며 <b>Level 0부터 Level 3까지 탈출</b>하세요!
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

        // 물리 충돌을 처리할 벽 객체 바운딩 박스 리스트
        let wallBoxes = [];

        // 개구멍 구역 (특수 벽)
        const holeBounds = { xMin: -11.0, xMax: -9.0, zMin: -8.0, zMax: 2.0 };

        let waypoints = [];
        let currentWaypointIndex = 0;

        const levelThemes = [
            { name: "LEVEL 0: THE LOBBY", bg: 0x2b2716, wall: 0xa89f5a, floor: 0x59522c, monsterSpeed: 3.5, monsterName: "Bacteria" },
            { name: "LEVEL 1: HABITABLE ZONE", bg: 0x0a1014, wall: 0x2c3840, floor: 0x182026, monsterSpeed: 4.2, monsterName: "Smiler" },
            { name: "LEVEL 2: PIPE DREAMS", bg: 0x1a0f0a, wall: 0x4a2e1d, floor: 0x29180e, monsterSpeed: 4.8, monsterName: "Skin-Stealer" },
            { name: "LEVEL 3: ELECTRICAL STATION", bg: 0x080808, wall: 0x222222, floor: 0x111111, monsterSpeed: 5.5, monsterName: "Hound" }
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
            camera.position.set(0, 1.6, 25);
            camera.rotation.order = 'YXZ';

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            container.appendChild(renderer.domElement);

            flashlight = new THREE.SpotLight(0xfff8d6, 6, 40, Math.PI / 3.5, 0.5, 1);
            camera.add(flashlight);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera.add(flashlight.target);

            loadLevel(0);

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
                window.focus();
            });

            animate();
        }

        function loadLevel(levelIdx) {
            currentLevel = levelIdx;
            hasKey = false;
            isChasing = false;
            wallBoxes = [];
            
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

            // 대형 바닥 & 천장
            const floorGeo = new THREE.PlaneGeometry(80, 80);
            const floorMat = new THREE.MeshStandardMaterial({ color: theme.floor, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            const ceilGeo = new THREE.PlaneGeometry(80, 80);
            const ceilMat = new THREE.MeshStandardMaterial({ color: theme.bg });
            const ceil = new THREE.Mesh(ceilGeo, ceilMat);
            ceil.position.y = 5.0;
            ceil.rotation.x = Math.PI / 2;
            scene.add(ceil);

            // 레벨별 전용 맵 구축
            buildLevelMaze(currentLevel, theme.wall);

            // 탈출 비상문
            const doorGeo = new THREE.BoxGeometry(2.5, 4.0, 0.2);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x8b0000 });
            exitDoorMesh = new THREE.Mesh(doorGeo, doorMat);
            exitDoorMesh.position.set(0, 2.0, 38.8);
            scene.add(exitDoorMesh);

            doorLight = new THREE.PointLight(0xff0000, 3, 10);
            doorLight.position.set(0, 4.0, 37.5);
            scene.add(doorLight);

            // 아몬드 워터 (열쇠)
            const keyGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.8, 8);
            const keyMat = new THREE.MeshStandardMaterial({ color: 0xffffaa, emissive: 0x888800 });
            keyMesh = new THREE.Mesh(keyGeo, keyMat);
            keyMesh.position.set(32, 0.6, -32);
            scene.add(keyMesh);

            // 레벨별 괴물 생성
            createMonsterForLevel(currentLevel);

            camera.position.set(0, 1.6, 32);
            gameStatus.innerText = `🎯 [${theme.name}] 구석의 아몬드 워터를 찾은 후 비상문으로 탈출하세요!`;
            gameStatus.style.color = "#ffcc00";
        }

        // 벽 생성 및 물리 충돌 보더 등록 함수
        function createWall(x, y, z, w, h, d, color) {
            const wallMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.8 });
            const geo = new THREE.BoxGeometry(w, h, d);
            const wall = new THREE.Mesh(geo, wallMat);
            wall.position.set(x, y, z);
            scene.add(wall);

            // 물리 판정 박스 추가
            const box = new THREE.Box3().setFromObject(wall);
            wallBoxes.push(box);
        }

        // 레벨별 독특한 맵 레이아웃 생성
        function buildLevelMaze(level, wallColor) {
            // 외곽 벽 공통
            createWall(0, 2.5, -39.5, 80, 5, 0.8, wallColor);
            createWall(0, 2.5, 39.5, 80, 5, 0.8, wallColor);
            createWall(-39.5, 2.5, 0, 0.8, 5, 80, wallColor);
            createWall(39.5, 2.5, 0, 0.8, 5, 80, wallColor);

            if (level === 0) {
                // Level 0: 표준 격자 미로
                createWall(15, 2.5, -15, 0.8, 5, 40, wallColor);
                createWall(-15, 2.5, 15, 40, 5, 0.8, wallColor);
                createWall(20, 2.5, 15, 0.8, 5, 30, wallColor);
                createWall(-20, 2.5, -15, 30, 5, 0.8, wallColor);
                createWall(0, 2.5, -25, 0.8, 5, 30, wallColor);

                waypoints = [
                    new THREE.Vector3(-30, 0, -30),
                    new THREE.Vector3(30, 0, -30),
                    new THREE.Vector3(30, 0, 30),
                    new THREE.Vector3(-30, 0, 30)
                ];
            } else if (level === 1) {
                // Level 1: 긴 공장형 일자 복도 및 창고
                createWall(-10, 2.5, 0, 0.8, 5, 60, wallColor);
                createWall(10, 2.5, 0, 0.8, 5, 60, wallColor);
                createWall(-25, 2.5, -20, 30, 5, 0.8, wallColor);
                createWall(25, 2.5, 20, 30, 5, 0.8, wallColor);

                waypoints = [
                    new THREE.Vector3(0, 0, -30),
                    new THREE.Vector3(0, 0, 30),
                    new THREE.Vector3(25, 0, 0),
                    new THREE.Vector3(-25, 0, 0)
                ];
            } else if (level === 2) {
                // Level 2: 구불구불한 좁은 지하 통로
                createWall(0, 2.5, 10, 50, 5, 0.8, wallColor);
                createWall(-10, 2.5, -10, 50, 5, 0.8, wallColor);
                createWall(20, 2.5, -25, 0.8, 5, 30, wallColor);
                createWall(-20, 2.5, 25, 0.8, 5, 30, wallColor);

                waypoints = [
                    new THREE.Vector3(-30, 0, 20),
                    new THREE.Vector3(30, 0, -20),
                    new THREE.Vector3(0, 0, -30),
                    new THREE.Vector3(0, 0, 30)
                ];
            } else if (level === 3) {
                // Level 3: 발전소 고난도 세밀 미로
                createWall(-15, 2.5, 0, 0.8, 5, 40, wallColor);
                createWall(15, 2.5, 0, 0.8, 5, 40, wallColor);
                createWall(0, 2.5, -15, 30, 5, 0.8, wallColor);
                createWall(0, 2.5, 15, 30, 5, 0.8, wallColor);
                createWall(-25, 2.5, -25, 20, 5, 0.8, wallColor);
                createWall(25, 2.5, 25, 20, 5, 0.8, wallColor);

                waypoints = [
                    new THREE.Vector3(-30, 0, -30),
                    new THREE.Vector3(30, 0, -30),
                    new THREE.Vector3(30, 0, 30),
                    new THREE.Vector3(-30, 0, 30)
                ];
            }

            // 개구멍 벽 (공통 적용)
            createWall(-10, 3.1, -3, 20, 3.8, 0.8, wallColor);
        }

        // 레벨별 개성 있는 괴물 생성
        function createMonsterForLevel(level) {
            monsterMesh = new THREE.Group();

            if (level === 0) {
                // Level 0: Bacteria (기본 키 큰 기형체)
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

            } else if (level === 1) {
                // Level 1: Smiler (얼굴만 어둠 속에서 빛나는 괴물)
                const faceGeo = new THREE.SphereGeometry(1.2, 16, 16);
                const faceMat = new THREE.MeshStandardMaterial({ color: 0x000000 });
                const face = new THREE.Mesh(faceGeo, faceMat);
                face.position.y = 1.8;
                monsterMesh.add(face);

                const eyeGeo = new THREE.SphereGeometry(0.2, 8, 8);
                monsterEyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
                const eye1 = new THREE.Mesh(eyeGeo, monsterEyeMat);
                const eye2 = new THREE.Mesh(eyeGeo, monsterEyeMat);
                eye1.position.set(-0.4, 2.0, -1.0);
                eye2.position.set(0.4, 2.0, -1.0);
                monsterMesh.add(eye1);
                monsterMesh.add(eye2);

            } else if (level === 2) {
                // Level 2: Skin-Stealer (긴 왜곡 팔다리를 가진 괴물)
                const bodyGeo = new THREE.BoxGeometry(0.8, 2.2, 0.5);
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0x3d2011, roughness: 0.9 });
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = 1.5;
                monsterMesh.add(body);

                const armGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.5);
                const arm1 = new THREE.Mesh(armGeo, bodyMat);
                const arm2 = new THREE.Mesh(armGeo, bodyMat);
                arm1.position.set(-0.6, 1.2, -0.2);
                arm1.rotation.z = Math.PI / 4;
                arm2.position.set(0.6, 1.2, -0.2);
                arm2.rotation.z = -Math.PI / 4;
                monsterMesh.add(arm1);
                monsterMesh.add(arm2);

                monsterEyeMat = new THREE.MeshBasicMaterial({ color: 0xffff00 });
                const headGeo = new THREE.SphereGeometry(0.25, 8, 8);
                const head = new THREE.Mesh(headGeo, monsterEyeMat);
                head.position.set(0, 2.6, -0.2);
                monsterMesh.add(head);

            } else if (level === 3) {
                // Level 3: Hound (사족보행 맹수형 괴물)
                const bodyGeo = new THREE.BoxGeometry(0.9, 0.7, 2.2);
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.2 });
                const body = new THREE.Mesh(bodyGeo, bodyMat);
                body.position.y = 0.6;
                monsterMesh.add(body);

                monsterEyeMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
                const eyeGeo = new THREE.SphereGeometry(0.15, 8, 8);
                const eye = new THREE.Mesh(eyeGeo, monsterEyeMat);
                eye.position.set(0, 0.8, -1.1);
                monsterMesh.add(eye);
            }

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

        // 강화된 AABB 물리 충돌 검사 (벽 뚫림 방지)
        function checkWallCollision(targetPos, radius = 0.6) {
            const playerBox = new THREE.Box3(
                new THREE.Vector3(targetPos.x - radius, 0, targetPos.z - radius),
                new THREE.Vector3(targetPos.x + radius, 4.0, targetPos.z + radius)
            );

            for (let i = 0; i < wallBoxes.length; i++) {
                if (playerBox.intersectsBox(wallBoxes[i])) {
                    return true; // 충돌 발생
                }
            }
            return false;
        }

        function animate() {
            requestAnimationFrame(animate);

            if (!gameStarted || gameOver || gameClear) {
                renderer.render(scene, camera);
                return;
            }

            const time = performance.now();
            const delta = (time - prevTime) / 1000;

            // Q, E 키 시점 회전
            const rotateSpeed = 1.8 * delta;
            if (keys['KeyQ']) camera.rotation.y += rotateSpeed;
            if (keys['KeyE']) camera.rotation.y -= rotateSpeed;

            if (Math.random() < 0.03) {
                mainFluorescentLight.intensity = Math.random() * 0.8 + 0.2;
            } else {
                mainFluorescentLight.intensity = 1.5;
            }

            const targetY = isCrouching ? 0.7 : 1.6;
            camera.position.y += (targetY - camera.position.y) * 10.0 * delta;

            const moveSpeed = (isCrouching ? 3.0 : 6.0) * delta;
            
            // 물리 충돌을 고려한 독립 축 이동 알고리즘 (벽 비벼서 이동 가능)
            const forwardDir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
            forwardDir.y = 0; forwardDir.normalize();

            const sideDir = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
            sideDir.y = 0; sideDir.normalize();

            let moveVector = new THREE.Vector3();

            if (keys['KeyW'] || keys['ArrowUp']) moveVector.addScaledVector(forwardDir, moveSpeed);
            if (keys['KeyS'] || keys['ArrowDown']) moveVector.addScaledVector(forwardDir, -moveSpeed);
            if (keys['KeyA'] || keys['ArrowLeft']) moveVector.addScaledVector(sideDir, -moveSpeed);
            if (keys['KeyD'] || keys['ArrowRight']) moveVector.addScaledVector(sideDir, moveSpeed);

            // X축 이동 및 충돌 체크
            const nextPosX = new THREE.Vector3(camera.position.x + moveVector.x, camera.position.y, camera.position.z);
            if (!checkWallCollision(nextPosX)) {
                camera.position.x = nextPosX.x;
            }

            // Z축 이동 및 충돌 체크
            const nextPosZ = new THREE.Vector3(camera.position.x, camera.position.y, camera.position.z + moveVector.z);
            if (!checkWallCollision(nextPosZ)) {
                camera.position.z = nextPosZ.z;
            }

            // [개구멍 판정]
            if (
                camera.position.x > holeBounds.xMin && camera.position.x < holeBounds.xMax &&
                camera.position.z > holeBounds.zMin && camera.position.z < holeBounds.zMax
            ) {
                if (camera.position.y > 1.0) {
                    camera.position.z += (camera.position.z > -3 ? 0.2 : -0.2);
                }
            }

            // [괴물 AI]
            const distToPlayer = monsterMesh.position.distanceTo(camera.position);
            const currentSpeed = levelThemes[currentLevel].monsterSpeed;

            if (isFlashlightOn && distToPlayer < 16.0) {
                if (!isChasing) {
                    isChasing = true;
                    if(monsterEyeMat) monsterEyeMat.color.setHex(0xff0000);
                    gameStatus.innerText = `🚨 [${levelThemes[currentLevel].monsterName}] 괴물이 당신을 감지했습니다!`;
                    gameStatus.style.color = "#ff0000";
                }
            } else if (!isFlashlightOn && distToPlayer > 12.0) {
                if (isChasing) {
                    isChasing = false;
                    if(monsterEyeMat) monsterEyeMat.color.setHex(0xffffff);
                    gameStatus.innerText = "⚠️ 괴물이 추적을 멈췄습니다.";
                    gameStatus.style.color = "#ffaa00";
                }
            }

            if (isChasing) {
                const dir = new THREE.Vector3().subVectors(camera.position, monsterMesh.position);
                dir.y = 0;
                dir.normalize();
                
                const nextMonsterPos = monsterMesh.position.clone().addScaledVector(dir, currentSpeed * delta);
                if (!checkWallCollision(nextMonsterPos, 0.4)) {
                    monsterMesh.position.copy(nextMonsterPos);
                }
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
                endScreen.style.display = 'flex';
                endScreen.style.background = '#110000';
                endTitle.innerText = "YOU DIED";
                endTitle.style.color = "#8b0000";
                endDesc.innerText = `[${levelThemes[currentLevel].name}]에서 ${levelThemes[currentLevel].monsterName}에게 잡혔습니다...`;
            }

            // 레벨 클리어 판정
            const distDoor = camera.position.distanceTo(exitDoorMesh.position);
            if (distDoor < 3.0 && hasKey) {
                if (currentLevel < maxLevel) {
                    loadLevel(currentLevel + 1);
                } else {
                    gameClear = true;
                    endScreen.style.display = 'flex';
                    endScreen.style.background = '#0a1a0a';
                    endTitle.innerText = "ALL LEVELS ESCAPED!";
                    endTitle.style.color = "#00ff00";
                    endDesc.innerText = "🎉 백룸의 모든 레벨과 괴물들을 따돌리고 최종 탈출했습니다!";
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
