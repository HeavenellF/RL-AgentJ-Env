#!/usr/bin/env python
import pygame
import random
from sys import exit
import os

import gym
from gym import spaces
import numpy as np

from Button import mainMenu_elements, gameOver_elements
from collision import get_collision_side
import levelsobject

#========================== AGENT CLASS ================================#
class Player:
    def __init__(self):
        self.player_stand = pygame.image.load('Env/image/player/playerstand.png').convert_alpha()
        self.player_walk_1 = pygame.image.load('Env/image/player/playerwalk1.png').convert_alpha()
        self.player_charge = pygame.image.load('Env/image/player/playercharge.png').convert_alpha()
        self.player_jump = pygame.image.load('Env/image/player/playerjump.png').convert_alpha()
        self.player_fell = pygame.image.load('Env/image/player/playerfell.png').convert_alpha()
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

# P = Player()

# ================== CLASS FOR GAME ENVIRONMENT ======================== #

class AgentJEnv(gym.Env):
    def __init__(self, render_mode=None):
        super(AgentJEnv, self).__init__()
        # Set the display driver to 'dummy' if running in headless mode
        self.render_mode = render_mode
        if self.render_mode is None:
            os.environ["SDL_VIDEODRIVER"] = "dummy"  # For headless mode
        pygame.init()
        self.bgm_sound = pygame.mixer.Sound('Env/sound/bgm.mp3')
        self.bgm_sound.set_volume(0.5)
        self.finish_sound = pygame.mixer.Sound('Env/sound/finish.mp3')
        self.finish_sound.set_volume(0.5)
        self.wallbounce1_sound = pygame.mixer.Sound('Env/sound/wallhit1.mp3')
        self.wallbounce1_sound.set_volume(0.8)
        self.wallbounce2_sound = pygame.mixer.Sound('Env/sound/wallhit2.mp3')
        self.wallbounce2_sound.set_volume(0.8)
        self.wallbounce3_sound = pygame.mixer.Sound('Env/sound/wallhit3.mp3')
        self.wallbounce3_sound.set_volume(0.8)
        self.jump_sound = pygame.mixer.Sound('Env/sound/jump.mp3')
        self.jump_sound.set_volume(0.9)
        self.fell_sound = pygame.mixer.Sound('Env/sound/fell.mp3')
        self.fell_sound.set_volume(1)
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, -1, 0]),  # lower bounds of each component
            high=np.array([np.inf, np.inf, 10, 1, 1]),  # upper bounds for each component
            dtype=np.float32  # data type for each component (32-bit float)
        )
        self.reward_range = (-float('inf'), float('inf'))

        self.width = 1200
        self.height = 900
        self.fps = 60


        if self.render_mode == "human":
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption('Agent J')
            self.clock = pygame.time.Clock()
        else:
            pygame.display.set_mode((1,1))
            self.screen = None
            self.clock = None

        #========================== LEVELS OBJECT ================================#
        self.levels_object = [
            levelsobject.level1_object(self.width, self.height),
            levelsobject.level2_object(self.width, self.height),
            levelsobject.level3_object(self.width, self.height),
            levelsobject.level4_object(self.width, self.height),
            levelsobject.level5_object(self.width, self.height),
            levelsobject.level6_object(self.width, self.height),
            levelsobject.level7_object(self.width, self.height),
            levelsobject.level8_object(self.width, self.height),
            levelsobject.levelend1_object(self.width, self.height),
            levelsobject.levelend2_object(self.width, self.height),
            levelsobject.levelend3_object(self.width, self.height)
        ]

        self.level = 0
        #=========================================================================#
        self.reset()

    def reset(self):
        # Reset the game environtment
        self.P = Player() # Reset the player
        self.start_game()
        return self.get_state()

    def step(self, action):
        if not self.P.midAir and not self.P.tired:
            if action == 0:    # Do nothing
                self.P.midStrafe = False
            elif action == 1:  # Move Left
                self.P.player_direction = -1
                self.P.midStrafe = True
            elif action == 2: # Move Right
                self.P.player_direction = 1
                self.P.midStrafe = True
            elif action == 3: # Jump Low
                self.P.midStrafe = False
                self.P.player_gravity = -13
                self.P.midAir = True
                self.play_sound('jump')
            elif action == 4: # Jump High
                self.P.midStrafe = False
                self.P.player_gravity = -19.5
                self.P.midAir = True
                self.play_sound('jump')

        self.game_logic()
        
        state = 0
        reward = 0
        done = False
        return state, reward, done
    
    def get_state(self):
        return (self.level, self.P.player_rect.x, self.P.player_rect.y, self.P.player_gravity, self.P.player_direction)

    def render(self):
        if self.render_mode == "human":
            self.screen.blit(self.P.player_surf,self.P.player_rect)
            pygame.display.update()
            self.clock.tick(self.fps)

    def close(self):
        pygame.quit()

    def play_sound(self, type):
        if type == 'wall':
            random_number = random.randint(1, 3)
            if random_number == 1 : self.wallbounce1_sound.play()
            elif random_number == 2 : self.wallbounce2_sound.play()
            elif random_number == 3 : self.wallbounce3_sound.play()
        elif type == 'jump':
            self.jump_sound.play()
        elif type == 'fell':
            self.fell_sound.play()

    def start_game(self):
        self.bgm_sound.stop()
        self.bgm_sound.play(-1)
        self.level = 1
        self.P.player_rect = self.P.player_surf.get_rect(midbottom= (self.width/2,825))

    def game_logic(self):
        """" Game Logic """
        # Blit
        for surf, rect, _ in self.levels_object[self.level-1]:
            if self.render_mode == "human":
                self.screen.blit(surf, rect)

        # Jumping 
        self.P.player_gravity += 0.6
        self.P.player_rect.y += self.P.player_gravity
        if self.P.midAir:
            self.P.player_rect.x += self.P.player_direction*10
        # Move the Character
        if self.P.midStrafe:
            self.P.player_rect.x += self.P.player_direction*5
        # Stop when touching a Border
        if self.P.player_rect.right >= self.width:
            self.P.midStrafe = False
            self.P.player_rect.right = self.width
            if self.P.midAir: 
                self.P.player_direction *= -1
                self.play_sound('wall')
        if self.P.player_rect.left <= 0:
            self.P.player_rect.left = 0
            self.P.midStrafe = False
            if self.P.midAir: 
                self.P.player_direction *= -1
                self.play_sound('wall')

        self.P.onAir += 1
        for platform_surf, platform_rect, platform in self.levels_object[self.level-1]:
            if platform:
                if self.P.player_rect.colliderect(platform_rect):
                    side = get_collision_side(self.P.player_rect, platform_rect)
                    if side == 'top':
                        self.P.player_rect.top = platform_rect.bottom
                        if self.P.midAir: 
                            self.P.player_gravity = 0
                            self.play_sound('wall')
                    elif side == 'bottom':
                        if self.P.player_gravity >= 30:
                            self.P.tired = True
                            self.P.midStrafe = False
                            self.play_sound('fell')
                        if self.P.tired:
                            self.P.rest += 1
                            if self.P.rest >= 90:
                                self.P.tired = False
                                self.P.rest = 0
                        self.P.player_gravity = 0
                        self.P.player_rect.bottom = platform_rect.top + 2
                        self.P.midAir = False
                    elif side == 'right':
                        if not self.P.midStrafe: 
                            self.P.player_direction *= -1
                            self.play_sound('wall')
                        self.P.player_rect.right = platform_rect.left
                    elif side == 'left':
                        if not self.P.midStrafe: 
                            self.P.player_direction *= -1
                            self.play_sound('wall')
                        self.P.player_rect.left = platform_rect.right

        # check if the Player reach top or bottom
        if self.P.player_rect.top <= 0:
            self.P.player_rect.top += self.height
            self.level += 1
        elif self.P.player_rect.top >= self.height:
            self.P.player_rect.top -= self.height
            self.level -= 1

        # Close the game if done
        if self.level == len(self.levels_object):
            if (self.P.player_rect.right >= 460 and self.P.player_rect.right <= 740) or (self.P.player_rect.left >= 460 and self.P.player_rect.left <= 740):
                if self.P.player_rect.centery <= 630:
                    pygame.quit()
                    exit()

        self.P.player_animation()

env = AgentJEnv(render_mode="human")
state = env.reset()
action = 0
i = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            env.close()
            exit()
        
        # click to get the Cord of the Cursor
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.pos)
        
        # Keyboard press down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                action = 1
            if event.key == pygame.K_d:
                action = 2
            if event.key == pygame.K_c:
                action = 3
            if event.key == pygame.K_v:
                action = 4
            if event.key == pygame.K_r:
                state = env.reset()
            # ============================================ #
            if event.key == pygame.K_n:
                env.level += 1
            if event.key == pygame.K_m:
                env.level -= 1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a and env.P.midStrafe:
                action = 0
            if event.key == pygame.K_d and env.P.midStrafe:
                action = 0  

    # action = random.choice([0, 1, 2, 3, 4])
    state, reward, done = env.step(action)

    # stop the jumping action
    if action in (3,4):
        action = 0

    env.render()

    if done:
        break

env.close()
