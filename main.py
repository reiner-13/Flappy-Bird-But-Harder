"""
Improvements that can be made:
    1) Put everything in the Gamestate class
    2) No global variables
    3) Put everything in the Gamestate class
    4) Organize stuff better
    
We'll get 'em next time.
"""

import pygame, sys
from random import randint, choice
import bird as b # bird class
from pygame.constants import *

pygame.init() # initialize pygame
pygame.display.set_caption("Flappy Bird")

WINDOW_SIZE = (500, 700)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)) # shrinks display so pixel art is easy
clock = pygame.time.Clock()

pygame.font.init()
score_font = pygame.font.SysFont('Verdana', 30) # various fonts needed
starting_font = pygame.font.SysFont('Verdana', 10)
game_over_font = pygame.font.SysFont('Verdana', 20)

WHITE = (255,255,255)

pipe_img = pygame.image.load("images/pipe.png").convert() # loading all images needed
pipe_img.set_colorkey(WHITE) # making colorkey for transparency
cloud_1_img = pygame.image.load("images/cloud_1.png").convert()
cloud_1_img.set_colorkey(WHITE)
cloud_2_img = pygame.image.load("images/cloud_2.png").convert()
cloud_2_img.set_colorkey(WHITE)
flip_pipe_img = pygame.transform.flip(pipe_img, False, True)
background_img = pygame.image.load("images/background_1.png")
ground_img = pygame.image.load("images/ground.png")

bird = b.Bird(pygame.Rect((90, 130 , 27, 19))) # BIRD
ground_rect = pygame.Rect((0, 325, 250, 25))

global pipes # probably could have and should have put these in the GameState class but I'm in too deep
pipes = []
global pipe_movement
pipe_movement = []
global clouds
clouds = []

def render(surf, img, rect): # simple rendering function that simplifies some things
    surf.blit(img, (rect.x, rect.y))

def animation_handler(type, frame_duration, frames_in): # crude system to animate the bird
    current_frame = frames_in // frame_duration + 1
    img = pygame.image.load(f"images/{type}_{current_frame}.png").convert()
    img.set_colorkey(WHITE)
    return img

def func_update(): # a few lines that need to be called at the end of while loops
    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60) # 60 fps

def load_pipes(initial_num): # function that's called at startup and during the game
    if initial_num == 0: # initial_num determines if the function is being called at startup or not
        x = bird.rect.x + 250
    else:
        x = 250
    UPPER_BOUND = 140 # restriction on where pipes spawn
    LOWER_BOUND = 285
    y = randint(UPPER_BOUND, LOWER_BOUND)
    pipes.append(pygame.Rect(x, y, 32, 229))
    pipes.append(pygame.Rect(x, y - 320, 32, 229))
    if len(pipe_movement) < 5: # pipe_movement is a list of 1's and -1's that determine which direction the pairs of pipes move
        if randint(0,2) == 0:
            pipe_movement.append(1) # move_pipes() takes in the movement data two at a time
            pipe_movement.append(1)
        else:
            pipe_movement.append(-1)
            pipe_movement.append(-1)

def grouped(list): # allows move_pipes() to take in two pipes in the for loop
    return zip(*[iter(list)]*2)

def move_pipes(): # moves pipes up or down in pairs
    UPPER_BOUND = 140
    LOWER_BOUND = 285
    for i in range(len(pipes)):
        for pipe1, pipe2 in grouped(pipes):
            if pipe1.y <= UPPER_BOUND:
                pipe_movement[pipes.index(pipe1)] = 1
                pipe_movement[pipes.index(pipe2)] = 1
            elif pipe1.y >= LOWER_BOUND:
                pipe_movement[pipes.index(pipe1)] = -1
                pipe_movement[pipes.index(pipe2)] = -1
        pipes[i].y += pipe_movement[i]

def load_clouds(): # 
    x = randint(WINDOW_SIZE[0] / 2 + 5, WINDOW_SIZE[0] / 2 + 500) # loads clouds from 5 units to the right of the window to 500
    y = randint(10, 120) # arbitrary y values
    if randint(0,1) == 0: 
        clouds.append(pygame.Rect(x, y, 34, 10)) # the cloud rects' widths determine which cloud image should be loaded onto it
    else:
        clouds.append(pygame.Rect(x, y, 36, 12))

def update_clouds(): # moves the clouds
    if len(clouds) < 8 or len(clouds) == None: # only 7 clouds exist at any given time
        if clouds[0].x <= -40: # clouds get deleted after leaving the screen
            clouds.remove(clouds[0])
        if len(clouds) != 7:
            load_clouds()
        for cloud in clouds:
            cloud.x -= 1
            cloud.y += choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1])
            if cloud.w == 34: # cloud width determines image loaded
                render(display, cloud_1_img, cloud)
            else:
                render(display, cloud_2_img, cloud)

def rot_center(image, angle): # rotates image specific angle (based on bird's gravity value)
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image

class GameState():
    def __init__(self, state):
        self.state = state # either "pregame" or "game"
        self.pause = False
        self.score = 0
        self.starting_text_frame = 0 # used to animate text
        self.bird_frame_count = 0 # used to animate bird
        self.check_new_pipe = None # used to score based off passed pipes
        
    def pregame(self):
        display.fill((100,190,250))
        render(display, background_img, pygame.Rect(0, 0, 0, 0))
        render(display, ground_img, ground_rect)
        update_clouds()

        self.bird_frame_count = self.frame_increase(self.bird_frame_count, 20)
        bird_img = animation_handler("bird", 7, self.bird_frame_count)
        render(display, bird_img, bird.rect)
        
        self.starting_text_anim(55, 100, "Press Space to Start")

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_SPACE:
                    self.state = "game"
                elif event.key == K_q:
                    pygame.quit()
                    sys.exit()

        func_update()

    def game(self):
        display.fill((100,190,250))
        render(display, background_img, pygame.Rect(0, 0, 0, 0))
        update_clouds()
        move_pipes()
        self.update_score()
                
        if pipes[0].x <= -50:
            pipes.remove(pipes[0])
            pipes.remove(pipes[0])
            try:
                pipe_movement.remove(pipe_movement[0])
                pipe_movement.remove(pipe_movement[0])
            except:
                pass
        elif pipes[0].x <= 100 and len(pipes) < 4:
            load_pipes(1)
        
        for pipe in pipes:
            if pipe.colliderect(bird.rect):
                bird.game_over = True
            if not bird.game_over:
                pipe.x -= 2
            if pipe.y > 100:
                render(display, pipe_img, pipe)
            else:
                render(display, flip_pipe_img, pipe)

        score_surf = score_font.render(str(int(self.score)), False, (0, 0, 0))
        if self.score < 20:
            display.blit(score_surf,(120,0))
        elif self.score < 200:
            display.blit(score_surf, (100,0))
        elif self.score < 2000:
            display.blit(score_surf, (80,0))
        
        self.bird_frame_count = self.frame_increase(self.bird_frame_count, 20)
        if not bird.game_over:
            bird_img = animation_handler("bird", 7, self.bird_frame_count)
        else:
            bird_img = pygame.image.load("images/bird_1.png").convert()
            bird_img.set_colorkey(WHITE)
            game_over_surf1 = game_over_font.render("Game Over", False, (255,0,0))
            game_over_surf2 = game_over_font.render("Game Over", False, (0,0,0))
            
            display.blit(game_over_surf2, (65,100))
            display.blit(game_over_surf2, (69,100))
            display.blit(game_over_surf2, (67,98))
            display.blit(game_over_surf2, (67,102))
            display.blit(game_over_surf1, (67,100))

            self.starting_text_anim(68, 130, "Press Space to Restart")

        bird.update_angle()
        rot_img = rot_center(bird_img, bird.angle)
        render(display, rot_img, bird.rect)
        render(display, ground_img, ground_rect)

        bird.gravity += 0.3

        if bird.gravity > 6:
            bird.gravity = 6
        elif bird.gravity < -4:
            bird.gravity = -4
        if bird.rect.y <= 0:
            bird.rect.y = 0
            bird.gravity += 0.3

        bird.rect.y += bird.gravity

        if bird.rect.y > 306:
            bird.rect.y = 306
            bird.game_over = True
        elif bird.rect.y < 0:
            bird.rect.y = 0
            bird.game_over = True

        esc_surf = starting_font.render("Esc to Pause", False, (50, 50, 50))
        display.blit(esc_surf, (5,0))
        q_surf = starting_font.render("Q to Quit", False, (50, 50, 50))
        display.blit(q_surf, (5,10))

        while self.pause and not bird.game_over:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.pause = False
                    elif event.key == K_q:
                        pygame.quit()
                        sys.exit()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.pause = True
                if event.key == K_SPACE:
                    if not bird.game_over:
                        bird.gravity += -10
                    elif bird.rect.y > 305:
                        bird.rect.x = 90
                        bird.rect.y = 130
                        bird.bird_reset()
                        self.score = 0
                        self.starting_text_frame = 0
                        self.bird_frame_count = 0
                        for pipe in reversed(pipes):
                            pipes.remove(pipe)
                        load_pipes(0)
                        self.state = "pregame"
                elif event.key == K_q:
                    pygame.quit()
                    sys.exit()

        func_update()

    def frame_increase(self, thing_frames, max_frames): # increases frames of whatever is being animated
        if thing_frames < max_frames:
            thing_frames += 1
        else:
            thing_frames = 0
        return thing_frames

    def update_score(self): # updates the score brother
        if self.check_new_pipe is pipes[0]:
            limit = 1
        else:
            limit = 0
        
        if pipes[0].x < bird.rect.x and limit == 0: # if the leftmost pipe passed the player, +1 score
            self.score += 1
            limit += 1
            self.check_new_pipe = pipes[0] # this and the previous if statement are used to stop the number from rapidly increasing

    def starting_text_anim(self, x, y, str): # used to animate some text
        self.starting_text_frame += 1
        if self.starting_text_frame < 50:
            starting_text_surf = starting_font.render(str, False, (0, 0, 0))
        else:
            starting_text_surf = starting_font.render(str, False, (100, 100, 100))
            if self.starting_text_frame == 70:
                self.starting_text_frame = 0

        if str == "Press Space to Start":
            if self.bird_frame_count < 10:
                bird.rect.y += 1
            elif self.bird_frame_count < 21 and self.bird_frame_count != 10:
                bird.rect.y -= 1
            else:
                pass

        if self.bird_frame_count < 5:
            display.blit(starting_text_surf,(x, y-1))
        elif self.bird_frame_count < 10:
            display.blit(starting_text_surf,(x, y))
        elif self.bird_frame_count < 15:
            display.blit(starting_text_surf,(x, y+1))
        else:
            display.blit(starting_text_surf,(x, y))
        
    def state_manager(self): # if "state", call "state"()
        if self.state == "pregame":
            self.pregame()
        elif self.state == "game":
            self.game()

game_state = GameState("pregame")
load_pipes(0) # 0 means startup-pipe-loading
load_clouds()

while True: # the overarching while loop
    game_state.state_manager()