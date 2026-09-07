import pygame
import random
import sys

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 320, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("피아노 타일 게임")

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (255, 0, 0)

# 게임 변수
LANE_WIDTH = WIDTH // 4
TILE_HEIGHT = 120
clock = pygame.time.Clock()

def run_game():
    score = 0
    speed = 4
    tiles = []
    game_over = False

    # 초기 타일 생성
    for i in range(4):
        col = random.randint(0, 3)
        tiles.append(pygame.Rect(col * LANE_WIDTH, (3 - i) * TILE_HEIGHT - TILE_HEIGHT, LANE_WIDTH, TILE_HEIGHT))

    while True:
        screen.fill(GRAY)

        # 레인 구분선 그리기
        for i in range(1, 4):
            pygame.draw.line(screen, WHITE, (i * LANE_WIDTH, 0), (i * LANE_WIDTH, HEIGHT), 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mx, my = event.pos
                hit = False
                for tile in tiles[:]:
                    if tile.collidepoint(mx, my):
                        tiles.remove(tile)
                        score += 1
                        hit = True
                        if score % 5 == 0:
                            speed += 0.5
                        break
                
                # 빈 공간을 누르면 게임 오버
                if not hit:
                    game_over = True

            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:  # R키 누르면 재시작
                    run_game()

        if not game_over:
            # 타일 이동 및 로직
            for tile in tiles:
                tile.y += speed

            # 가장 아래 타일이 화면을 벗어나면 게임 오버
            if tiles and tiles[0].y >= HEIGHT:
                game_over = True

            # 새 타일 추가
            if tiles and tiles[-1].y > 0:
                col = random.randint(0, 3)
                new_y = tiles[-1].y - TILE_HEIGHT
                tiles.append(pygame.Rect(col * LANE_WIDTH, new_y, LANE_WIDTH, TILE_HEIGHT))

        # 타일 그리시
        for tile in tiles:
            pygame.draw.rect(screen, BLACK, tile)

        # 점수 표시
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # 게임 오버 화면
        if game_over:
            over_font = pygame.font.SysFont(None, 48)
            over_text = over_font.render("GAME OVER", True, RED)
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
            screen.blit(restart_text, (WIDTH // 2 - 110, HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(60)

run_game()
