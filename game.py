import cv2
import tkinter as tk
import mediapipe as mp
import math
import time
import pygame
import random
import os

FPS = 120
WIDTH = 1000
HEIGHT = 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# 難度調整
rock_quantity = 0
speed_y_upper = 0
speed_y_lower = 0
upgrading_time = 0
shoot_interval = 0
percentage = 0
difficulty = 0
ammo_infinity = False

# 遊戲初始化&創建視窗
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("星際戰艦生存戰")
clock = pygame.time.Clock()

# 載入圖片
background_img = pygame.image.load(os.path.join("img", "background.jpg")).convert()
player_img = pygame.image.load(os.path.join("img", "universeship.png")).convert()
# player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(10):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
    # rock_imgs.append(pygame.transform.scale(rock_original_imgs, (random.randint(50,150), random.randint(38,114))))
fat_guy_img = pygame.image.load(os.path.join("img", "fat_guy.png")).convert()
fat_guy_img = pygame.transform.scale(fat_guy_img, (297, 446))
alien_img = pygame.image.load(os.path.join("img", "alien_light.png"))
winner_img = pygame.image.load(os.path.join("img", "winner.png"))
loser_img = pygame.transform.scale(fat_guy_img, (297, 297))

explosion_animation = {'Large_Explosion': [], "Small_Explosion": [], 'Player': [], 'Alien': []}

for i in range(9):
    explosion_img = pygame.image.load(os.path.join("img", f"expl{i}.png"))
    explosion_img.set_colorkey(BLACK)
    explosion_animation['Large_Explosion'].append(pygame.transform.scale(explosion_img, (75, 75)))
    explosion_animation['Small_Explosion'].append(pygame.transform.scale(explosion_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    explosion_animation['Player'].append(player_expl_img)

for i in range(10):
    alien_explosion_img = pygame.image.load(os.path.join("img", f"alien_explosion{i}.png"))
    alien_explosion_img.set_colorkey(BLACK)
    explosion_animation['Alien'].append(alien_explosion_img)

ammo_image = pygame.image.load(os.path.join("img", "ammo.png")).convert()
ammo_image = pygame.transform.scale(ammo_image, (60, 60))
power_imgs = {'shield': pygame.image.load(os.path.join("img", "shield.png")).convert(),
              'gun': pygame.image.load(os.path.join("img", "gun.png")).convert(),
              'ammo': ammo_image}
alien_attack_img = pygame.image.load(os.path.join("img", "alien_attack.png")).convert()

# 載入音樂、音效
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
reload_sound = pygame.mixer.Sound(os.path.join("sound", "reload.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
explosion_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.3)
font_name = os.path.join("font.ttf")

# OpenCV Declarations
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# 全域變數
x2 = 0
y2 = 0
x_wrist2 = 0
y_wrist2 = 0
length2 = 0
slope = 0
shoot = False
y_shoot_upper = 0
y_shoot_lower = 0
shoot_time = 0
gun_time = 0
now = 0
shoot_now = 0
ammo = 0
F_A_collide = False
Alien_x = 0
Alien_y = 0
times = 0
alien_die = False
is_replay = False


# 中文&英文文字顯示
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, False, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


# 產生隕石
def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)


# 繪製生命條
def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0

    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# 繪製外星人生命條
def draw_alien_health(surf, hp, x, y):
    if hp < 0:
        hp = 0

    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 400) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# 繪製生命數
def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# 開始畫面
def draw_init():
    font = pygame.font.SysFont("Arial", 48)
    screen.blit(background_img, (0, 0))
    draw_text(screen, "星際戰艦生存戰!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '操作方式', 48, WIDTH / 2, HEIGHT * 25 / 64)
    draw_text(screen, '← →移動飛船 空白鍵發射子彈', 25, WIDTH / 2, HEIGHT * 16 / 32)
    draw_text(screen, '雙手作虛擬方向盤移動飛船 大拇指控制子彈發射', 25, WIDTH / 2, HEIGHT * 18 / 32)
    draw_text(screen, '請選擇難度開始遊戲', 25, WIDTH / 2, HEIGHT * 20 / 32)
    # draw_text(screen, '按任意鍵開始遊戲!', 18, WIDTH / 2, HEIGHT * 3 / 4)

    # 難度按鈕顯示
    text_easy = font.render("  easy  ", True, WHITE)
    text_easy_rect = text_easy.get_rect(center=(WIDTH / 4, HEIGHT * 3 / 4))
    text_normal = font.render("  normal  ", True, WHITE)
    text_normal_rect = text_normal.get_rect(center=(WIDTH / 2, HEIGHT * 3 / 4))
    text_hard = font.render("  hard  ", True, WHITE)
    text_hard_rect = text_hard.get_rect(center=(WIDTH * 3 / 4, HEIGHT * 3 / 4))

    pygame.display.update()

    waiting = True
    button_clicked = False

    # 自訂函式內的全域宣告
    global alien_die
    global rock_quantity
    global speed_y_upper
    global speed_y_lower
    global upgrading_time
    global shoot_interval
    global percentage
    global ammo_infinity
    global difficulty
    alien_die = False

    # 待機畫面迴圈
    while waiting:
        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                return True

            # 取得滑鼠點擊事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 簡單模式難度調整
                if text_easy_rect.collidepoint(event.pos):
                    button_clicked = True
                    rock_quantity = 8
                    speed_y_upper = 3
                    speed_y_lower = 1
                    upgrading_time = 10000
                    shoot_interval = 200
                    percentage = 0.6
                    ammo_infinity = True
                    difficulty = 1

                # 普通模式難度調整
                elif text_normal_rect.collidepoint(event.pos):
                    button_clicked = True
                    rock_quantity = 14
                    speed_y_upper = 6
                    speed_y_lower = 2
                    upgrading_time = 5000
                    shoot_interval = 500
                    percentage = 0.85
                    ammo_infinity = False
                    difficulty = 2

                # 困難模式難度調整
                elif text_hard_rect.collidepoint(event.pos):
                    button_clicked = True
                    rock_quantity = 20
                    speed_y_upper = 10
                    speed_y_lower = 6
                    upgrading_time = 2500
                    shoot_interval = 1000
                    percentage = 0.9
                    ammo_infinity = False
                    difficulty = 3

                else:
                    button_clicked = False

        # 按鈕繪製
        pygame.draw.rect(screen, (106, 90, 205), text_easy_rect, border_radius=15)
        screen.blit(text_easy, text_easy_rect)
        pygame.draw.rect(screen, (106, 90, 205), text_normal_rect, border_radius=15)
        screen.blit(text_normal, text_normal_rect)
        pygame.draw.rect(screen, (106, 90, 205), text_hard_rect, border_radius=15)
        screen.blit(text_hard, text_hard_rect)

        if button_clicked:
            waiting = False

        pygame.display.update()


# 勝利待機畫面
def draw_victory_end(surf):
    img = winner_img
    img_rect = img.get_rect()
    img_rect.centerx = WIDTH / 2
    img_rect.centery = HEIGHT * 1 / 4
    font = pygame.font.SysFont("Arial", 48)
    screen.blit(background_img, (0, 0))

    # 功能按鈕顯示
    draw_text(screen, "VICTORY", 64, WIDTH / 2, HEIGHT / 2)
    replay = font.render("  restart  ", True, WHITE)
    replay_rect = replay.get_rect(center=(WIDTH / 4, HEIGHT * 3 / 4))
    exit_game = font.render("  left game  ", True, WHITE)
    exit_game_rect = exit_game.get_rect(center=(WIDTH * 3 / 4, HEIGHT * 3 / 4))

    pygame.display.update()

    waiting = True
    button_clicked = False

    # 自訂函式內的全域宣告
    global is_replay
    global show_init

    while waiting:
        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():

            # 離開視窗
            if event.type == pygame.QUIT:
                pygame.quit()
                return True

            # 取得滑鼠點擊事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    button_clicked = True
                    is_replay = True
                    show_init = True

                elif exit_game_rect.collidepoint(event.pos):
                    button_clicked = True
                    pygame.quit()

                else:
                    button_clicked = False

        # 按鈕繪製
        pygame.draw.rect(screen, (106, 90, 205), replay_rect, border_radius=15)
        screen.blit(replay, replay_rect)
        pygame.draw.rect(screen, (106, 90, 205), exit_game_rect, border_radius=15)
        screen.blit(exit_game, exit_game_rect)
        surf.blit(img, img_rect)

        if button_clicked:
            waiting = False

        pygame.display.update()


# 失敗待機畫面
def draw_lose_end(surf):
    img = loser_img
    img_rect = img.get_rect()
    img_rect.centerx = WIDTH / 2
    img_rect.centery = HEIGHT * 1 / 4
    font = pygame.font.SysFont("Arial", 48)

    # 功能按鈕顯示
    draw_text(screen, "HAHA! LOSER~", 64, WIDTH / 2, HEIGHT / 2)
    replay = font.render("  restart  ", True, WHITE)
    replay_rect = replay.get_rect(center=(WIDTH / 4, HEIGHT * 3 / 4))
    exit_game = font.render("  left game  ", True, WHITE)
    exit_game_rect = exit_game.get_rect(center=(WIDTH * 3 / 4, HEIGHT * 3 / 4))
    pygame.display.update()

    waiting = True
    button_clicked = False

    # 自訂函式內的全域宣告
    global is_replay
    global show_init

    while waiting:
        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():

            # 離開視窗
            if event.type == pygame.QUIT:
                pygame.quit()
                return True

            # 取得滑鼠點擊事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    button_clicked = True
                    is_replay = True
                    show_init = True

                elif exit_game_rect.collidepoint(event.pos):
                    button_clicked = True
                    pygame.quit()

                else:
                    button_clicked = False

        # 按鈕繪製
        pygame.draw.rect(screen, (106, 90, 205), replay_rect, border_radius=15)
        screen.blit(replay, replay_rect)
        pygame.draw.rect(screen, (106, 90, 205), exit_game_rect, border_radius=15)
        screen.blit(exit_game, exit_game_rect)
        surf.blit(img, img_rect)

        if button_clicked:
            waiting = False

        pygame.display.update()


# 玩家物件宣告
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.transform.scale(player_img, (50, 38))
        self.image = pygame.transform.scale(player_img, (100, 76))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 32
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = 200
        self.rect.y = 200
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 100
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0
        self.shoot_time = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.ammo = 0
        if ammo_infinity:
            self.ammo = 100000000000000
        elif difficulty == 2:
            self.ammo = 120
        elif difficulty == 3:
            self.ammo = 30

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > upgrading_time:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1300:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 100

        key_pressed = pygame.key.get_pressed()

        if key_pressed[pygame.K_SPACE] and now - self.shoot_time > shoot_interval:
            player.shoot()
            self.gun_time = now

        # 以斜率判斷右轉
        if slope < 0:
            if slope * 10 > -40:
                self.rect.x -= slope * 10

        # 以斜率判斷左轉
        if slope > 0:
            if slope * 10 < 40:
                self.rect.x -= slope * 10

        # 鍵盤控制
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += 6
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= 6
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += 6
        if key_pressed[pygame.K_UP]:
            self.rect.y -= 6

        # if key_pressed[pygame.K_SPACE]:
        #     player.shoot()
        if not self.hidden:
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.top < 0:
                self.rect.top = 0

        global ammo
        ammo = self.ammo

    # 射擊函式
    def shoot(self):
        if not self.hidden and self.ammo >= 1:
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                if difficulty == 2:
                    self.ammo -= 1
                if difficulty == 3:
                    self.ammo -= 1
                # shoot_sound.play()

            elif self.gun == 2 and self.ammo >= 2:
                bullet1 = Bullet(self.rect.left + 30, self.rect.centery - 30)
                bullet2 = Bullet(self.rect.right - 30, self.rect.centery - 30)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                if difficulty == 2:
                    self.ammo -= 1
                if difficulty == 3:
                    self.ammo -= 2
                # shoot_sound.play()

            elif self.gun >= 3 and self.ammo >= 2:
                bullet1 = Bullet(self.rect.left + 10, self.rect.centery)
                bullet2 = Bullet(self.rect.centerx, self.rect.top)
                bullet3 = Bullet(self.rect.right - 10, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(bullet3)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bullet3)
                if difficulty == 2:
                    self.ammo -= 1
                if difficulty == 3:
                    self.ammo -= 3

                # shoot_sound.play()
        self.shoot_time = pygame.time.get_ticks()

    # 損失一條命時會將戰艦暫時隱藏
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 500)

    # 增加射擊光束數量
    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

    # 增加彈藥
    def reload(self):
        self.ammo += 40


# 石頭物件宣告
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_origin = random.choice(rock_imgs)
        self.image_origin = pygame.transform.scale(self.image_origin,
                                                   (random.randint(50, 200), random.randint(38, 152)))
        self.image_origin.set_colorkey(BLACK)
        self.image = self.image_origin.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.65 / 2
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedx = random.randrange(-5, 5)
        self.speedy = random.randrange(speed_y_lower, speed_y_upper)
        self.total_degree = 0
        self.rotate_degree = random.randrange(-4, 4)
        self.mask = pygame.mask.from_surface(self.image)

    # 圖片旋轉
    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_origin, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedx = random.randrange(-3, 3)
            self.speedy = random.randrange(2, 10)


# 胖胖物件宣告
class Fat_guy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        global fat_guy_show

        numbers = list(range(-15, 15))
        numbers.remove(0)
        num_list = list(map(int, numbers))
        result_x = random.choice(num_list)
        result_y = random.choice(num_list)

        self.image_origin = fat_guy_img
        self.image_origin = pygame.transform.scale(self.image_origin, (149, 172))
        self.image_origin.set_colorkey(BLACK)
        self.image = self.image_origin.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.65 / 2
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = WIDTH - 300
        self.rect.y = -400
        self.speedx = int(result_x)
        self.speedy = int(result_y)
        self.total_degree = 0
        self.rotate_degree = 5

    # 圖片旋轉
    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_origin, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        global fat_guy_temp
        self.rotate()
        fat_guy_limit = 0
        if fat_guy_show and fat_guy_limit == 0 and fat_guy_temp == 0:
            self.rect.y = 100
            fat_guy_limit += 1
            fat_guy_temp += 1

        # 當胖胖和外星人碰撞後將不斷更新繼承外星人座標
        if F_A_collide:
            self.rect.x = Alien_x - 50
            self.rect.y = Alien_y - 150

        # 邊緣碰撞轉向判斷
        if not F_A_collide:
            if self.rect.right > WIDTH + 200:
                self.speedx = self.speedx * (-1)
            if self.rect.left < -200:
                self.speedx = self.speedx * (-1)
            self.rect.x += self.speedx
            if self.rect.top < -200:
                self.speedy = self.speedy * (-1)
            if self.rect.bottom > HEIGHT + 200:
                self.speedy = self.speedy * (-1)
            self.rect.y += self.speedy

# 外星人物件宣告
class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        global alien_show
        self.image = pygame.transform.scale(alien_img, (200, 200))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.radius = self.rect.width * 0.5
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = WIDTH / 2
        self.rect.y = -300
        self.speedx = random.randrange(-15, 15)
        self.health = 400

    def hide(self):
        global alien_show
        global alien_die
        self.rect.center = (WIDTH / 2, HEIGHT + 500)
        alien_show = False
        alien_die = True

    def attack(self):
        laser = Laser(self.rect.centerx, self.rect.bottom)
        all_sprites.add(laser)
        lasers.add(laser)

    def update(self):
        global Alien_x
        global Alien_y
        global times
        alien_limit = 0
        if alien_show:
            if alien_limit == 0:
                self.rect.y = 75
                alien_limit += 1
            if times % 40 == 0:
                for i in range(0, random.randint(1, 3)):
                    self.attack()
            if times % 10 == 0:
                self.speedx = random.randrange(-15, 15)
            if self.rect.right > WIDTH + 200:
                self.speedx = self.speedx * (-1)
            if self.rect.left < -200:
                self.speedx = self.speedx * (-1)
            self.rect.x += self.speedx
            Alien_x = self.rect.x
            Alien_y = self.rect.y


# 外星人攻擊物件宣告
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        degree = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170]
        # cos
        move_x = [-0.9848, -0.9396, -0.8660, -0.7660, -0.6427, -0.5, -0.3420, -0.1736, 0, 0.1736, 0.3420, 0.5,
                  0.6427, 0.7660, 0.8660, 0.9396, 0.9848]
        # sin
        move_y = [0.1736, 0.3420, 0.5, 0.6427, 0.7660, 0.8660, 0.9396, 0.9848, 1, 0.9848, 0.9396, 0.8660, 0.7660,
                  0.6427, 0.5, 0.3420, 0.1736]
        pygame.sprite.Sprite.__init__(self)
        self.image_origin = pygame.transform.scale(alien_attack_img, (83, 50))
        self.image_origin.set_colorkey(BLACK)
        self.image = self.image_origin.copy()
        self.rect = self.image.get_rect()
        num = random.randint(0, 16)
        self.rotate_degree = 60
        self.image = pygame.transform.rotate(self.image_origin, degree[num])
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.centerx = x
        self.rect.centery = y
        self.speedx = move_x[num] * 10
        self.speedy = move_y[num] * 10
        self.damage = 50

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.bottom < 0 and self.rect.left > WIDTH + 50 and self.rect.right < -50:
            self.kill()


# 子彈物件宣告
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = -10
        self.damage = 20

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


# 爆炸動畫
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                self.image = explosion_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


# 回血和加強攻擊
class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun', 'ammo'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 8

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


# 根據兩點的座標，計算角度
def vector_2d_angle(v1, v2):
    # 座標
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]

    # noinspection PyBroadException
    # 向量內積求角度
    try:
        angle_ = math.degrees(math.acos(
            (v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle_ = 180
    return angle_


# 根據傳入的 21 個節點座標，得到該手指的角度
def hand_angle(hand_):
    angle_list = []

    # thumb 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[2][0])), (int(hand_[0][1]) - int(hand_[2][1]))),
        ((int(hand_[3][0]) - int(hand_[4][0])), (int(hand_[3][1]) - int(hand_[4][1])))
    )

    # 判斷手心手背
    # if (round((int(hand_[0][0]) - int(hand_[2][0])), 0)) < 0:
    #     print("現在辨識為手背")
    # else:
    #     print("現在辨識為手心")

    angle_list.append(angle_)

    # index 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[6][0])), (int(hand_[0][1]) - int(hand_[6][1]))),
        ((int(hand_[7][0]) - int(hand_[8][0])), (int(hand_[7][1]) - int(hand_[8][1])))
    )
    angle_list.append(angle_)

    # middle 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[10][0])), (int(hand_[0][1]) - int(hand_[10][1]))),
        ((int(hand_[11][0]) - int(hand_[12][0])), (int(hand_[11][1]) - int(hand_[12][1])))
    )
    angle_list.append(angle_)

    # ring 無名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[14][0])), (int(hand_[0][1]) - int(hand_[14][1]))),
        ((int(hand_[15][0]) - int(hand_[16][0])), (int(hand_[15][1]) - int(hand_[16][1])))
    )
    angle_list.append(angle_)

    # pink 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[18][0])), (int(hand_[0][1]) - int(hand_[18][1]))),
        ((int(hand_[19][0]) - int(hand_[20][0])), (int(hand_[19][1]) - int(hand_[20][1])))
    )
    angle_list.append(angle_)

    # 輸出手指間角度列表
    for num in range(0, 5):
        angle_list[num] = round(angle_list[num], 2)

    print("手指間角度: " + str(angle_list))
    return angle_list


# 根據手指角度的串列內容，返回對應的手勢名稱
def hand_pos(fingers_angle):
    f1 = fingers_angle[0]  # 大拇指角度
    f2 = fingers_angle[1]  # 食指角度
    f3 = fingers_angle[2]  # 中指角度
    f4 = fingers_angle[3]  # 無名指角度
    f5 = fingers_angle[4]  # 小拇指角度
    # print(finger_angle)
    # 小於 90 表示手指伸直，大於等於 90 表示手指捲縮
    if f1 < 90 and f2 >= 90 and f3 >= 90 and f4 >= 90 and f5 >= 90:
        return 'good'
    elif f1 >= 90 and f2 >= 90 and f3 < 90 and f4 >= 90 and f5 >= 90:
        return 'fuck!!!'
    elif f1 < 90 and f2 < 90 and f3 >= 90 and f4 >= 90 and f5 < 90:
        return 'ROCK!'
    elif f1 >= 90 and f2 >= 90 and f3 >= 90 and f4 >= 90 and f5 >= 90:
        return '0'
    elif f1 >= 90 and f2 >= 90 and f3 >= 90 and f4 >= 90 and f5 < 90:
        return 'pink'
    elif f1 >= 90 and f2 < 90 and f3 >= 90 and f4 >= 90 and f5 >= 90:
        return '1'
    elif f1 >= 90 and f2 < 90 and f3 < 90 and f4 >= 90 and f5 >= 90:
        return '2'
    elif f1 >= 90 and f2 >= 90 and f3 < 90 and f4 < 90 and f5 < 90:
        return 'ok'
    elif f1 < 90 and f2 >= 90 and f3 < 90 and f4 < 90 and f5 < 90:
        return 'ok'
    elif f1 >= 90 and f2 < 90 and f3 < 90 and f4 < 90 and f5 > 90:
        return '3'
    elif f1 >= 90 and f2 < 90 and f3 < 90 and f4 < 90 and f5 < 90:
        return '4'
    elif f1 < 90 and f2 < 90 and f3 < 90 and f4 < 90 and f5 < 90:
        return '5'
    elif f1 < 90 and f2 >= 90 and f3 >= 90 and f4 >= 90 and f5 < 90:
        return '6'
    elif f1 < 90 and f2 < 90 and f3 >= 90 and f4 >= 90 and f5 >= 90:
        return '7'
    elif f1 < 90 and f2 < 90 and f3 < 90 and f4 >= 90 and f5 >= 90:
        return '8'
    elif f1 < 90 and f2 < 90 and f3 < 90 and f4 < 90 and f5 >= 90:
        return '9'
    else:
        return ''


cap = cv2.VideoCapture(0)  # 讀取攝影機
fontFace = cv2.FONT_HERSHEY_SIMPLEX  # 印出文字的字型
lineType = cv2.LINE_AA  # 印出文字的邊框
pTime = 0  # 開始時間初始化
cTime = 0  # 目前時間初始化

# 背景音樂循環播放
pygame.mixer.music.play(-1)

show_init = True
running = True

# mediapipe
with mp_hands.Hands(
        max_num_hands=2,  # 偵測手掌數量
        model_complexity=1,  # 模型複雜度
        min_detection_confidence=0.8,  # 最小偵測自信度
        min_tracking_confidence=0.8) as hands:  # 最小追蹤自信度

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    w, h = 640, 480  # 影像尺寸 width:640, height:480
    # 遊戲迴圈
    while running and cap.isOpened():
        ret, img = cap.read()
        img = cv2.resize(img, (w, h))  # 縮小尺寸，加快處理效率
        times += 1

        # 待機畫面
        if show_init:
            close = draw_init()
            score = 0
            if close:
                break
            show_init = False

            # 角色與群組
            all_sprites = pygame.sprite.Group()
            rocks = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            lasers = pygame.sprite.Group()
            powers = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            fat_guy = Fat_guy()
            alien = Alien()
            fat_guy_show = False
            alien_show = False
            fat_guy_temp = 0
            for i in range(rock_quantity):
                new_rock()

        # 2000分後肥肥出現
        if not fat_guy_show and score > 2000:
            all_sprites.add(fat_guy)
            fat_guy_show = True
            fat_guy_temp = 0

        # 3000分後外星人出現
        if not alien_show and score > 3000 and not alien_die:
            all_sprites.add(alien)
            alien_show = True

        clock.tick(FPS)  # Frames per second

        # 影像翻轉
        img = cv2.flip(img, 1)

        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 轉換成 RGB 色彩
        results = hands.process(img2)  # 偵測手勢

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_points = []  # 記錄手指節點座標的串列

                for i in hand_landmarks.landmark:
                    # 將 21 個節點換算成座標，記錄到 finger_points
                    x = i.x * w
                    y = i.y * h
                    x1 = hand_landmarks.landmark[4].x * w  # 取得大拇指末端 x 座標
                    y1 = hand_landmarks.landmark[4].y * h  # 取得大拇指末端 y 座標

                    x_wrist1 = hand_landmarks.landmark[0].x * w  # 取得手掌末端 x 座標
                    y_wrist1 = hand_landmarks.landmark[0].y * h  # 取得手掌末端 y 座標
                    z_wrist1 = hand_landmarks.landmark[0].z

                    finger_points.append((x, y))

                    y_shoot_upper = hand_landmarks.landmark[4].y * h
                    y_shoot_lower = hand_landmarks.landmark[6].y * h

                    # if times % 2 == 0:
                    #     y_move1 =

                    if y_shoot_lower - y_shoot_upper > 40:
                        shoot = True
                        shoot_time = pygame.time.get_ticks()
                    else:
                        shoot = False
                    now = pygame.time.get_ticks()
                    key_pressed = pygame.key.get_pressed()

                    # 射擊間隔時間
                    if abs(now - shoot_time) > shoot_interval:
                        player.shoot()
                        shoot_time = now
                    # print(y_shoot_lower - y_shoot_upper)
                    # print(shoot_time - now)

                # noinspection PyBroadException
                # 計算斜率並輸出
                try:
                    m = round(((y1 - y2) / (x1 - x2) * (-1)), 2)
                except:
                    pass

                slope = m
                print("斜率: " + str(m))
                x1_output = round(x1, 0)
                y1_output = round(y1, 0)
                print("大拇指末端座標: " + str(x1_output) + ", " + str(y1_output))
                print("z軸相對座標: " + str(z_wrist1))

                # 計算手掌間距離並輸出
                length1 = math.sqrt((abs(x_wrist1 - x_wrist2) * abs(x_wrist1 - x_wrist2)) + (
                        abs(y_wrist1 - y_wrist2) * abs(y_wrist1 - y_wrist2)))
                length1_output = round(length1, 2)
                print("手掌間距離: " + str(length1_output))

                # 計算雙手手掌間距離和前一次數據差值並輸出
                length_gap = round((length1 - length2), 2)
                print("雙手手掌間距離和前一次數據差值: " + str(length_gap))

                x2 = x1
                y2 = y1
                # y_move2 = y_move1
                x_wrist2 = x_wrist1
                y_wrist2 = y_wrist1
                length2 = length1

                # 以斜率判斷轉彎方向
                if m > 0:
                    cv2.putText(img, "Turn Left", (30, 120), fontFace, 2, (255, 255, 255), 10, lineType)
                else:
                    cv2.putText(img, "Turn Right", (30, 120), fontFace, 2, (255, 255, 255), 10, lineType)

                if finger_points:
                    finger_angle = hand_angle(finger_points)  # 計算手指角度，回傳長度為 5 的串列
                    # print(finger_angle)  # 印出角度
                    text = hand_pos(finger_angle)  # 取得手勢所回傳的內容
                    # cv2.putText(img, text, (30, 120), fontFace, 5, (255, 255, 255), 10, lineType)  # 印出文字

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 將節點和骨架繪製到影像中
                mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        # 將幀率顯示在影像上
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (600, 30), fontFace, 1, (0, 255, 0), 2, lineType)

        cv2.imshow('finger_recognition', img)

        # 按下esc結束程式
        if cv2.waitKey(1) & 0xFF == 27:
            break

        # 取得輸入
        key_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         player.shoot()

        # 更新所有角色
        all_sprites.update()

        # 判斷石頭和子彈相撞
        hits = pygame.sprite.groupcollide(rocks, bullets, True, True)

        for hit in hits:
            random.choice(explosion_sounds).play()
            score += int(hit.radius) * 5
            explosion = Explosion(hit.rect.center, 'Large_Explosion')
            all_sprites.add(explosion)

            # 掉寶機率
            if random.random() > percentage:
                power = Power(hit.rect.center)
                all_sprites.add(power)
                powers.add(power)
            new_rock()

        # 判斷石頭和飛船相撞
        hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)

        for hit in hits:
            new_rock()
            explosion = Explosion(hit.rect.center, 'Small_Explosion')
            all_sprites.add(explosion)
            player.health -= hit.radius

            # 飛船爆炸動畫
            if player.health <= 0:
                death_expl = Explosion(player.rect.center, 'Player')
                all_sprites.add(death_expl)
                die_sound.play()
                player.lives -= 1

                if player.lives > 0:
                    player.health = 100
                player.hide()

        # 判斷掉落的寶物和飛船相撞
        hits = pygame.sprite.spritecollide(player, powers, True)
        for hit in hits:
            if hit.type == 'shield':
                player.health += 20

                if player.health > 100:
                    player.health = 100
                shield_sound.play()

            elif hit.type == 'gun':
                player.gunup()
                gun_sound.play()

            elif hit.type == 'ammo':
                player.reload()
                reload_sound.play()

        # 判斷博偉和外星人相撞
        hits = pygame.sprite.collide_circle(fat_guy, alien)
        if hits:
            # Fat and Alien collation
            F_A_collide = True

        # 判斷博偉和子彈相撞
        if difficulty != 1:
            hits = pygame.sprite.spritecollide(fat_guy, bullets, True, pygame.sprite.collide_circle)
            for hit in hits:
                player.health -= 20

                if player.health <= 0:
                    death_expl = Explosion(player.rect.center, 'Player')
                    all_sprites.add(death_expl)
                    die_sound.play()
                    player.lives -= 1

                    if player.lives > 0:
                        player.health = 100
                    player.hide()

        # 判斷外星人和子彈相撞
        if alien_show:
            hits = pygame.sprite.spritecollide(alien, bullets, True, pygame.sprite.collide_circle)
            for hit in hits:
                alien.health -= 20
                # print("外星人生命值:", alien.health)
                if alien.health <= 0 and alien_show:
                    explosion = Explosion(hit.rect.center, 'Alien')
                    all_sprites.add(explosion)
                    alien.hide()
                    F_A_collide = False

        # 判斷子彈和雷射光束相撞
        if alien_show:
            hits = pygame.sprite.groupcollide(lasers, bullets, False, True)

        # 判斷飛船和雷射光束相撞
        hits = pygame.sprite.spritecollide(player, lasers, True)
        for hit in hits:
            player.health -= 50

            if player.health <= 0:
                death_expl = Explosion(player.rect.center, 'Player')
                all_sprites.add(death_expl)
                die_sound.play()
                player.lives -= 1

                if player.lives > 0:
                    player.health = 100
                player.hide()

        slope = 0

        if player.lives <= 0 and not (death_expl.alive()):
            draw_lose_end(screen)

        # if is_replay == True:
        #     show_init = True

        if not show_init:
            if alien_die:
                draw_victory_end(screen)

        # 畫面顯示
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_health(screen, player.health, 25, 17)
        draw_alien_health(screen, alien.health, alien.rect.centerx - 50, alien.rect.top - 15)
        draw_text(screen, "HP", 14, 12, 11)
        draw_lives(screen, player.lives, player_mini_img, WIDTH - 110, 15)

        if player.ammo < 0:
            player.ammo = 0

        if difficulty == 1:
            draw_text(screen, "Ammo:∞", 24, WIDTH - 200, 10)
        if difficulty == 2:
            draw_text(screen, "Ammo:" + str(ammo), 24, WIDTH - 200, 10)
        if difficulty == 3:
            draw_text(screen, "Ammo:" + str(ammo), 24, WIDTH - 200, 10)
        pygame.display.update()

pygame.quit()
cap.release()
cv2.destroyAllWindows()
