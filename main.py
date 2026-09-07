import streamlit as st
import random

st.set_page_config(page_title="어둠 속의 탈출", layout="centered")

# 맵 크기 및 구조 (1: 벽, 0: 길)
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1]
]

HEIGHT = len(MAP)
WIDTH = len(MAP[0])

# 게임 상태 초기화
def init_game():
    st.session_state.player = [1, 1]
    st.session_state.monster = [5, 7]
    st.session_state.key = [1, 7]
    st.session_state.exit = [5, 1]
    st.session_state.has_key = False
    st.session_state.game_over = False
    st.session_state.game_clear = False

if "player" not in st.session_state:
    init_game()

# 이동 함수
def move_player(dx, dy):
    if st.session_state.game_over or st.session_state.game_clear:
        return

    px, py = st.session_state.player
    nx, ny = px + dx, py + dy

    # 벽 체크
    if MAP[ny][nx] == 0:
        st.session_state.player = [nx, ny]

        # 열쇠 획득 체크
        if st.session_state.player == st.session_state.key:
            st.session_state.has_key = True

        # 탈출 체크
        if st.session_state.player == st.session_state.exit and st.session_state.has_key:
            st.session_state.game_clear = True
            return

        # 괴물 이동 (플레이어 추적)
        move_monster()

        # 괴물과 충돌 체크
        if st.session_state.player == st.session_state.monster:
            st.session_state.game_over = True

def move_monster():
    mx, my = st.session_state.monster
    px, py = st.session_state.player

    possible_moves = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = mx + dx, my + dy
        if MAP[ny][nx] == 0:
            # 플레이어와의 거리 계산
            dist = abs(px - nx) + abs(py - ny)
            possible_moves.append((dist, [nx, ny]))

    if possible_moves:
        possible_moves.sort()  # 가깝게 이동
        st.session_state.monster = possible_moves[0][1]

# 화면 상단 타이틀
st.title("👁️ 어둠 속의 탈출")

if st.session_state.game_over:
    st.error("💀 괴물에게 잡혔습니다... YOU DIED")
    if st.button("다시 시작"):
        init_game()
        st.rerun()

elif st.session_state.game_clear:
    st.balloons()
    st.success("🎉 탈출에 성공했습니다!")
    if st.button("다시 시작"):
        init_game()
        st.rerun()

else:
    # 맵 그리기 (손전등 시야 효과: 거리가 2 이하인 곳만 표시)
    px, py = st.session_state.player
    grid_html = "<div style='font-family: monospace; font-size: 24px; line-height: 1.2; text-align: center; background-color: black; padding: 20px; border-radius: 10px;'>"

    for y in range(HEIGHT):
        row_str = ""
        for x in range(WIDTH):
            dist = abs(px - x) + abs(py - y)
            
            # 시야 범위 내일 때만 표시
            if dist <= 2:
                if [x, y] == st.session_state.player:
                    row_str += "🏃"  # 플레이어
                elif [x, y] == st.session_state.monster:
                    row_str += "👹"  # 괴물
                elif [x, y] == st.session_state.key and not st.session_state.has_key:
                    row_str += "🔑"  # 열쇠
                elif [x, y] == st.session_state.exit:
                    row_str += "🚪"  # 탈출구
                elif MAP[y][x] == 1:
                    row_str += "⬛"  # 벽
                else:
                    row_str += "⬜"  # 길
            else:
                row_str += "🟦"  # 어둠 (시야 밖)
        grid_html += row_str + "<br>"
    grid_html += "</div>"

    st.markdown(grid_html, unsafe_allow_html=True)

    # 미션 정보
    if not st.session_state.has_key:
        st.warning("🔑 열쇠를 찾으세요!")
    else:
        st.info("🚪 문으로 가서 탈출하세요!")

    # 이동 버튼 (십자키 배치)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("⬆️ 위", on_click=move_player, args=(0, -1), use_container_width=True)
    
    col4, col5, col6 = st.columns([1, 1, 1])
    with col4:
        st.button("⬅️ 왼쪽", on_click=move_player, args=(-1, 0), use_container_width=True)
    with col5:
        st.button("⬇️ 아래", on_click=move_player, args=(0, 1), use_container_width=True)
    with col6:
        st.button("➡️ 오른쪽", on_click=move_player, args=(1, 0), use_container_width=True)
