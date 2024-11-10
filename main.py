import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "Env"))

import pygame

from Env.gameEnv import AgentJEnv

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