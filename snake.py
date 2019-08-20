import pygame
from pygame.locals import *
import random, sys, time, copy

### Globals
# Config
HEIGHT = 160
WIDTH = 160
SIZE = (WIDTH, HEIGHT)  # Game border size
MARGIN = 60
WINHEIGHT = HEIGHT + MARGIN
WINWIDTH = WIDTH + MARGIN
WINSIZE = (WINWIDTH, WINHEIGHT)
GAMEORIGIN = ((WINWIDTH-WIDTH)//2, (WINHEIGHT-HEIGHT)//2) # The topleft corner of the game surface
PIXSCALE = 8
SPEED = 0.5 # Speed multiplier. Scales w/ the time delay of the main game loop

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

### Init
pygame.init()
screen = pygame.display.set_mode(WINSIZE)
gameFont = pygame.font.Font(None, 24)

class Snake:
    def __init__(self):
        self.headRect = Rect((GAMEORIGIN[0]+WIDTH)//2, (GAMEORIGIN[1]+HEIGHT)//2, PIXSCALE, PIXSCALE)   # left, top, width, height
        self.trailingRect = None    # Used to keep track of blacking out the trail
        self.rects = [self.headRect]
        self.direction = [0, 0]
        self.dead = False

    def turn(self, dir):
        self.direction = dir

    def move(self, food):
        oldRects = copy.deepcopy(self.rects)

        self.headRect.move_ip((self.direction[0]*PIXSCALE)*SPEED, (self.direction[1]*PIXSCALE)*SPEED)
        self.rects = [self.headRect]
        for i in range(len(oldRects)-1):
            self.rects.append(oldRects[i])
        
        if self.headRect.x < GAMEORIGIN[0] or self.headRect.x > WIDTH+GAMEORIGIN[0]-PIXSCALE-1 or self.headRect.y < GAMEORIGIN[1] or self.headRect.y > HEIGHT+GAMEORIGIN[1]-PIXSCALE-1:
            # Border touch case
            self.dead = True
        
        for rect in self.rects[1:]:
            if self.headRect.x == rect.x and self.headRect.y == rect.y:   # Body touch case
                self.dead = True
                break

        if abs(self.headRect.x - food.rect.x) < 8 and abs(self.headRect.y - food.rect.y) < 8:
            print("Monch monch")
            food.eaten = True
            self.extend()

            last = oldRects[len(oldRects)-1]
            secondLast = oldRects[len(oldRects)-2]
            trailingDir = [(secondLast.x-last.x)/PIXSCALE, (secondLast.y-last.y)/PIXSCALE]       

            self.trailingRect = last
            self.trailingRect.move_ip(-(trailingDir[0]*PIXSCALE)*SPEED*2, -(trailingDir[1]*PIXSCALE)*SPEED*2)
        elif len(self.rects) == 1:  # No monch monch yet
            self.trailingRect = oldRects[0]
            self.trailingRect.move_ip(-(self.direction[0]*PIXSCALE)*SPEED, -(self.direction[1]*PIXSCALE)*SPEED)   # The size of trailingRect should scale w/ the speed of the snake
        else:
            last = oldRects[len(oldRects)-1]
            secondLast = oldRects[len(oldRects)-2]
            trailingDir = [(secondLast.x-last.x)/PIXSCALE, (secondLast.y-last.y)/PIXSCALE]

            self.trailingRect = last
            self.trailingRect.move_ip(-(trailingDir[0]*PIXSCALE)*SPEED*2, -(trailingDir[1]*PIXSCALE)*SPEED*2)

        return food

    def extend(self):
        last = self.rects[len(self.rects)-1]
        if len(self.rects) == 1:
            lastDir = self.direction
        else:
            secondLast = self.rects[len(self.rects)-2]
            lastDir = [(secondLast.x-last.x)/PIXSCALE, (secondLast.y-last.y)/PIXSCALE] 

        if lastDir[0] > 0:  # Right
            newRect = Rect(last.x-PIXSCALE, last.y, PIXSCALE, PIXSCALE)
        elif lastDir[0] < 0:   # Left
            newRect = Rect(last.x+PIXSCALE, last.y, PIXSCALE, PIXSCALE)
        elif lastDir[1] > 0:    # Down
            newRect = Rect(last.x, last.y-PIXSCALE, PIXSCALE, PIXSCALE)
        elif lastDir[1] < 0:   # Up
            newRect = Rect(last.x, last.y+PIXSCALE, PIXSCALE, PIXSCALE)

        self.rects.append(newRect)

class Food:
    def __init__(self):
        self.rect = Rect(random.randint(GAMEORIGIN[0]+PIXSCALE, GAMEORIGIN[0]+HEIGHT-PIXSCALE), random.randint(GAMEORIGIN[1]+PIXSCALE, GAMEORIGIN[1]+WIDTH-PIXSCALE), PIXSCALE, PIXSCALE)
        self.eaten = False

def main():
    # Init game vars
    score = 0
    scoreSurf = gameFont.render(f"Score: {score}", 0, BLACK)
    gameEnd = False

    # Init snake
    snake = Snake()
    snakeSurf = pygame.Surface((PIXSCALE, PIXSCALE))
    snakeSurf.fill(WHITE)

    # Init food
    food = Food()
    foodSurf = pygame.Surface((PIXSCALE, PIXSCALE))
    foodSurf.fill(GREEN)

    # Init game surface
    gameSurf = pygame.Surface((HEIGHT, WIDTH))  # The gameplay area
    gameSurf.fill(BLACK)

    # Draw on screen
    screen.fill(WHITE)
    screen.blit(gameSurf, GAMEORIGIN)
    screen.blit(snakeSurf, (snake.headRect.x, snake.headRect.y))
    screen.blit(foodSurf, (food.rect.x, food.rect.y))
    screen.blit(scoreSurf, (6, 12))    # Top left corner
    pygame.display.flip()   # Update display

    # Main game loop
    while True:
        for event in pygame.event.get(): # Going through the event queue
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif not snake.dead and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and (snake.direction != [0, -1] and snake.direction != [0, 1]):
                    snake.turn([0, -1])
                elif event.key == pygame.K_a and (snake.direction != [-1, 0] and snake.direction != [1, 0]):
                    snake.turn([-1, 0])
                elif event.key == pygame.K_s and (snake.direction != [0, 1] and snake.direction != [0, -1]):
                    snake.turn([0, 1])
                elif event.key == pygame.K_d and (snake.direction != [1, 0] and snake.direction != [-1, 0]):
                    snake.turn([1, 0])

        if snake.dead and not gameEnd:
            endSurf = gameFont.render(f"Game Over!", 0, WHITE)
            screen.fill(BLACK)
            screen.blit(endSurf, ((WINWIDTH//2)-36, (WINHEIGHT//2)-12))
            pygame.display.flip()
            gameEnd = True
        else:
            food = snake.move(food)    # Moving snake

            if snake.dead:
                continue

            ### Drawing
            screen.fill(WHITE)
            screen.blit(gameSurf, GAMEORIGIN)
            screen.blit(foodSurf, (food.rect.x, food.rect.y))
            
            if food.eaten:
                score += 1

                # Black out old food
                foodSurf.fill(BLACK)
                screen.blit(foodSurf, (food.rect.x, food.rect.y))

                food = Food()   # Make more food for the snake!

                # Green in new food
                foodSurf.fill(GREEN)
                screen.blit(foodSurf, (food.rect.x, food.rect.y))

            snakeSurf.fill(WHITE)
            for rect in snake.rects:    # Filling in new positions
                screen.blit(snakeSurf, (rect.x, rect.y))

            # Score
            scoreSurf.fill(WHITE)
            screen.blit(scoreSurf, (6, 12))    # Blacking out old score
            scoreSurf = gameFont.render(f"Score: {score}", 1, BLACK)
            screen.blit(scoreSurf, (6, 12))

            # Trailing rect
            if snake.trailingRect != None:
                snakeSurf.fill(BLACK)
                screen.blit(snakeSurf, (snake.trailingRect.x, snake.trailingRect.y))

            pygame.display.flip()

        time.sleep(0.040)

if __name__ == "__main__":
    main()