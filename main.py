import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🗡️ 검 강화하기",
    page_icon="🗡️",
    layout="wide"
)

st.title("🗡️ 영웅의 검 강화하기")

st.markdown("""
### 🕹️ 게임 방법
1. **강화하기** 버튼을 눌러 검을 강화하세요!
2. 강화 단계가 높아질수록 **성공 확률은 낮아지고, 실패 시 검이 파괴**될 위험이 커집니다.
3. 검을 판매하여 골드를 확보하거나, 최고 강화 단계(+20단계)에 도전해 보세요!
""")

game_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0; padding: 0; background-color: #0b0f19; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff; user-select: none; display: flex; justify-content: center; align-items: center; height: 100vh;
        }
        #game-box {
            width: 700px; background: #151d2a; border: 3px solid #2c3e50; border-radius: 16px; padding: 25px;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.8); text-align: center; box-sizing: border-box;
        }
        #stats {
            display: flex; justify-content: space-around; background: #1e293b; padding: 12px; border-radius: 10px;
            margin-bottom: 20px; font-size: 18px; font-weight: bold; border: 1px solid #334155;
        }
        #sword-stage {
            height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: radial-gradient(circle, rgba(30,58,138,0.4) 0%, rgba(15,23,42,0.8) 70%);
            border-radius: 12px; border: 2px dashed #475569; margin-bottom: 20px; position: relative;
        }
        #sword-icon { font-size: 80px; filter: drop-shadow(0 0 10px rgba(255,255,255,0.3)); transition: transform 0.2s; }
        #sword-name { font-size: 26px; font-weight: bold; margin-top: 10px; text-shadow: 0 0 10px #38bdf8; }
        #chance-info { font-size: 16px; color: #94a3b8; margin-bottom: 20px; }
        
        .btn-group { display: flex; gap: 15px; justify-content: center; }
        button {
            padding: 14px 28px; font-size: 18px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer;
            transition: all 0.2s; color: #fff; text-shadow: 1px 1px 2px #000;
        }
        #btn-upgrade { background: linear-gradient(135deg, #2563eb, #1d4ed8); box-shadow: 0 4px 12px rgba(37,99,235,0.4); }
        #btn-upgrade:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); transform: translateY(-2px); }
        #btn-sell { background: linear-gradient(135deg, #059669, #047857); box-shadow: 0 4px 12px rgba(5,150,105,0.4); }
        #btn-sell:hover { background: linear-gradient(135deg, #10b981, #059669); transform: translateY(-2px); }
        
        #log {
            margin-top: 20px; font-size: 20px; font-weight: bold; min-height: 30px;
            text-shadow: 0 0 8px rgba(255,255,255,0.5);
        }
    </style>
</head>
<body>
    <div id="game-box">
        <div id="stats">
            <div>골드: <span id="gold" style="color:#facc15;">1,000</span> G</div>
            <div>최고 기록: <span id="max-level" style="color:#38bdf8;">+0</span></div>
        </div>

        <div id="sword-stage">
            <div id="sword-icon">🗡️</div>
            <div id="sword-name" style="color:#e2e8f0;">+0 녹슨 낡은 단검</div>
        </div>

        <div id="chance-info">
            강화 비용: <span id="cost" style="color:#facc15;">100</span> G | 
            성공 확률: <span id="rate" style="color:#4ade80;">100%</span>
        </div>

        <div class="btn-group">
            <button id="btn-upgrade" onclick="upgrade()">🔥 강화하기</button>
            <button id="btn-sell" onclick="sell()">💰 판매하기 (<span id="sell-price">0</span> G)</button>
        </div>

        <div id="log">검을 강화하여 최고의 무기를 만드세요!</div>
    </div>

<script>
const swords = [
    { name: "녹슨 낡은 단검", icon: "🗡️", color: "#94a3b8", rate: 100, cost: 100, sell: 50 },
    { name: "수련용 철검", icon: "⚔️", color: "#cbd5e1", rate: 95, cost: 200, sell: 250 },
    { name: "기사의 강철검", icon: "⚔️", color: "#60a5fa", rate: 90, cost: 400, sell: 700 },
    { name: "은빛 롱소드", icon: "🗡️", color: "#38bdf8", rate: 85, cost: 800, sell: 1700 },
    { name: "불꽃 레이피어", icon: "🗡️", color: "#f97316", rate: 80, cost: 1500, sell: 3500 },
    { name: "독사 가디언 소드", icon: "⚔️", color: "#a855f7", rate: 75, cost: 3000, sell: 7500 },
    { name: "암흑의 마검", icon: "🗡️", color: "#ec4899", rate: 70, cost: 5000, sell: 15000 },
    { name: "용사자 대검", icon: "⚔️", color: "#eab308", rate: 65, cost: 10000, sell: 30000 },
    { name: "드래곤 슬레이어", icon: "🗡️", color: "#ef4444", rate: 60, cost: 20000, sell: 65000 },
    { name: "천상의 에스토크", icon: "⚔️", color: "#38bdf8", rate: 55, cost: 40000, sell: 140000 },
    { name: "성스러운 광휘검", icon: "🗡️", color: "#facc15", rate: 50, cost: 80000, sell: 300000 },
    { name: "공허의 정령검", icon: "⚔️", color: "#c084fc", rate: 45, cost: 150000, sell: 650000 },
    { name: "태초의 멸망도", icon: "🗡️", color: "#f43f5e", rate: 40, cost: 300000, sell: 1400000 },
    { name: "시공의 신검", icon: "⚔️", color: "#22d3ee", rate: 35, cost: 600000, sell: 3000000 },
    { name: "신살자의 무구", icon: "🗡️", color: "#f472b6", rate: 30, cost: 1200000, sell: 6500000 },
    { name: "창조의 엑스칼리버", icon: "⚔️", color: "#fbbf24", rate: 25, cost: 2500000, sell: 15000000 },
    { name: "차원 파괴의검", icon: "🗡️", color: "#a7f3d0", rate: 20, cost: 5000000, sell: 35000000 },
    { name: "영원의 인피니티 블레이드", icon: "⚔️", color: "#38bdf8", rate: 15, cost: 10000000, sell: 80000000 },
    { name: "전설의 유기적 초신성검", icon: "🔱", color: "#f43f5e", rate: 10, cost: 25000000, sell: 200000000 },
    { name: "절대자의 절대검", icon: "👑", color: "#facc15", rate: 5, cost: 50000000, sell: 500000000 },
    { name: "신화 속 제왕의 신검", icon: "💎", color: "#a855f7", rate: 0, cost: 0, sell: 1500000000 }
];

let level = 0;
let gold = 1000;
let maxLevel = 0;

function updateUI() {
    const cur = swords[level];
    document.getElementById('gold').innerText = gold.toLocaleString();
    document.getElementById('max-level').innerText = '+' + maxLevel;
    document.getElementById('sword-icon').innerText = cur.icon;
    document.getElementById('sword-name').innerText = '+' + level + ' ' + cur.name;
    document.getElementById('sword-name').style.color = cur.color;
    document.getElementById('cost').innerText = cur.cost.toLocaleString();
    document.getElementById('rate').innerText = cur.rate + '%';
    document.getElementById('sell-price').innerText = cur.sell.toLocaleString();

    if (level === 20) {
        document.getElementById('chance-info').innerText = "최고 단계에 도달했습니다!";
    } else {
        document.getElementById('chance-info').innerHTML = `
            강화 비용: <span style="color:#facc15;">${cur.cost.toLocaleString()}</span> G | 
            성공 확률: <span style="color:#4ade80;">${cur.rate}%</span>
        `;
    }
}

function upgrade() {
    const cur = swords[level];

    if (level >= 20) {
        setLog("이미 최고 단계의 검입니다!", "#facc15");
        return;
    }

    if (gold < cur.cost) {
        setLog("골드가 부족합니다!", "#ef4444");
        return;
    }

    gold -= cur.cost;

    // 아이콘 흔들기 애니메이션
    const iconEl = document.getElementById('sword-icon');
    iconEl.style.transform = 'scale(1.3) rotate(15deg)';
    setTimeout(() => { iconEl.style.transform = 'scale(1) rotate(0deg)'; }, 150);

    const rand = Math.random() * 100;
    if (rand < cur.rate) {
        level++;
        if (level > maxLevel) maxLevel = level;
        setLog(`🎉 강화 성공! (+${level} ${swords[level].name})`, "#4ade80");
    } else {
        setLog(`💥 강화 실패! 검이 깨졌습니다... (+0 초기화)`, "#ef4444");
        level = 0;
    }

    updateUI();
}

function sell() {
    const cur = swords[level];
    if (level === 0) {
        setLog("기본 검은 판매할 수 없습니다.", "#cbd5e1");
        return;
    }

    gold += cur.sell;
    setLog(`💰 검을 판매하여 +${cur.sell.toLocaleString()} G 를 얻었습니다!`, "#facc15");
    level = 0;
    updateUI();
}

function setLog(msg, color) {
    const logEl = document.getElementById('log');
    logEl.innerText = msg;
    logEl.style.color = color;
}

updateUI();
</script>
</body>
</html>"""

components.html(game_html, height=560)
