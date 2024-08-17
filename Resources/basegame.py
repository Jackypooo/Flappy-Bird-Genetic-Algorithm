import pygame
import time
import random

random.seed(0)

# pygame setup
pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS", 30)
screen = pygame.display.set_mode((1000, 800))

clock = pygame.time.Clock()
running = True

class Bird(pygame.sprite.Sprite):
    def __init__(self, size, position):
        pygame.sprite.Sprite.__init__(self)

        self.size = size

        self.image  = pygame.image.load('Resources/Bird.png')
        self.image = pygame.transform.scale(self.image, self.size)
        self.canvas = pygame.Surface(self.size)

        self.position = position
        self.accel = -0.25
        self.velocity = 0

        self.jumpforce = 8

        self.currentScore = 0

    def draw(self, screen):
        self.scoreCanvas = font.render(str(self.currentScore), False, ("White"))

        self.canvas.set_colorkey("Black")
        self.canvas.blit(self.image, [0,0])

        #Draw Bird
        screen.blit(self.canvas, self.position)

        #Draw Score
        screen.blit(self.scoreCanvas, (screen.get_size()[0]/2, 100))

    def updatePos(self):
        self.velocity += self.accel
        self.position = [self.position[0], self.position[1] - self.velocity]

    def jump(self):
        self.velocity = self.jumpforce

    def collisionDetection(self, pipes):
        if self.position[1] < 0:
            return True
        if self.position[1] > screen.get_size()[1]-self.size[1]:
            return True
        
        for x in pipes:
            pipePos = x.get()

            #Check Collision W/ Pipes
            if((pipePos[0] < (self.position[0] + self.size[0] + 50) and pipePos[0] > self.position[0] - self.size[0]+25) and (self.position[1] < pipePos[1] or self.position[1] > pipePos[1]+(pipePos[2 ]-self.size[1]))):
                return True
            
            if(pipePos[0] < self.position[0]-self.size[0]+25):
                self.currentScore = x.score(self.currentScore)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)

        self.w = 100
        self.gap = 250
        self.pos = position
        self.h = random.randint(100,screen.get_size()[1]- self.gap - 300)

        self.pointawarded = False

    def draw(self, screen):
        self.upper = pygame.Rect(self.pos-self.w/2, 0, self.w, self.h)
        self.lower = pygame.Rect(self.upper.left, self.h + self.gap, self.w, 1000)

        pygame.draw.rect(screen, "Green", self.upper)
        pygame.draw.rect(screen, "Green", self.lower)

    def move(self, speed):
        self.pos -= speed

        #Reset
        if self.pos < 0:
            self.pointawarded = False
            self.pos = 1500
            self.h = random.randint(100,screen.get_size()[1]-self.gap + 100)
    
    def get(self):
        return self.pos, self.h, self.gap
    
    def score(self, currentScore):
        if(not self.pointawarded):
            self.pointawarded = True
            currentScore += 1
        return currentScore
        

player = Bird([60,60], [600,300])

pipes = [Pipe(1000),Pipe(1500),Pipe(2000)]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    screen.fill((103, 196, 215))

    for x in pipes:
        x.move(3)
        x.draw(screen)

    player.updatePos()
    player.draw(screen)  

    if(player.collisionDetection(pipes)):running=False

    pygame.display.flip()

    clock.tick(60)

pygame.quit()