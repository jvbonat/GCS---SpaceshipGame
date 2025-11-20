##############################################################
###               S P A C E     E S C A P E                ###
##############################################################
###                  versao Alpha 0.6                      ###
##############################################################

import pygame
import random
import os
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
pygame.display.set_caption("🚀 Space Escape")

ASSETS = {
    "background1": "fundo_espacial.png",
    "background2": "fundo_espacial_fase2.jpg",
    "background3": "fundo_espacial_fase3.png",

    "player": "nave001.png",
    "meteor": "meteoro001.png",
    "meteor_life": "meteoro_vida.png",

    "sound_point": "classic-game-action-positive-5-224402.mp3",
    "sound_hit": "stab-f-01-brvhrtz-224599.mp3",

    "music1": "distorted-future-363866.mp3",
    "music2": "game-gaming-background-music-385611.mp3",
    "music3": "distorted-future-363866.mp3"
}

WHITE = (255, 255, 255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def load_image(filename, color, size=None):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    surf = pygame.Surface(size or (50, 50))
    surf.fill(color)
    return surf

# backgrounds
backgrounds = [
    load_image(ASSETS["background1"], WHITE, (WIDTH, HEIGHT)),
    load_image(ASSETS["background2"], WHITE, (WIDTH, HEIGHT)),
    load_image(ASSETS["background3"], WHITE, (WIDTH, HEIGHT)),
]

player_img = load_image(ASSETS["player"], (0, 0, 255), (80, 60))
meteor_img = load_image(ASSETS["meteor"], (255, 0, 0), (40, 40))
meteor_life_img = load_image(ASSETS["meteor_life"], (0, 255, 0), (40, 40))

def load_sound(path):
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

sound_point = load_sound(ASSETS["sound_point"])
sound_hit = load_sound(ASSETS["sound_hit"])

music_tracks = [ASSETS["music1"], ASSETS["music2"], ASSETS["music3"]]

def play_music(index):
    if os.path.exists(music_tracks[index]):
        pygame.mixer.music.load(music_tracks[index])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

# ----------------------------- INTRO SCREEN -----------------------------
font = pygame.font.Font(None, 48)

def intro_screen():
    running = True
    while running:
        screen.fill((10, 10, 10))
        text = font.render("PRESS ENTER TO START", True, WHITE)
        screen.blit(text, (200, 270))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

intro_screen()

# ----------------------------- GAME VARIABLES -----------------------------
player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 60))
player_speed = 7

meteor_list = []
meteor_types = []

for _ in range(7):
    x = random.randint(0, WIDTH - 40)
    y = random.randint(-600, -40)
    meteor_types.append("life" if random.random() < 0.10 else "normal")
    meteor_list.append(pygame.Rect(x, y, 40, 40))

meteor_speeds = [random.randint(3, 8) for _ in range(7)]

score = 0
lives = 3
phase = 1
clock = pygame.time.Clock()
font_small = pygame.font.Font(None, 36)

play_music(0)

# ---------- NOVAS FUNCIONALIDADES ----------
invulnerable = False
invuln_end_time = 0

blink_timer = 0        # nave piscando
blink_state = True     # alternar visibilidade

paused = False         # PAUSE
meteor_speed_bonus = 0

# ----------------------------- GAME LOOP -----------------------------
running = True
while running:
    clock.tick(FPS)

    # PAUSE
    if paused:
        pause_text = font.render("JOGO PAUSADO - Pressione P", True, WHITE)
        screen.blit(pause_text, (130, 260))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False
        continue

    screen.blit(backgrounds[phase - 1], (0, 0))

    # ------ EXIT EVENTS ------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = True

    # movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
        player_rect.y += player_speed

    # remove invulnerabilidade quando acabar
    if invulnerable and time.time() > invuln_end_time:
        invulnerable = False
        blink_timer = 0

    # meteors
    for i, meteor in enumerate(meteor_list):
        meteor.y += meteor_speeds[i] + meteor_speed_bonus


        if meteor.y > HEIGHT:
            meteor.y = random.randint(-300, -40)
            meteor.x = random.randint(0, WIDTH - 40)
            meteor_types[i] = "life" if random.random() < 0.10 else "normal"
            score += 1
            if sound_point:
                sound_point.play()

        if meteor.colliderect(player_rect):
            if not invulnerable:  # só toma dano se não invulnerável
                if meteor_types[i] == "life":
                    lives += 1
                else:
                    lives -= 1
                    invulnerable = True
                    invuln_end_time = time.time() + 2  # 2 segundos invencível
                    blink_timer = 30  # piscadas
                    if sound_hit:
                        sound_hit.play()

            meteor.y = random.randint(-200, -40)
            meteor.x = random.randint(0, WIDTH - 40)

    # fases
    if score >= 20 and phase == 1:
        phase = 2
        play_music(1)
        for i in range(len(meteor_speeds)):
            meteor_speeds[i] += 2   # aumenta velocidade real

    if score >= 50 and phase == 2:
        phase = 3
        play_music(2)
        for i in range(len(meteor_speeds)):
            meteor_speeds[i] += 1  # aumenta velocidade real


    # --------- DESENHAR NAVE (piscando se invulnerável) ----------
    if invulnerable:
        blink_state = not blink_state
        if blink_state:
            screen.blit(player_img, player_rect)
    else:
        screen.blit(player_img, player_rect)

    # meteors
    for i, meteor in enumerate(meteor_list):
        img = meteor_life_img if meteor_types[i] == "life" else meteor_img
        screen.blit(img, meteor)

    # HUD
    text = font_small.render(f"Pontos: {score}   Vidas: {lives}   Fase: {phase}", True, WHITE)
    screen.blit(text, (10, 10))

    if lives <= 0:
        running = False

    pygame.display.flip()

# ----------------------------- END SCREEN -----------------------------
pygame.mixer.music.stop()

screen.fill((0, 0, 0))

msg = "VOCÊ VENCEU!" if score >= 80 else "GAME OVER!"
end_text = font.render(msg, True, WHITE)
score_text = font.render(f"Pontuação Final: {score}", True, WHITE)

screen.blit(end_text, (250, 250))
screen.blit(score_text, (250, 300))

pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            waiting = False

pygame.quit()
