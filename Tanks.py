# Пользовательский интерфейс
import pygame
from random import randint
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 32


shot_sound = pygame.mixer.Sound('sounds/shot.wav')
destroy_sound = pygame.mixer.Sound('sounds/destroy.wav')
dead = pygame.mixer.Sound('sounds/dead.wav')
engine_sound = pygame.mixer.Sound('sounds/engine.wav')
start_sound = pygame.mixer.Sound('sounds/level_start.mp3')
star_sound = pygame.mixer.Sound('sounds/star.wav')

start_sound_volume = 0.1

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)

imgBrick = pygame.image.load('images/block_brick.png')
imgTanks = [
    pygame.image.load('images/tank1.png'),
    pygame.image.load('images/tank2.png'),
    pygame.image.load('images/tank3.png'),
    pygame.image.load('images/tank4.png'),
    pygame.image.load('images/tank5.png'),
    pygame.image.load('images/tank6.png'),
    pygame.image.load('images/tank7.png'),
    pygame.image.load('images/tank8.png'),
    ]
imgBangs = [
    pygame.image.load('images/bang1.png'),
    pygame.image.load('images/bang2.png'),
    pygame.image.load('images/bang3.png'),
    ]
imgBonuses = [
    pygame.image.load('images/bonus_star.png'),
    pygame.image.load('images/bonus_tank.png'),
    ]
    
DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

MOVE_SPEED =    [1, 2, 2, 1, 2, 3, 3, 2]
BULLET_SPEED =  [4, 5, 6, 5, 5, 5, 6, 7]
BULLET_DAMAGE = [1, 1, 2, 3, 2, 2, 3, 4]
SHOT_DELAY =    [60, 50, 30, 40, 30, 25, 25, 30]

class UI:
    def __init__(self):
        pass

    def update(self):
        pass
    
    def draw(self):
        i = 0
        for obj in objects:
            if obj.type == 'tank':
                pygame.draw.rect(window, obj.color, (5 + i * 70, 5, 22, 22))

                text = fontUI.render(str(obj.rank), 1, 'black')
                rect = text.get_rect(center = (5 + i * 70 + 11, 5 + 11))
                window.blit(text, rect)

                text = fontUI.render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center = (5 + i * 70 + 32, 5 + 11))
                window.blit(text, rect)
                i += 1
                

class Tank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.type = 'tank'
        self.engine_sound_playing = False

        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.hp = 5
        self.shotTimer = 0

        self.moveSpeed = 2
        self.shotDelay = 60
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]

        self.rank = 0
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center = self.rect.center)

        start_sound.play()

    def update(self):
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center = self.rect.center)

        self.moveSpeed = MOVE_SPEED[self.rank]
        self.shotDelay = SHOT_DELAY[self.rank]
        self.bulletSpeed = BULLET_SPEED[self.rank]
        self.bulletDamage = BULLET_DAMAGE[self.rank]
        
        oldX, oldY = self.rect.topleft
        if keys[self.keyLEFT]:
            self.rect.x -= self.moveSpeed
            self.direct = 3
        elif keys[self.keyRIGHT]:
            self.rect.x += self.moveSpeed
            self.direct = 1
        elif keys[self.keyUP]:
            self.rect.y -= self.moveSpeed
            self.direct = 0
        elif keys[self.keyDOWN]:
            self.rect.y += self.moveSpeed
            self.direct = 2

        for obj in objects:
            if obj != self and obj.type == 'block' and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.keySHOT] and self.shotTimer == 0:
            dx = DIRECTS[self.direct][0] * self.bulletSpeed
            dy = DIRECTS[self.direct][1] * self.bulletSpeed
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)
            self.shotTimer = self.shotDelay

            shot_sound.play()

        if self.shotTimer > 0: self.shotTimer -= 1


        if keys[self.keyLEFT] or keys[self.keyRIGHT] or keys[self.keyUP] or keys[self.keyDOWN]:
            self.start_engine_sound() 
        else:
            self.stop_engine_sound()
 

    def draw(self):
        window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            print(self.color, 'dead')
            dead.play()


    def start_engine_sound(self):
        if not self.engine_sound_playing:
            engine_sound.play(-1)
            self.engine_sound_playing = True

    def stop_engine_sound(self):
        if self.engine_sound_playing:
            engine_sound.stop()
            self.engine_sound_playing = False


class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        bullets.append(self)
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage
        destroy_sound.play()
    def update(self):
        self.px += self.dx
        self.py += self.dy
        
        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                if obj != self.parent and obj.type != 'bang' and obj.type != 'bonus':
                    if obj.rect.collidepoint(self.px, self.py):
                        obj.damage(self.damage)
                        bullets.remove(self)
                        Bang(self.px, self.py)
                        destroy_sound.play()
                        break

    def draw(self):
        pygame.draw.circle(window, 'yellow', (self.px, self.py), 2)


class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.2
        if self.frame >= 3: objects.remove(self)

    def draw(self):
        image = imgBangs[int(self.frame)]
        rect = image.get_rect(center = (self.px, self.py))
        window.blit(image, rect)
    
class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBrick, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0: 
            objects.remove(self)
            destroy_sound.play()

class Bonus:
    def __init__(self, px, py, bonusNum):
        objects.append(self)
        self.type = 'bonus'

        self.image = imgBonuses[bonusNum]
        self.rect = self.image.get_rect(center = (px, py))

        self.timer = 600
        self.bonusNum = bonusNum
        
        

    def update(self):
        if self.timer > 0: self.timer -= 1
        else: objects.remove(self)

        for obj in objects:
            if obj.type == 'tank' and self.rect.colliderect(obj.rect):
                if self.bonusNum == 0:
                    if obj.rank < len(imgTanks) - 1:
                        obj.rank += 1
                        objects.remove(self)
                        break
                elif self.bonusNum == 1:
                    obj.hp += 1
                    objects.remove(self)
                    break
    
    def draw(self):
        if self.timer % 30 < 15:
            window.blit(self.image, self.rect)


class Menu:
    def __init__(self):
        self.start_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 25, 100, 50)
        self.restart_button_rect = pygame.Rect(WIDTH - 120, 10, 100, 30)
        self.is_active = True
        self.is_game_over = False

    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(window, 'gray', self.start_button_rect)
        start_text = fontUI.render('Start', 1, 'black')
        start_text_rect = start_text.get_rect(center=self.start_button_rect.center)
        window.blit(start_text, start_text_rect)

    def draw_restart_button(self):
        pygame.draw.rect(window, 'gray', self.restart_button_rect)
        restart_text = fontUI.render('Restart', 1, 'black')
        restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
        window.blit(restart_text, restart_text_rect)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button_rect.collidepoint(event.pos):
                self.is_active = False
            elif self.restart_button_rect.collidepoint(event.pos):
                self.restart_game()

    
    
    def restart_game(self):
        global bullets, objects, menu, bonusTimer
        bullets = []

        saved_blocks = []
        for obj in objects:
            if obj.type == 'block':
                saved_blocks.append(obj)

        objects = []

        for block in saved_blocks:
            Block(block.rect.x, block.rect.y, TILE)

        Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
        Tank('red', 650, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN))
        bonusTimer = 180
        self.is_game_over = False

        for block in objects:
            if block.type == 'block':
                block.draw()
        


menu = Menu()


bullets = []
objects = []
Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
Tank('red', 650, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN))
ui = UI()

for _ in range(50):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect): fined = True

        if not fined: break

    Block(x, y, TILE)

bonusTimer = 180

play = True
while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False

        menu.handle_events(event)  

    keys = pygame.key.get_pressed()

    if menu.is_active:  
        menu.update()
        menu.draw()
    else:
        if bonusTimer > 0:
            bonusTimer -= 1
        else:
            Bonus(randint(50, WIDTH - 50), randint(50, HEIGHT - 50), randint(0, len(imgBonuses) - 1))
            bonusTimer = randint(120, 240)

        for bullet in bullets:
            bullet.update()
        for obj in objects:
            obj.update()
        ui.update()

        window.fill('black')
        for bullet in bullets:
            bullet.draw()
        for obj in objects:
            obj.draw()
        ui.draw()

        if len(objects) <= 1: 
            menu.is_game_over = True
        
        menu.draw_restart_button()  

    pygame.display.update()
    clock.tick(FPS)

 

pygame.quit()
