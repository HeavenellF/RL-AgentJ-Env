    if game_state == 1:
        # Blit
        for surf, rect, _ in levels_object[level-1]:
            screen.blit(surf, rect)

        # Jumping 
        if P.jumpCharge !=0 and P.jumpCharge <= 15:
            P.jumpCharge += 0.3
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

    pygame.display.update()
    clock.tick(fps)