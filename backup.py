# PPUT THIS STARTS FROM START_GAME FUNCTION UNTIL THE END OF THE FILE

start_game()
# start_game2(player)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        # click to get the Cord of the Cursor
        if event.type == pygame.MOUSEBUTTONDOWN:
            if player_rect.collidepoint(event.pos):
                player_gravity = -15
        
        if game_state == 1:
            # Keyboard press down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not midAir and not tired:
                    jumpCharge += 0.3
                    midStrafe = False
                if event.key == pygame.K_a and not midAir and not tired:
                    player_direction = -1
                    if jumpCharge == 0:
                        midStrafe = True
                if event.key == pygame.K_d and not midAir and not tired:
                    player_direction = 1
                    if jumpCharge == 0:
                        midStrafe = True
                if event.key == pygame.K_n:
                    level += 1
                    player_rect.y = 800
                if event.key == pygame.K_m:
                    level -= 1
                    player_rect.y = 800

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a and midStrafe:
                    midStrafe = False
                if event.key == pygame.K_d and midStrafe:
                    midStrafe = False
                if event.key == pygame.K_SPACE and not midAir and jumpCharge != 0:
                    player_gravity = -1.3 * jumpCharge
                    jumpCharge = 0
                    midAir = True
                    play_sound('jump')          

    # Gameplay
    if game_state == 1:
        # Blit
        for surf, rect, _ in levels_object[level-1]:
            screen.blit(surf, rect)

        # Jumping 
        if jumpCharge !=0 and jumpCharge <= 15:
            jumpCharge += 0.3
        player_gravity += 0.6
        player_rect.y += player_gravity
        if midAir:
            player_rect.x += player_direction*10
        # Move the Character
        if midStrafe:
            player_rect.x += player_direction*5
        # Stop when touching a Border
        if player_rect.right >= width:
            midStrafe = False
            player_rect.right = width
            if midAir: 
                player_direction *= -1
                play_sound('wall')
        if player_rect.left <= 0:
            player_rect.left = 0
            midStrafe = False
            if midAir: 
                player_direction *= -1
                play_sound('wall')

        onAir += 1
        for platform_surf, platform_rect, platform in levels_object[level-1]:
            if platform:
                if player_rect.colliderect(platform_rect):
                    side = get_collision_side(player_rect, platform_rect)
                    if side == 'top':
                        player_rect.top = platform_rect.bottom
                        if midAir: 
                            player_gravity = 0
                            play_sound('wall')
                    elif side == 'bottom':
                        if player_gravity >= 30:
                            tired = True
                            midStrafe = False
                            play_sound('fell')
                        if tired:
                            rest += 1
                            if rest >= 90:
                                tired = False
                                rest = 0
                        player_gravity = 0
                        player_rect.bottom = platform_rect.top + 2
                        midAir = False
                    elif side == 'right':
                        if not midStrafe: 
                            player_direction *= -1
                            play_sound('wall')
                        player_rect.right = platform_rect.left
                    elif side == 'left':
                        if not midStrafe: 
                            player_direction *= -1
                            play_sound('wall')
                        player_rect.left = platform_rect.right

        # check if the Player reach top or bottom
        if player_rect.top <= 0:
            player_rect.top += height
            level += 1
        elif player_rect.top >= height:
            player_rect.top -= height
            level -= 1

        # Close the game if done
        if level == len(levels_object):
            if (player_rect.right >= 460 and player_rect.right <= 740) or (player_rect.left >= 460 and player_rect.left <= 740):
                if player_rect.centery <= 630:
                    pygame.quit()
                    exit()

        player_animation()
        screen.blit(player_surf,player_rect)

    pygame.display.update()
    clock.tick(fps)