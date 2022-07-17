import pygame as pg
import sys
import random
from os import path

# Constants
WIDTH,HEIGHT = 600,800
FPS = 30 # Frames per seconds
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("Space War")
clock = pg.time.Clock()

# asset folders
IMG_DIR = path.join(path.dirname(__file__), 'img')
SOUND_DIR = path.join(path.dirname(__file__), 'sounds')
EXPLOSION_DIR = path.join(path.dirname(__file__), 'img/explosion')
FONT_DIR = path.join(path.dirname(__file__),'font')

# Load all images
BACKGROUND = pg.transform.scale(pg.image.load(path.join(IMG_DIR,'bg.jpeg')),(WIDTH,HEIGHT))
BACKGROUND_RECT1 = BACKGROUND.get_rect()
BACKGROUND_RECT2 = BACKGROUND.get_rect()
# player 
PLAYER_IMG = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"player.png")), (75,75))
PLAYER_MINI_IMG = pg.transform.scale(PLAYER_IMG, (30,25))
# enemy
ENEMY_RED_IMG = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"enemy_red.png")),(50,50))
ENEMY_GREEN_IMG = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"enemy_green.png")),(50,50))
ENEMY_BLUE_IMG = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"enemy_blue.png")),(50,50))
# bullet
BULLET_RED = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"bullet_red.png")),(50,50))
BULLET_GREEN = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"bullet_green.png")),(50,50))
BULLET_BLUE = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"bullet_blue.png")),(50,50))
BULLET_YELLOW = pg.transform.scale(pg.image.load(path.join(IMG_DIR,"bullet_yellow.png")),(50,50))
# explosion image
EXPLOSION_ANIM = {}
EXPLOSION_ANIM['xl'] = []
EXPLOSION_ANIM['lg'] = []
EXPLOSION_ANIM['md'] = []
EXPLOSION_ANIM['sm'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pg.image.load(path.join(EXPLOSION_DIR, filename)).convert()
    img.set_colorkey((0,0,0))
    img_lg = pg.transform.scale(img, (100, 100))
    EXPLOSION_ANIM['xl'].append(img_lg)
    img_lg = pg.transform.scale(img, (75, 75))
    EXPLOSION_ANIM['lg'].append(img_lg)
    img_md = pg.transform.scale(img, (50, 50))
    EXPLOSION_ANIM['md'].append(img_md)
    img_sm = pg.transform.scale(img, (25, 25))
    EXPLOSION_ANIM['sm'].append(img_sm)

# Sounds
# background music
pg.mixer.music.load(path.join(SOUND_DIR, 'space_war_background_music.ogg'))
pg.mixer.music.set_volume(0.2)
# player shoot sound
PLAYER_SHOOT_SOUND = pg.mixer.Sound(path.join(SOUND_DIR, 'sound_player_shoot.wav'))
EXPLOSION_SOUNDS = []
for snd in ['expl_a.wav', 'expl_b.wav']:
    EXPLOSION_SOUNDS.append(pg.mixer.Sound(path.join(SOUND_DIR, snd)))

# Font
FONT_NAME = path.join(FONT_DIR, 'SimSun.ttf')

# create sprite groups
all_sprites = pg.sprite.Group()
enemy_sprites = pg.sprite.Group()
enemy_bullet_sprites = pg.sprite.Group()
player_bullet_sprites = pg.sprite.Group()

class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = PLAYER_IMG
        self.bullet_image = BULLET_YELLOW
        self.rect = self.image.get_rect()      
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.shoot_reload = 100
        self.last_shot = 0
        self.mask = pg.mask.from_surface(self.image)
        self.score = 0
        self.bullet_damage = 10   
        self.shield = 100     
        self.lives = 3
    
    def update(self):
        self.speedx = 0
        self.speedy = 0

        keystate = pg.key.get_pressed()
        if keystate[pg.K_a]:
            self.speedx = -5
        if keystate[pg.K_d]:
            self.speedx = 5
        if keystate[pg.K_w]:
            self.speedy = -5
        if keystate[pg.K_s]:
            self.speedy = 5
        if keystate[pg.K_SPACE]:
            self.shoot()
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # check if out of screen
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
        
        # check player shield and lives
        if self.shield <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.shield = 100

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_reload:
            bullet = Bullet(self.rect.centerx,self.rect.top,self.bullet_image, -10, self.bullet_damage)
            all_sprites.add(bullet)
            player_bullet_sprites.add(bullet)
            self.last_shot = now
            PLAYER_SHOOT_SOUND.play()

class Enemy(pg.sprite.Sprite):

    COLOR_MAP = {
        RED : (ENEMY_RED_IMG, 10, BULLET_RED, 5),
        GREEN : (ENEMY_GREEN_IMG, 20, BULLET_GREEN, 10),
        BLUE : (ENEMY_BLUE_IMG, 30, BULLET_BLUE, 15)
    }

    def __init__(self, color):
        pg.sprite.Sprite.__init__(self)
        self.color = color
        self.image = self.COLOR_MAP[color][0]
        self.shield = self.COLOR_MAP[color][1]
        self.bullet_image = self.COLOR_MAP[color][2]
        self.bullet_damage = self.COLOR_MAP[color][3]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(10,WIDTH - self.rect.width - 10)
        self.rect.y = random.randrange(-100,0)
        self.speedx = random.randrange(-3,3)
        self.speedy = random.randrange(1,5)
        self.mask = pg.mask.from_surface(self.image)
    
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # check if out of screen
        if self.rect.x <= 0 or self.rect.right >= WIDTH:
            self.speedx = -self.speedx
        if self.rect.top > HEIGHT:
            self.kill()
        
        # check when to shoot
        if random.randrange(0, 3 * FPS) == 1:
            self.shoot()

    def shoot(self):
        if self.rect.y > 0:
            bullet = Bullet(self.rect.centerx, self.rect.bottom + 20, self.bullet_image, 5, self.bullet_damage)
            all_sprites.add(bullet)
            enemy_bullet_sprites.add(bullet)    

class Bullet(pg.sprite.Sprite):
    def __init__(self,x,y,img,speedy,damage):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = speedy
        self.damage = damage
    
    def update(self):
        self.rect.y += self.speedy
        # check if out of the screen
        if self.speedy < 0 and self.rect.bottom < 0: # player's bullet
            self.kill()
        if self.speedy > 0 and self.rect.top > HEIGHT: # enemy's bullet
            self.kill()

class Explosion(pg.sprite.Sprite):
    def __init__(self, center, size):
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.image = EXPLOSION_ANIM[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 50
        self.frame = 0
        self.mask = pg.mask.from_surface(self.image)
    
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            now = pg.time.get_ticks()
            self.frame += 1
            if self.frame == len(EXPLOSION_ANIM[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = EXPLOSION_ANIM[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

def generate_enemies(num):
    for i in range(num):
        enemy = Enemy(random.choice([RED,GREEN,BLUE]))
        all_sprites.add(enemy)
        enemy_sprites.add(enemy)

def draw_roll_background(surf, background, rect1, rect2):
    # draw background 1
    rect1.top += 1
    surf.blit(background, rect1)
    # draw background 2
    rect2.bottom = rect1.top
    surf.blit(background,rect2)
    # if out of screen redo
    if rect1.top > HEIGHT:
        rect1.top = 0
        rect2.top = -HEIGHT

def get_font_surface(text, font_name, font_size, font_color):
    font = pg.font.Font(FONT_NAME, font_size)
    font_surface = font.render(text, True, font_color)
    return font_surface

def draw_text(surf, font_surface, left_x=None, center_x=None, right_x=None, y=None):
    ''' you can optionall provide one parameter value of: left_x, center_x, or right_x
        you must provide parameter value of y
    '''
    text_rect = font_surface.get_rect()
    if center_x == None and left_x != None:
        center_x = left_x + int(text_rect.width / 2)
    elif center_x == None and left_x == None and right_x != None:
        center_x = right_x - int(text_rect.width / 2)
    text_rect.midtop = (center_x, y)
    surf.blit(font_surface, text_rect)

def draw_shield_bar(surf, x, y, shield):
    if shield < 0:
        shield = 0
    BAR_LENGTH = 100
    bAR_HEIGHT = 10
    fill = (shield / 100) * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, bAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, bAR_HEIGHT)
    pg.draw.rect(surf, GREEN, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 1)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 34 * i
        img_rect.y = y
        surf.blit(img, img_rect)

player = Player()
all_sprites.add(player)

# play background music
pg.mixer.music.play(loops=-1)

# Game Loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # process input (events)
    for event in pg.event.get():
        # check for closing window
        if event.type == pg.QUIT:
            running = False

    # generate enemies if there is none
    if len(enemy_sprites.sprites()) == 0:
        generate_enemies(10)
    
    # update
    all_sprites.update()

    # check if player hit any enemy
    hits = pg.sprite.spritecollide(player,enemy_sprites, False, pg.sprite.collide_mask)
    for enemy in hits:
        expl = Explosion(enemy.rect.center,'md')
        all_sprites.add(expl)
        random.choice(EXPLOSION_SOUNDS).play()
        player.shield -= enemy.shield
        enemy.kill()
    
    # check if player's bullet hit any enemy
    hits = pg.sprite.groupcollide(player_bullet_sprites,enemy_sprites,True,False, pg.sprite.collide_mask)
    for bullet in hits:
        for enemy in hits[bullet]:
            player.score += enemy.shield
            enemy.shield -= player.bullet_damage
            if enemy.shield <= 0:
                expl = Explosion(enemy.rect.center,'lg')
                all_sprites.add(expl)
                enemy.kill()
            else:
                expl = Explosion(enemy.rect.center,'sm')
                all_sprites.add(expl)
            random.choice(EXPLOSION_SOUNDS).play()
    
    # check if player hit enemy bullets
    hits = pg.sprite.spritecollide(player, enemy_bullet_sprites, False, pg.sprite.collide_mask)
    for bullet in hits:
        expl = Explosion(bullet.rect.center,'sm')
        all_sprites.add(expl)
        random.choice(EXPLOSION_SOUNDS).play()
        player.shield -= bullet.damage
        bullet.kill()

    # check if player game over
    if player.lives == 0:
        running = False

    # check if player's bullet hit enemy's bullets
    hits = pg.sprite.groupcollide(player_bullet_sprites, enemy_bullet_sprites,True,True, pg.sprite.collide_mask)

    # -----------
    # Draw/Render
    # -----------
    screen.fill(BLACK)
    draw_roll_background(screen, BACKGROUND, BACKGROUND_RECT1, BACKGROUND_RECT2)

    # score
    draw_text(screen, get_font_surface("得分: " + str(player.score), FONT_NAME,20, WHITE),center_x = WIDTH / 2, y=10)

    # draw lives
    draw_lives(screen, 10, 5, player.lives, PLAYER_MINI_IMG)

    # draw shield
    draw_shield_bar(screen, 10, 35, player.shield)
    draw_text(screen, get_font_surface(str(player.shield), FONT_NAME, 16, WHITE), left_x = 112, y = 30)

    # draw each sprite
    all_sprites.draw(screen)

    # after drawing everythjing, flip the display
    pg.display.flip()

pg.quit()
sys.exit(0)