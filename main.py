import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import sys

# 게임 초기화
pygame.init()
WIDTH, HEIGHT = 1000, 750
display = (WIDTH, HEIGHT)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("폐가 탈출: 살인마의 집")

# 마우스 고정
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# 카메라 / 플레이어 상태
camera_pos = [0.0, 1.0, 5.0]
camera_rot = [0.0, 0.0]  # pitch, yaw
flashlight_on = True
has_key = False
game_over = False
game_clear = False
jumpscare_active = False
jumpscare_timer = 0

# 아이템 및 엔티티 위치
KEY_POS = [10.0, 0.3, -12.0]
DOOR_POS = [0.0, 1.5, 9.8]
KILLER_POS = [12.0, 1.0, -14.0]

# 텍스트 렌더링 함수
def render_text(text, position):
    font = pygame.font.SysFont('malgungothic', 28)
    text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

# 3D 큐브 그리기
def draw_cube(pos, size, color):
    x, y, z = pos
    sx, sy, sz = size
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    
    vertices = [
        [sx, sy, -sz], [sx, -sy, -sz], [-sx, -sy, -sz], [-sx, sy, -sz],
        [sx, sy, sz], [sx, -sy, sz], [-sx, -sy, sz], [-sx, sy, sz]
    ]
    surfaces = [
        (0,1,2,3), (4,5,6,7), (0,4,7,3),
        (1,5,6,2), (0,1,5,4), (3,2,6,7)
    ]
    
    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()

# 조명 설정 (손전등)
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    if flashlight_on:
        # 손전등 SpotLight 설정
        light_pos = [camera_pos[0], camera_pos[1], camera_pos[2], 1.0]
        
        rad_yaw = math.radians(camera_rot[1])
        rad_pitch = math.radians(camera_rot[0])
        dir_x = math.sin(rad_yaw) * math.cos(rad_pitch)
        dir_y = -math.sin(rad_pitch)
        dir_z = -math.cos(rad_yaw) * math.cos(rad_pitch)
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [dir_x, dir_y, dir_z])
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 25.0)  # 손전등 각도
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.9, 0.7, 1.0])
    else:
        # 아주 어두운 암흑
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.05, 0.05, 0.05, 1.0])

# 초기 3D 엔진 설정
glEnable(GL_DEPTH_TEST)
glEnable(GL_COLOR_MATERIAL)
glMatrixMode(GL_PROJECTION)
gluPerspective(60, (WIDTH / HEIGHT), 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)

clock = pygame.time.Clock()

# 메인 루프
while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # F키 상호작용 (손전등 / 열쇠 획득)
            if event.key == pygame.K_f and not game_over and not game_clear:
                flashlight_on = not flashlight_on

                # 열쇠 근처에서 F키로 주우기
                dist_to_key = math.sqrt(
                    (camera_pos[0] - KEY_POS[0])**2 + 
                    (camera_pos[2] - KEY_POS[2])**2
                )
                if dist_to_key < 2.5 and not has_key:
                    has_key = True

    if not game_over and not game_clear:
        # 마우스 시점 회전
        mx, my = pygame.mouse.get_rel()
        camera_rot[1] += mx * 0.15
        camera_rot[0] += my * 0.15
        camera_rot[0] = max(-80, min(80, camera_rot[0]))

        # WASD 이동
        keys = pygame.key.get_pressed()
        speed = 4.0 * dt
        rad_yaw = math.radians(camera_rot[1])

        dx, dz = 0, 0
        if keys[pygame.K_w]:
            dx += math.sin(rad_yaw) * speed
            dz -= math.cos(rad_yaw) * speed
        if keys[pygame.K_s]:
            dx -= math.sin(rad_yaw) * speed
            dz += math.cos(rad_yaw) * speed
        if keys[pygame.K_a]:
            dx -= math.cos(rad_yaw) * speed
            dz -= math.sin(rad_yaw) * speed
        if keys[pygame.K_d]:
            dx += math.cos(rad_yaw) * speed
            dz += math.sin(rad_yaw) * speed

        # 폐가 벽 충돌 경계
        new_x = max(-14.0, min(14.0, camera_pos[0] + dx))
        new_z = max(-14.0, min(9.0, camera_pos[2] + dz))
        camera_pos[0] = new_x
        camera_pos[2] = new_z

        # 살인마 추적 AI
        k_dx = camera_pos[0] - KILLER_POS[0]
        k_dz = camera_pos[2] - KILLER_POS[2]
        dist_killer = math.sqrt(k_dx**2 + k_dz**2)
        if dist_killer > 0:
            KILLER_POS[0] += (k_dx / dist_killer) * 2.2 * dt
            KILLER_POS[2] += (k_dz / dist_killer) * 2.2 * dt

        # 갑툭튀 요건 (살인마가 근접했을 때)
        if dist_killer < 1.8:
            jumpscare_active = True
            game_over = True

        # 탈출 문 도착 체크
        dist_door = math.sqrt((camera_pos[0] - DOOR_POS[0])**2 + (camera_pos[2] - DOOR_POS[2])**2)
        if dist_door < 2.0 and has_key:
            game_clear = True

    # 화면 렌더링
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # 카메라 적용
    glRotatef(camera_rot[0], 1, 0, 0)
    glRotatef(camera_rot[1], 0, 1, 0)
    glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])

    setup_lighting()

    # 1. 흉가 바닥 & 천장
    draw_cube([0, -0.5, 0], [15, 0.1, 15], [0.15, 0.1, 0.08])
    draw_cube([0, 3.5, 0], [15, 0.1, 15], [0.05, 0.05, 0.05])

    # 2. 폐가 벽면
    draw_cube([0, 1.5, -15], [15, 2, 0.2], [0.2, 0.18, 0.15])
    draw_cube([-15, 1.5, 0], [0.2, 2, 15], [0.2, 0.18, 0.15])
    draw_cube([15, 1.5, 0], [0.2, 2, 15], [0.2, 0.18, 0.15])

    # 3. 갇힌 출구 문 (초록색/붉은색)
    door_color = [0.0, 0.8, 0.2] if has_key else [0.6, 0.1, 0.1]
    draw_cube(DOOR_POS, [1.2, 1.5, 0.1], door_color)

    # 4. 바닥에 떨어진 열쇠 (황금색)
    if not has_key:
        draw_cube(KEY_POS, [0.15, 0.15, 0.15], [1.0, 0.8, 0.0])

    # 5. 추적해오는 살인마 (붉은 눈의 괴물)
    draw_cube(KILLER_POS, [0.5, 1.2, 0.5], [0.3, 0.0, 0.0])
    draw_cube([KILLER_POS[0], KILLER_POS[1] + 0.8, KILLER_POS[2] + 0.4], [0.1, 0.1, 0.1], [1.0, 0.0, 0.0])

    # 2D UI 및 점프스케어 렌더링
    glDisable(GL_LIGHTING)
    
    if jumpscare_active:
        # 깜짝 놀래키는 화면 효과 (붉은 깜빡임)
        glClearColor(random.choice([0.8, 0.0]), 0.0, 0.0, 1.0)
        render_text("살인마에게 잡혔습니다! [ESC로 종료]", (WIDTH//2 - 180, HEIGHT//2))
    elif game_clear:
        render_text("폐가 탈출 성공! [ESC로 종료]", (WIDTH//2 - 150, HEIGHT//2))
    else:
        glClearColor(0.0, 0.0, 0.0, 1.0)
        state_text = "열쇠 획득 완료! 문으로 가세요!" if has_key else "열쇠를 찾으세요 (가까이서 F키)"
        render_text(f"[F] 손전등 토글 / 상호작용 | {state_text}", (20, 20))

    pygame.display.flip()
streamlit
pygame
PyOpenGL
PyOpenGL_accelerate
