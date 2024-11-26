from multiprocessing import shared_memory
import struct

shm = shared_memory.SharedMemory(name="command_buffer")

def check_for_push():
    command_value = struct.unpack('I', shm.buf[:4])[0]
    if command_value == 1:  # 1 represents "push"
        shm.buf[:4] = struct.pack('I', 0)  # Reset to "no command"
        return "up"
    elif command_value == 2:
        shm.buf[:4] = struct.pack('I', 0)
        return "down"
    else:
        return "none"

def pong():
    import pygame,sys
    import random
    from pygame import mixer

    
    #initialising pygame

    pygame.init()
    screen_width=800
    screen_height=600
    screen=pygame.display.set_mode((screen_width,screen_height))
    clock=pygame.time.Clock()
    pygame.display.set_caption("Pong!")
    icon=pygame.image.load("assets\\ping-pong.png")
    pygame.display.set_icon(icon)
    mixer.music.load("assets\\pongbmg.wav")
    mixer.music.play(-1)
    paddlesound=mixer.Sound("assets\\paddlesound.wav")
    wallsound=mixer.Sound('assets\\wallsound.wav')
    pointsound=mixer.Sound('assets\\pointsound.wav')
    pointsound.set_volume(0.2)
    wallsound.set_volume(0.2)
    paddlesound.set_volume(0.2)




    #Game objects
    game_state='playing'
    ball=pygame.Rect(screen_width/2 - 15,screen_height/2 - 15,20,20)
    player=pygame.Rect(screen_width - 20,screen_height/2 - 70,10,140)
    opponent=pygame.Rect(10,screen_height/2 - 70,10,140)
    gameover=pygame.image.load('assets\\gameover.png')
    playercolor=115,255,87
    ballcolor=(235,35,35)
    playerscore=0
    opponentscore=0
    userinfo=''
    textfont=pygame.font.Font("freesansbold.ttf",24)
    userfont=pygame.font.Font("freesansbold.ttf",48)
    #movement

    ball_speed_x=-3
    ball_speed_y=3 * random.choice((1,-1))

    player_speed=0
    opponent_speed=2
    #game loop

    running=True
    while running:
        screen.fill((23,23,23))
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_DOWN:
                    player_speed+=7
                if event.key==pygame.K_UP:
                    player_speed-=7
                if event.key==pygame.K_ESCAPE:
                    running=False
                    mixer.music.load("assets\\arcadebackground.wav")
                    mixer.music.play(-1)
                if event.key==pygame.K_RETURN:
                    if game_state=='over':
                        playerscore=0
                        opponentscore=0
                        ball_speed_x=-3
                        ball_speed_y=3 * random.choice((1,-1))
                        player_speed=0
                        opponent_speed=5



                        
            if event.type==pygame.KEYUP:
                if event.key==pygame.K_DOWN:
                    player_speed-=7
                if event.key==pygame.K_UP:
                    player_speed+=7
            
        
        #ball movement and collision
        action = check_for_push()
        if action == "up":
            player_speed-=32
        elif action == "down":
            player_speed+=32
        elif action == "none":
            player_speed = 0
        ball.x+=ball_speed_x 
        ball.y+=ball_speed_y
        
        if ball.top<=0 or ball.bottom>=screen_height:
            ball_speed_y*=-1
            wallsound.play()
        if ball.left<=0:
            ball.y=screen_height/2
            ball.x=screen_width/2
            ball_speed_x=-3
            ball_speed_y=random.choice((3,-3))
            playerscore+=1
            pointsound.play()
        if ball.right>=screen_width:
            ball.y=screen_height/2
            ball.x=screen_width/2
            ball_speed_x=-3
            ball_speed_y=random.choice((3,-3))
            opponentscore+=1
            pointsound.play()
        if  ball.colliderect(opponent):
            ball_speed_x*=-1
            paddlesound.play()
        if  ball.colliderect(player):
            ball_speed_x=-5
            paddlesound.play()
        if player.top<=0:
            player.top=0
            
        if player.bottom>=screen_height:
            player.bottom=screen_height
            
        if opponent.top<=0:
            opponent.top=0
            
        if opponent.bottom>=screen_height:
            opponent.bottom=screen_height
            
        if opponent.y-25<ball.y:
            opponent.top+=opponent_speed
            
        if opponent.y+25>ball.y:
            opponent.bottom-=opponent_speed

        player.y+=player_speed
            
        pygame.draw.rect(screen,playercolor,player)
        pygame.draw.rect(screen,playercolor,opponent)
        pygame.draw.ellipse(screen,ballcolor,ball)
        pygame.draw.aaline(screen,random.choice(("red","green","blue")),(screen_width/2,0),(screen_width/2,screen_height))
        if playerscore == 5:
            wintext = userfont.render(f"YOU WON!",False,(255,255,255))
            screen.blit(wintext, (screen_width //2, screen_height // 2))
            ball_speed_x=0
            ball_speed_y=0
            player_speed=0
            opponent_speed=0
        if opponentscore==15:
            game_state='over'
            ball_speed_x=0
            ball_speed_y=0
            player_speed=0
            opponent_speed=0
            screen.blit(gameover,(0,0))
            screen.blit(usertext,(300,350))

        
        # purple_square = pygame.Rect(screen_width / 2 - 25, screen_height - 50, 50, 50)
        # pygame.draw.rect(screen, (128, 0, 128), purple_square)

        playertext=textfont.render(f"{playerscore}",False,(135,135,135))
        screen.blit(playertext,(410,290))
        opponenttext=textfont.render(f"{opponentscore}",False,(135,135,135))
        screen.blit(opponenttext,(380,290))
        usertext=userfont.render(f"{userinfo}",False,(255,255,255))
        
        #updating the window
        pygame.display.flip()
        clock.tick(60)

pong()