<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>피아노 타일 게임</title>
  <style>
    body {
      margin: 0;
      background: #111;
      color: #fff;
      font-family: Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      overflow: hidden;
    }
    #score-board {
      font-size: 24px;
      margin-bottom: 10px;
    }
    #game-board {
      width: 320px;
      height: 480px;
      background: #222;
      position: relative;
      overflow: hidden;
      border: 2px solid #555;
    }
    .tile {
      width: 80px;
      height: 120px;
      background: #000;
      position: absolute;
      border: 1px solid #333;
      box-sizing: border-box;
      cursor: pointer;
    }
    #game-over {
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.85);
      flex-direction: column;
      justify-content: center;
      align-items: center;
      font-size: 28px;
    }
    button {
      margin-top: 15px;
      padding: 10px 20px;
      font-size: 16px;
      cursor: pointer;
      border: none;
      background: #4CAF50;
      color: white;
      border-radius: 5px;
    }
  </style>
</head>
<body>

  <div id="score-board">점수: <span id="score">0</span></div>
  
  <div id="game-board">
    <div id="game-over">
      <div>게임 오버!</div>
      <button onclick="startGame()">다시 시작</button>
    </div>
  </div>

  <script>
    const board = document.getElementById('game-board');
    const scoreElement = document.getElementById('score');
    const gameOverScreen = document.getElementById('game-over');
    
    let score = 0;
    let speed = 4;
    let isGameOver = false;
    let tiles = [];
    let animationId;

    // 효과음 재생 함수 (Web Audio API 사용)
    function playSound() {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440 + (score * 10), audioCtx.currentTime); // 점수가 오르면 음높이도 상승
      
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
      
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      
      osc.start();
      osc.stop(audioCtx.currentTime + 0.1);
  }

    function createTile(yPosition) {
      const col = Math.floor(Math.random() * 4); // 0~3번 라인 중 무작위 선택
      const tile = document.createElement('div');
      tile.className = 'tile';
      tile.style.left = (col * 80) + 'px';
      tile.style.top = yPosition + 'px';
      
      // 타일 클릭 이벤트
      tile.addEventListener('mousedown', function() {
        if (!isGameOver) {
          playSound();
          score++;
          scoreElement.innerText = score;
          
          // 일정 점수마다 속도 증가
          if (score % 5 === 0) speed += 0.5;
          
          tile.remove();
          tiles = tiles.filter(t => t !== tile);
        }
      });

      board.appendChild(tile);
      tiles.push(tile);
    }

    function update() {
      if (isGameOver) return;

      // 타일 이동
      for (let i = 0; i < tiles.length; i++) {
        const tile = tiles[i];
        const currentTop = parseFloat(tile.style.top);
        const newTop = currentTop + speed;
        tile.style.top = newTop + 'px';

        // 타일을 놓치고 바닥에 닿았을 때 게임 오버
        if (newTop >= 480) {
          endGame();
          return;
        }
      }

      // 가장 위쪽 타일 위치를 확인하여 새 타일 생성
      const lastTile = tiles[tiles.length - 1];
      if (!lastTile || parseFloat(lastTile.style.top) > 0) {
        const startY = lastTile ? parseFloat(lastTile.style.top) - 120 : -120;
        createTile(startY);
      }

      animationId = requestAnimationFrame(update);
    }

    function startGame() {
      // 초기화
      tiles.forEach(tile => tile.remove());
      tiles = [];
      score = 0;
      speed = 4;
      isGameOver = false;
      scoreElement.innerText = score;
      gameOverScreen.style.display = 'none';

      // 초기 타일 4개 생성
      for (let i = 0; i < 4; i++) {
        createTile((3 - i) * 120 - 120);
      }

      cancelAnimationFrame(animationId);
      update();
    }

    function endGame() {
      isGameOver = true;
      gameOverScreen.style.display = 'flex';
    }

    // 게임 시작
    startGame();
  </script>
</body>
</html>
