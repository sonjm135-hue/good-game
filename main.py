import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Basketball Arcade", layout="wide")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; }
        #ui {
            position: absolute; top: 20px; left: 20px; color: #fff;
            font-size: 20px; font-weight: bold; text-shadow: 2px 2px 4px #000;
            pointer-events: none; z-index: 10;
        }
        #combo-ui {
            font-size: 28px; color: #ffeb3b; display: none; margin-top: 5px;
            animation: pulse 0.5s infinite alternate;
        }
        @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.1); } }
        #game-over {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); display: none; flex-direction: column;
            justify-content: center; align-items: center; color: #fff; z-index: 20;
        }
        #restart-btn {
            margin-top: 20px; padding: 12px 30px; font-size: 22px; font-weight: bold;
            color: #111; background-color: #ff9800; border: none; border-radius: 8px;
            cursor: pointer; transition: 0.2s;
        }
        #restart-btn:hover { background-color: #ffb74d; transform: scale(1.05); }
        #guide {
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            color: #ddd; font-size: 16px; background: rgba(0,0,0,0.6); padding: 8px 16px;
            border-radius: 20px; pointer-events: none; z-index: 10;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="ui">
        <div>SCORE: <span id="score" style="color: #4caf50;">0</span></div>
        <div>TIME: <span id="timer" style="color: #ff5722;">60</span>s</div>
        <div id="combo-ui">🔥 <span id="combo-count">0</span> COMBO! (+<span id="combo-bonus">0</span>)</div>
    </div>
    <div id="guide">마우스 드래그로 조준 및 힘을 조절하여 슛을 쏘세요!</div>

    <div id="game-over">
        <h1 style="font-size: 50px; margin-bottom: 10px; color: #ff9800;">GAME OVER</h1>
        <p style="font-size: 24px;">최종 점수: <span id="final-score" style="color: #4caf50;">0</span>점</p>
        <button id="restart-btn" onclick="resetGame()">다시 도전</button>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer;
        let ball, rim, backboard, hoopGroup;
        let isDragging = false, dragStart = { x: 0, y: 0 }, dragEnd = { x: 0, y: 0 };
        let ballVelocity = new THREE.Vector3(0, 0, 0);
        let isBallInAir = false;
        
        // 게임 상태 변수
        let score = 0, timeLeft = 60, combo = 0;
        let gameActive = true, timerInterval;
        let particles = [];

        // 골대 이동 관련 변수
        let hoopDirection = 1;
        let hoopSpeed = 0.05;

        const gravity = -0.008;
        const ballInitialPos = new THREE.Vector3(0, 1.2, 5);

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 2.5, 8);
            camera.lookAt(0, 2, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(5, 10, 7);
            dirLight.castShadow = true;
            scene.add(dirLight);

            // 바닥
            const floorGeo = new THREE.PlaneGeometry(20, 20);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x333344, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            // 농구공
            const ballGeo = new THREE.SphereGeometry(0.35, 32, 32);
            const ballMat = new THREE.MeshStandardMaterial({ color: 0xe65100, roughness: 0.4 });
            ball = new THREE.Mesh(ballGeo, ballMat);
            ball.castShadow = true;
            scene.add(ball);

            // 골대 그룹 생성
            hoopGroup = new THREE.Group();
            
            // 백보드
            const bbGeo = new THREE.BoxGeometry(2.4, 1.6, 0.1);
            const bbMat = new THREE.MeshStandardMaterial({ color: 0xeeeeee, roughness: 0.2 });
            backboard = new THREE.Mesh(bbGeo, bbMat);
            backboard.position.set(0, 3.5, -0.05);
            backboard.castShadow = true;
            hoopGroup.add(backboard);

            // 백보드 테두리 사각형
            const innerBoxGeo = new THREE.BoxGeometry(0.8, 0.6, 0.12);
            const innerBoxMat = new THREE.MeshBasicMaterial({ color: 0xd32f2f });
            const innerBox = new THREE.Mesh(innerBoxGeo, innerBoxMat);
            innerBox.position.set(0, 3.2, -0.04);
            hoopGroup.add(innerBox);

            // 림 (골대 고리)
            const rimGeo = new THREE.TorusGeometry(0.48, 0.04, 16, 32);
            const rimMat = new THREE.MeshStandardMaterial({ color: 0xd32f2f, roughness: 0.3 });
            rim = new THREE.Mesh(rimGeo, rimMat);
            rim.rotation.x = Math.PI / 2;
            rim.position.set(0, 2.9, 0.48);
            rim.castShadow = true;
            hoopGroup.add(rim);

            // 기둥
            const poleGeo = new THREE.CylinderGeometry(0.1, 0.1, 4, 16);
            const poleMat = new THREE.MeshStandardMaterial({ color: 0x555555 });
            const pole = new THREE.Mesh(poleGeo, poleMat);
            pole.position.set(0, 2, -0.2);
            hoopGroup.add(pole);

            hoopGroup.position.set(0, 0, -2);
            scene.add(hoopGroup);

            // 이벤트 리스너
            window.addEventListener('mousedown', onMouseDown);
            window.addEventListener('mouseup', onMouseUp);
            window.addEventListener('resize', onWindowResize);

            resetBall();
            startTimer();
            animate();
        }

        function startTimer() {
            timerInterval = setInterval(() => {
                if (!gameActive) return;
                timeLeft--;
                document.getElementById('timer').innerText = timeLeft;
                if (timeLeft <= 0) {
                    endGame();
                }
            }, 1000);
        }

        function endGame() {
            gameActive = false;
            clearInterval(timerInterval);
            document.getElementById('final-score').innerText = score;
            document.getElementById('game-over').style.display = 'flex';
        }

        function resetGame() {
            score = 0;
            timeLeft = 60;
            combo = 0;
            gameActive = true;
            document.getElementById('score').innerText = score;
            document.getElementById('timer').innerText = timeLeft;
            document.getElementById('combo-ui').style.display = 'none';
            document.getElementById('game-over').style.display = 'none';
            resetBall();
            startTimer();
        }

        function resetBall() {
            isBallInAir = false;
            ball.position.copy(ballInitialPos);
            ballVelocity.set(0, 0, 0);
        }

        function onMouseDown(e) {
            if (!gameActive || isBallInAir) return;
            isDragging = true;
            dragStart.x = e.clientX;
            dragStart.y = e.clientY;
        }

        function onMouseUp(e) {
            if (!isDragging || isBallInAir) return;
            isDragging = false;
            dragEnd.x = e.clientX;
            dragEnd.y = e.clientY;

            const dx = dragEnd.x - dragStart.x;
            const dy = dragStart.y - dragEnd.y; // Y축 반전

            if (dy > 20) { // 최소 드래그 거리 조건
                isBallInAir = true;
                ballVelocity.x = dx * 0.008;
                ballVelocity.y = Math.min(dy * 0.009, 0.32);
                ballVelocity.z = -Math.min(dy * 0.015, 0.45);
            }
        }

        // 파티클 폭죽 이펙트
        function createParticles(pos) {
            const pCount = 25;
            const pGeo = new THREE.SphereGeometry(0.05, 8, 8);
            const pMat = new THREE.MeshBasicMaterial({ color: 0xffeb3b });

            for (let i = 0; i < pCount; i++) {
                const particle = new THREE.Mesh(pGeo, pMat);
                particle.position.copy(pos);
                particle.velocity = new THREE.Vector3(
                    (Math.random() - 0.5) * 0.2,
                    Math.random() * 0.2,
                    (Math.random() - 0.5) * 0.2
                );
                particle.alive = true;
                scene.add(particle);
                particles.push(particle);
            }
        }

        function updateParticles() {
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.position.add(p.velocity);
                p.scale.multiplyScalar(0.95);
                if (p.scale.x < 0.01) {
                    scene.remove(p);
                    particles.splice(i, 1);
                }
            }
        }

        function checkScore() {
            const worldRimPos = new THREE.Vector3();
            rim.getWorldPosition(worldRimPos);

            const distXZ = new THREE.Vector2(ball.position.x - worldRimPos.x, ball.position.z - worldRimPos.z).length();
            const distY = Math.abs(ball.position.y - worldRimPos.y);

            // 공이 림 중앙 근처를 위에서 아래로 통과할 때
            if (distXZ < 0.35 && distY < 0.2 && ballVelocity.y < 0) {
                combo++;
                const bonus = combo > 1 ? (combo - 1) * 2 : 0;
                const points = 2 + bonus;
                score += points;

                document.getElementById('score').innerText = score;
                if (combo > 1) {
                    document.getElementById('combo-count').innerText = combo;
                    document.getElementById('combo-bonus').innerText = bonus;
                    document.getElementById('combo-ui').style.display = 'block';
                }

                createParticles(worldRimPos);
                resetBall();
            }
        }

        function checkCollisions() {
            const worldRimPos = new THREE.Vector3();
            rim.getWorldPosition(worldRimPos);
            
            const worldBbPos = new THREE.Vector3();
            backboard.getWorldPosition(worldBbPos);

            // 1. 백보드 충돌
            if (Math.abs(ball.position.x - worldBbPos.x) < 1.2 &&
                Math.abs(ball.position.y - worldBbPos.y) < 0.8 &&
                Math.abs(ball.position.z - worldBbPos.z) < 0.25) {
                ballVelocity.z *= -0.6; // 반사
                ballVelocity.x *= 0.8;
                ball.position.z = worldBbPos.z + 0.26;
            }

            // 2. 림(고리) 바운스 충돌
            const distToRim = ball.position.distanceTo(worldRimPos);
            if (distToRim < 0.55 && distToRim > 0.35) {
                ballVelocity.x += (ball.position.x - worldRimPos.x) * 0.1;
                ballVelocity.z += (ball.position.z - worldRimPos.z) * 0.1;
                ballVelocity.y *= -0.5;
            }
        }

        function animate() {
            requestAnimationFrame(animate);

            if (gameActive) {
                // 골대 좌우 이동 (난이도 요인)
                hoopGroup.position.x += hoopSpeed * hoopDirection;
                if (hoopGroup.position.x > 2.5 || hoopGroup.position.x < -2.5) {
                    hoopDirection *= -1;
                }

                // 공 물리 연산
                if (isBallInAir) {
                    ballVelocity.y += gravity;
                    ball.position.add(ballVelocity);
                    ball.rotation.x += 0.05;

                    checkCollisions();
                    checkScore();

                    // 바닥 충돌 및 바운스
                    if (ball.position.y <= 0.35) {
                        ball.position.y = 0.35;
                        ballVelocity.y *= -0.5;
                        ballVelocity.x *= 0.8;
                        ballVelocity.z *= 0.8;

                        // 슛 실패 시 콤보 초기화 후 리셋
                        if (Math.abs(ballVelocity.y) < 0.02) {
                            combo = 0;
                            document.getElementById('combo-ui').style.display = 'none';
                            resetBall();
                        }
                    }

                    // 맵 밖으로 벗어난 경우 리셋
                    if (ball.position.z < -10 || Math.abs(ball.position.x) > 8) {
                        combo = 0;
                        document.getElementById('combo-ui').style.display = 'none';
                        resetBall();
                    }
                }
            }

            updateParticles();
            renderer.render(scene, camera);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

components.html(game_html, height=750)
