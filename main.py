#!/usr/bin/env python
import pygame
import random
from sys import exit

import gym
from gym import spaces
import numpy as np

from Button import mainMenu_elements, gameOver_elements
from collision import get_collision_side
import levelsobject

width = 1200
height = 900
fps = 60

pygame.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Agent J')    # Window Name here
clock = pygame.time.Clock()

#========================== LEVELS OBJECT ================================#
levels_object = [levelsobject.level1_object(width,height), 
                 levelsobject.level2_object(width,height), 
                 levelsobject.level3_object(width,height),
                 levelsobject.level4_object(width,height),
                 levelsobject.level5_object(width,height),
                 levelsobject.level6_object(width,height),
                 levelsobject.level7_object(width,height),
                 levelsobject.level8_object(width,height),
                 levelsobject.levelend1_object(width,height),
                 levelsobject.levelend2_object(width,height),
                 levelsobject.levelend3_object(width,height)]
level = 0
#=========================================================================#
#====================================== MP3 ==============================#
bgm_sound = pygame.mixer.Sound('sound/bgm.mp3')
bgm_sound.set_volume(0.5)
finish_sound = pygame.mixer.Sound('sound/finish.mp3')
finish_sound.set_volume(0.5)
wallbounce1_sound = pygame.mixer.Sound('sound/wallhit1.mp3')
wallbounce1_sound.set_volume(0.8)
wallbounce2_sound = pygame.mixer.Sound('sound/wallhit2.mp3')
wallbounce2_sound.set_volume(0.8)
wallbounce3_sound = pygame.mixer.Sound('sound/wallhit3.mp3')
wallbounce3_sound.set_volume(0.8)
jump_sound = pygame.mixer.Sound('sound/jump.mp3')
jump_sound.set_volume(0.9)
fell_sound = pygame.mixer.Sound('sound/fell.mp3')
fell_sound.set_volume(1)

def play_sound(type):
    if type == 'wall':
        random_number = random.randint(1, 3)
        if random_number == 1 : wallbounce1_sound.play()
        elif random_number == 2 : wallbounce2_sound.play()
        elif random_number == 3 : wallbounce3_sound.play()
    elif type == 'jump':
        jump_sound.play()
    elif type == 'fell':
        fell_sound.play()
#=========================================================================#

#========================== AGENT CLASS ================================#
class Player:
    def __init__(self):
        self.player_stand = pygame.image.load('image/player/playerstand.png').convert_alpha()
        self.player_walk_1 = pygame.image.load('image/player/playerwalk1.png').convert_alpha()
        self.player_charge = pygame.image.load('image/player/playercharge.png').convert_alpha()
        self.player_jump = pygame.image.load('image/player/playerjump.png').convert_alpha()
        self.player_fell = pygame.image.load('image/player/playerfell.png').convert_alpha()
        self.player_state = [self.player_stand, self.player_walk_1, self.player_jump, self.player_fell]
        self.player_index = 0

        self.player_surf = self.player_state[self.player_index]
        self.player_rect = self.player_surf.get_rect()
        self.player_gravity = 0
        self.player_direction = 1
        self.midAir = False
        self.midStrafe = False
        self.onAir = 0
        self.tired = False
        self.rest = 0

    def player_animation(self):
        # walking animation
        if self.midStrafe:
            self.player_index = 1
            self.player_surf = self.player_state[self.player_index]
        elif self.midAir:
            self.player_index = 2
            self.player_surf = self.player_state[self.player_index]
        elif self.tired:
            self.player_index = 3
            self.player_surf = self.player_state[self.player_index]
        else:
            self.player_index = 0
            self.player_surf = self.player_state[self.player_index]

        if self.player_direction == 1:
            self.player_surf = pygame.transform.flip(self.player_surf, True, False)

P = Player()

# ================== CLASS FOR GAME ENVIRONMENT ======================== #

class AgentJEnv(gym.Env):
    def __init__(self):
        super(AgentJEnv, self).__init__()
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, -1, 0]),  # lower bounds of each component
            high=np.array([np.inf, np.inf, 10, 1, 1]),  # upper bounds for each component
            dtype=np.float32  # data type for each component (32-bit float)
        )
        self.reward_range = (-float('inf'), float('inf'))
        self.reset()

    def reset(self):
        # Reset the game environtment
        global P
        P = Player() # Reset the player
        start_game(P)
        return self.get_state()

    def step(self, action):
        state, reward, done = step(action)
        return state, reward, done
    
    def get_state(self):
        return (level, P.player_rect.x, P.player_rect.y, P.player_gravity, P.player_direction)

    def render(self):
        screen.blit(P.player_surf,P.player_rect)
        pygame.display.update()
        # pygame.display.flip()
    
# ===================================================================== #

def start_game(player):
    global level
    bgm_sound.stop()
    bgm_sound.play(-1)
    level = 1
    player.player_rect = player.player_surf.get_rect(midbottom= (width/2,825))
# =========================================================================== #

# ====================== STEP FUNCTION GAME ========================== #
def step(action):
    global P
    if not P.midAir and not P.tired:
        if action == 0:    # Do nothing
            P.midStrafe = False
        elif action == 1:  # Move Left
            P.player_direction = -1
            P.midStrafe = True
        elif action == 2: # Move Right
            P.player_direction = 1
            P.midStrafe = True
        elif action == 3: # Jump Low
            P.midStrafe = False
            P.player_gravity = -13
            P.midAir = True
            play_sound('jump')
        elif action == 4: # Jump High
            P.midStrafe = False
            P.player_gravity = -19.5
            P.midAir = True
            play_sound('jump')

    game_logic()
    # Run the game 1 frame

    # Get the new state
    # Get the reward
    # Check if the game is done
    state = 0
    reward = 0
    done = False
    return state, reward, done
# ==================================================================== #

def game_logic():
    global level     

    # Gameplay
    # Blit
    for surf, rect, _ in levels_object[level-1]:
        screen.blit(surf, rect)

    # Jumping 
    P.player_gravity += 0.6
    P.player_rect.y += P.player_gravity
    if P.midAir:
        P.player_rect.x += P.player_direction*10
    # Move the Character
    if P.midStrafe:
        P.player_rect.x += P.player_direction*5
    # Stop when touching a Border
    if P.player_rect.right >= width:
        P.midStrafe = False
        P.player_rect.right = width
        if P.midAir: 
            P.player_direction *= -1
            play_sound('wall')
    if P.player_rect.left <= 0:
        P.player_rect.left = 0
        P.midStrafe = False
        if P.midAir: 
            P.player_direction *= -1
            play_sound('wall')

    P.onAir += 1
    for platform_surf, platform_rect, platform in levels_object[level-1]:
        if platform:
            if P.player_rect.colliderect(platform_rect):
                side = get_collision_side(P.player_rect, platform_rect)
                if side == 'top':
                    P.player_rect.top = platform_rect.bottom
                    if P.midAir: 
                        P.player_gravity = 0
                        play_sound('wall')
                elif side == 'bottom':
                    if P.player_gravity >= 30:
                        P.tired = True
                        P.midStrafe = False
                        play_sound('fell')
                    if P.tired:
                        P.rest += 1
                        if P.rest >= 90:
                            P.tired = False
                            P.rest = 0
                    P.player_gravity = 0
                    P.player_rect.bottom = platform_rect.top + 2
                    P.midAir = False
                elif side == 'right':
                    if not P.midStrafe: 
                        P.player_direction *= -1
                        play_sound('wall')
                    P.player_rect.right = platform_rect.left
                elif side == 'left':
                    if not P.midStrafe: 
                        P.player_direction *= -1
                        play_sound('wall')
                    P.player_rect.left = platform_rect.right

    # check if the Player reach top or bottom
    if P.player_rect.top <= 0:
        P.player_rect.top += height
        level += 1
    elif P.player_rect.top >= height:
        P.player_rect.top -= height
        level -= 1

    # Close the game if done
    if level == len(levels_object):
        if (P.player_rect.right >= 460 and P.player_rect.right <= 740) or (P.player_rect.left >= 460 and P.player_rect.left <= 740):
            if P.player_rect.centery <= 630:
                pygame.quit()
                exit()

    P.player_animation()
    screen.blit(P.player_surf,P.player_rect)


# start_game(P)
# while True:
#     game_logic()

env = AgentJEnv()
action = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        # click to get the Cord of the Cursor
        if event.type == pygame.MOUSEBUTTONDOWN:
            if P.player_rect.collidepoint(event.pos):
                P.player_gravity = -15
        
        # Keyboard press down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and not P.midAir and not P.tired:
                action = 1
            if event.key == pygame.K_d and not P.midAir and not P.tired:
                action = 2
            if event.key == pygame.K_c and not P.midAir and not P.tired:
                action = 3
            if event.key == pygame.K_v and not P.midAir and not P.tired:
                action = 4
            if event.key == pygame.K_r:
                start_game(P)
            # ============================================ #
            if event.key == pygame.K_n:
                level += 1
                P.player_rect.y = 800
            if event.key == pygame.K_m:
                level -= 1
                P.player_rect.y = 800

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a and P.midStrafe:
                action = 0
            if event.key == pygame.K_d and P.midStrafe:
                action = 0  

    # action = random.choice([0, 1, 2, 3, 4])
    state, reward, done = env.step(action)

    # stop the jumping action
    if action == 3 or action == 4:
        action = 0

    env.render()

    if done:
        break

    clock.tick(fps)
