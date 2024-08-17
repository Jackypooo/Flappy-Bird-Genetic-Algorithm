import pygame
import random
import time

def sim(gen, iteration, inputspeed, highscoreTime, seed=0):

    #Choice seed so agents go through the same level each iteration
    random.seed(seed)

    # pygame setup
    pygame.init()
    pygame.font.init()

    #Pygame Stuff
    font = pygame.font.SysFont("Comic Sans MS", 30)
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Sim " + str(iteration))

    clock = pygame.time.Clock()
    running = True

    #Class for player object
    class Bird(pygame.sprite.Sprite):
        def __init__(self, moveset, size=[60,60], position=[400,300], jumpspeed=4):
            '''Initilization Method for Player Object'''
            pygame.sprite.Sprite.__init__(self)

            #Determines size of bird
            self.size = size

            #Tracks Game Time
            self.deltatime = 1

            #Initializes the moves the bird takes throughout the level
            self.moves = moveset

            #Initializes the bird image and scales it
            self.image  = pygame.image.load('Bird.png')
            self.image = pygame.transform.scale(self.image, self.size)
            self.canvas = pygame.Surface(self.size)

            #Initializes Movement Variables
            self.position = position
            self.accel = -0.25
            self.velocity = 0

            #Initializes how often the bird can jump
            self.jumpspeed = jumpspeed

            #Initializes other jump variables
            self.jumpforce = 8
            self.canJump = True

            #Tracks score throughoout game
            self.currentScore = 0

            #Initializes life and last move time 
            self.isAlive = True
            self.lastmove = 0

            #Tracks the time the bird started
            self.startTime = time.time()

            #Tracks the used inputs before death
            self.usedInputs = 0
        
        def update(self, screen):
            '''General Update Function'''
            #Updates Deltatime
            self.deltatime += 1/self.jumpspeed
            self.deltatimerounded = int(round(self.deltatime, 1))

            #Determines if bird can jump
            if(self.deltatimerounded != self.lastmove):
                self.lastmove = self.deltatimerounded
                self.canJump = True
                self.usedInputs += 1
            else:
                self.canJump = False

            #Updates Position and Draws bird to screen
            self.updatePos()
            self.draw(screen)

        def draw(self, screen):
            '''Method used to draw bird and score to the screen'''
            #Sets Score Variable based on aliveagents
            self.aliveagentscanvas = font.render("Alive Agents: " + str(numAliveAgents), False, ("White"))
            self.highsorecanvas = font.render("Highest Time: " + str(round(highscoreTime, 2)), False,("White"))

            self.canvas.set_colorkey("Black")
            self.canvas.blit(self.image, [0,0])

            #Draw Bird
            screen.blit(self.canvas, self.position)

            #Draw Number of Alive Agents and Highscore to Screen
            screen.blit(self.aliveagentscanvas, (10, 25))
            screen.blit(self.highsorecanvas, (10, 75))


        def updatePos(self):
            '''Variable that handles birds movement'''
            #Jump
            if(self.moves[self.deltatimerounded] == 0 and self.canJump):
                self.velocity = self.jumpforce

            #Fall
            self.velocity += self.accel
            self.position = [self.position[0], self.position[1] - self.velocity]

        def collisionDetection(self, pipes):
            '''Function for detecting colision and returning'''
            #Determines if death occured above or below gap

            #Determines whats returned if collision occurs
            ToReturn = [True, self.currentScore, time.time()-self.startTime, self.usedInputs, self.moves]

            #If touching roof then death
            if self.position[1] < 0:
                ToReturn.append(0)
                return ToReturn
            
            #If Touching Flooor then death
            if self.position[1] > screen.get_size()[1]-self.size[1]:
                ToReturn.append(1)
                return ToReturn
            
            #Get the features of each pipe on screen
            for x in pipes:

                #Check Collision W/ Pipes
                WithinPipeL = x.pos < self.position[0] + self.size[0] + 50
                WithinPipeR = x.pos > self.position[0] - self.size[0] + 25
                
                AbovePipe = self.position[1] < x.h
                BelowPipe = self.position[1] > x.h+(x.gap-self.size[1])

                #Collision Logic
                if(WithinPipeL and WithinPipeR) and (AbovePipe or BelowPipe):
                    if(AbovePipe):
                        ToReturn.append(0)
                    else:
                        ToReturn.append(1)
                    return ToReturn
                
                #Increase score if past Pipe
                if(x.pos < self.position[0]-self.size[0]+25):
                    self.currentScore = x.score(self.currentScore)

    #Class for pipe object
    class Pipe(pygame.sprite.Sprite):
        def __init__(self, position):
            '''Initialization function that generates width, gap, position, and height of pipes'''
            pygame.sprite.Sprite.__init__(self)

            #Pipe Variables
            self.w = 100
            self.gap = 250
            self.pos = position
            self.h = random.randint(100,screen.get_size()[1]- self.gap - 300)

            self.pointawarded = False

        def draw(self, screen):
            '''Function to draw pipe to screen'''
            #Creates upper and lower parts of pipes
            self.upper = pygame.Rect(self.pos-self.w/2, 0, self.w, self.h)
            self.lower = pygame.Rect(self.upper.left, self.h + self.gap, self.w, 1000)

            #Draws upper and lower parts of pipes
            pygame.draw.rect(screen, "Green", self.upper)
            pygame.draw.rect(screen, "Green", self.lower)

        def move(self, speed):
            '''Function to move pipes'''
            #Moves pipes based on speed
            self.pos -= speed

            #Reset if pipe goes off of screen
            if self.pos < 0:
                self.pointawarded = False
                self.pos = 1500
                #Randomize height of each pipe
                self.h = random.randint(100,screen.get_size()[1]-self.gap + 100)
        
        def score(self, currentScore):
            '''Function to award points to birds'''
            if(not self.pointawarded):
                self.pointawarded = True
                currentScore += 1
            return currentScore

    #Agent Generation
    agents = []
    for x in gen:
        agents.append([Bird(moveset=x.moveset, jumpspeed=inputspeed)])

    #Calculate number of alive agents
    numAliveAgents = len(agents)

    #Create Pipes
    pipes = [Pipe(1000),Pipe(1500),Pipe(2000)]

    while running:
        #Get if quit button pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #Background Color
        screen.fill((103, 196, 215))

        #Manage Pipes
        for x in pipes:
            x.move(3)
            x.draw(screen)

        #Manage Multiple Agents
        for x in agents:
            if x[0].isAlive:
                x[0].update(screen)

                #Checks Collisions
                collision = x[0].collisionDetection(pipes)
                #If There is a collision delete agent and append it to the output
                if(collision):
                    collision.remove(True)

                    x[0].isAlive=False
                    numAliveAgents -= 1

                    #Append return values to agents in other script
                    for i in collision:
                        x.append(i)

        #Check to make sure at least one agent is alive
        if numAliveAgents < 1:running = False
        
        #Update Screen
        pygame.display.flip()
        clock.tick(60)

    #Quit Game
    pygame.quit()
    
    #Return Agent Outputs Including Return Values from death
    return(agents)

