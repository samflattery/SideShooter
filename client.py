# import module_manager
# module_manager.review()
# Module Manager code from Austin Schick
import pygame
import random
import math
import sys

from Player import *
from Blocks import *
from Enemy import *
from Weapons import *

# Sockets Setup
import socket
import threading
from queue import Queue


def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

# Animation Framework

class PygameGame(object):

    def __init__(self, width=600, height=700, fps=50, title="SideShooter"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (0, 0, 0)
        pygame.init()
        self.font = pygame.font.SysFont(None, 25)

    def init(self, replay=False):
        # Groups
        if not replay:
            self.playerGroup = pygame.sprite.Group()
            self.otherPlayerGroup = pygame.sprite.Group()
        self.bulletGroup = pygame.sprite.Group()
        self.enemyBulletGroup = pygame.sprite.Group()
        self.enemyGroup = pygame.sprite.Group()
        self.backgroundGroup = pygame.sprite.Group()
        self.questionBlockGroup = pygame.sprite.Group()
        self.backgroundSkyGroup = pygame.sprite.LayeredUpdates()
        self.mountainsGroup = pygame.sprite.LayeredUpdates()
        self.transparentGroup = pygame.sprite.Group()
        self.blackBlockGroup = pygame.sprite.Group()
        self.otherBulletGroup = pygame.sprite.Group()

        # Walking Animation
        self.walkRightCount = 0
        self.walkLeftCount = 0
        self.spriteIndex = 0
        self.walkRight = []
        self.walkLeft = []
        for i in range(1, 11):
            self.walkRight.append(pygame.image.load("Run/R%d.png" % i).convert_alpha())
            self.walkLeft.append(pygame.image.load("Run/L%d.png" % i).convert_alpha())

        # Enemy Animation
        self.tankExplodeR = []
        self.tankExplodeL = []
        self.tankR = pygame.image.load("Tanks/tankR.png").convert_alpha()
        self.tankR = pygame.transform.scale(self.tankR, (90, 60))
        self.tankL = pygame.image.load("Tanks/tankL.png").convert_alpha()
        self.tankL = pygame.transform.scale(self.tankL, (90, 60))
        self.enemyPics = [self.tankL, self.tankR]

        # Exploding Animatiion
        self.enemyDead = []
        for i in range(1, 6):
            self.tankExplodeR.append(pygame.image.load("Tanks/tankExplodeR%d.png" % i).convert_alpha())
        for i in range(1, 6):
            self.tankExplodeL.append(pygame.image.load("Tanks/tankExplodeL%d.png" % i).convert_alpha())
        for i in range(5):
            image1 = self.tankExplodeR.pop(0)
            image1 = pygame.transform.scale(image1, (90, 60))
            self.tankExplodeR.append(image1)
            image2 = self.tankExplodeL.pop(0)
            image2 = pygame.transform.scale(image2, (90, 60))
            self.tankExplodeL.append(image2)

        # Background
        self.background = pygame.image.load("Background/sky.png").convert_alpha()
        self.backgroundRect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (self.backgroundRect.width, self.height - 90))
        self.backgroundSkyGroup.add(Background(self.background, self.height, 0))

        self.mountains = pygame.image.load("Background/mountains.png").convert_alpha()
        self.mountainsRect = self.mountains.get_rect()
        self.moountains = pygame.transform.scale(self.mountains, (self.mountainsRect.width, self.height - 90))
        self.mountainsGroup.add(Background(self.mountains, self.height, 0))

        # Guns
        self.machineGunSymbol = pygame.image.load("Guns/AK47.png").convert_alpha()
        self.machineGunSymbol = pygame.transform.scale(self.machineGunSymbol, (100, 50))
        self.handgunSymbol = pygame.image.load("Guns/handgun.png").convert_alpha()
        self.handgunSymbol = pygame.transform.scale(self.handgunSymbol, (50, 50))
        self.shotgunSymbol = pygame.image.load("Guns/shotgun.png").convert_alpha()
        self.shotgunSymbol = pygame.transform.scale(self.shotgunSymbol, (70, 50))
        self.machineGun = pygame.transform.scale(self.machineGunSymbol, (30, 15))
        self.handgun = pygame.transform.scale(self.handgunSymbol, (20, 20))
        self.shotgun = pygame.transform.scale(self.shotgunSymbol, (30, 11))
        self.currentGun = self.handgun
        self.newWeapon = None
        self.floatingWeaponGroup = pygame.sprite.Group()

        # Bullets
        self.bulletR = pygame.image.load("Sprites/bulletR.png").convert_alpha()
        self.bulletL = pygame.image.load("Sprites/bulletL.png").convert_alpha()
        self.bulletR = pygame.transform.scale(self.bulletR, (15, 5))
        self.bulletL = pygame.transform.scale(self.bulletL, (15, 5))
        self.bulletUpR = pygame.transform.rotate(self.bulletR, 15)
        self.bulletDownR = pygame.transform.rotate(self.bulletR, -15)
        self.bulletUpL = pygame.transform.rotate(self.bulletL, -15)
        self.bulletDownL = pygame.transform.rotate(self.bulletR, 15)

        # World Building Sprites
        self.grass1 = pygame.image.load("Blocks/grass1.png").convert_alpha()
        self.grass2 = pygame.image.load("Blocks/grass2.png").convert_alpha()
        self.grass3 = pygame.image.load("Blocks/grass3.png").convert_alpha()
        self.grass4 = pygame.image.load("Blocks/grass4.png").convert_alpha()
        self.grass5 = pygame.image.load("Blocks/grass5.png").convert_alpha()
        self.grass6 = pygame.image.load("Blocks/grass6.png").convert_alpha()
        self.grassTypes = [self.grass1, self.grass2, self.grass3, self.grass4, self.grass5, self.grass6]
        self.dirtTop = pygame.image.load("Blocks/dirtTop.png").convert_alpha()
        self.dirtBottom = pygame.image.load("Blocks/dirtBottom.png").convert_alpha()
        self.airBlock = pygame.image.load("Blocks/airBlock.png").convert_alpha()
        self.questionBlock = pygame.image.load("Blocks/questionBlock.png").convert_alpha()
        self.transparentBlock = pygame.image.load("Blocks/transparentBlock.png").convert_alpha()
        self.black = pygame.image.load("Blocks/black.png").convert_alpha()

        # World Building Variables
        self.groundLevel = self.height
        self.cols = self.width // 30
        self.hillBlocks = [self.groundLevel - 120]
        self.drawingHill = False
        self.decreasing = False
        self.drawingHole = False
        self.holeWidthCount = 0
        self.drawingAirBlock = False
        self.blockLengthCount = 0
        self.isQuestionBlock = False
        self.lastBlock = None
        self.lastHillBlock = self.groundLevel - 90
        self.goStraight = False
        self.drewQuestionBlock = True
        self.consecutiveHoles = 0
        self.noHill = False
        self.hillCount = 2
        self.numHoles = None
        self.previousWasBlock = True
        self.canSpawnEnemies = True
        self.lastHillX = self.width
        self.consecutiveAirBlocks = 1
        self.airBlockNumber = None
        self.airBlockHeight = None

        # Player
        if not replay:
            self.player = Player("Lonely", self.walkRight[0], self.width // 4, self.groundLevel - 90)
            self.otherPlayers = dict()
            self.playerGroup.add(self.player)
        self.isMovingRight = False
        self.isMovingLeft = False
        self.isScrollingRight = False
        self.isScrollingLeft = False
        self.isJumping = False
        self.isFacing = "R"

        # Sockets Data
        self.scrollX = 0
        self.timer = 0
        self.madeBackground = False
        self.speed = self.player.speedX
        self.playerDraws = False
        self.shotBullet = False
        self.newEnemyCoordinates = None
        self.drewEnemy = False
        self.bulletOrigin = None
        self.enemyShot = False
        self.otherDrawingHill = False
        self.otherDrawingAirBlock = False

        # Display
        self.score = 0
        self.difficulty = "25%"
        self.machineGunAmmo = 100
        self.shotgunAmmo = 10
        self.mode = "gameMode"
        self.otherDead = False
        self.newGame = False
        self.otherNewGame = False
        self.text = "Press 'r' to restart!"
        self.playerDied = None
        if replay:
            self.twoPlayer = True
        else:
            self.twoPlayer = False

    def keyPressed(self, keyCode, modifier):
        # handles key presses
        if self.mode == "gameMode":
            if keyCode == pygame.K_RIGHT:
                self.isMovingRight = True
                self.isFacing = "R"
            if keyCode == pygame.K_LEFT:
                self.isMovingLeft = True
                self.isFacing = "L"
            if keyCode == pygame.K_UP:
                self.isJumping = True
                self.player.rect.y -= 2
            if keyCode == pygame.K_SPACE:
                self.shotBullet = True
                if self.currentGun == self.handgun:
                    if self.isFacing == "R":
                        self.player.shoot(self.bulletR, self.bulletGroup, self.player.rect.right + 7, self.player.rect.centery - 20, 1)
                    if self.isFacing == "L":
                        self.player.shoot(self.bulletL, self.bulletGroup, self.player.rect.left - 7, self.player.rect.centery - 20, -1)
                elif self.currentGun == self.shotgun:
                    self.shotgunAmmo -= 1
                    if self.isFacing == "R":
                        self.player.shoot(self.bulletDownR, self.bulletGroup, self.player.rect.right + 7, self.player.rect.centery - 20, 1, 15)
                        self.player.shoot(self.bulletR, self.bulletGroup, self.player.rect.right + 7, self.player.rect.centery - 20, 1, 0)
                        self.player.shoot(self.bulletUpR, self.bulletGroup, self.player.rect.right + 7, self.player.rect.centery - 20, 1, -15)
                    if self.isFacing == "L":
                        self.player.shoot(self.bulletUpL, self.bulletGroup, self.player.rect.left - 7, self.player.rect.centery - 20, -1, 15)
                        self.player.shoot(self.bulletL, self.bulletGroup, self.player.rect.left - 7, self.player.rect.centery - 20, -1, 0)
                        self.player.shoot(self.bulletDownL, self.bulletGroup, self.player.rect.left - 7, self.player.rect.centery - 20, -1, -15)

        elif self.mode == "gameOver" and not self.twoPlayer:
            if keyCode == pygame.K_r:
                self.init()

        elif self.mode == "gameOver":
            if keyCode == pygame.K_r:
                self.newGame = True
                self.text = "Waiting for other player to press 'r'"

    def keyReleased(self, keyCode, modifier):
        # handles key releases
        if keyCode == pygame.K_RIGHT:
            self.isMovingRight = False
        if keyCode == pygame.K_LEFT:
            self.isMovingLeft = False

    def startNewGame(self):
        # handles the starting of a new game, resetting it to its original state
        self.otherDead = False
        self.init(True)
        currPID = self.player.PID
        if currPID == "Player1":
            otherPID = "Player2"
        elif currPID == "Player2":
            otherPID = "Player1"
        self.player = Player(currPID, self.walkRight[0], self.width // 4, self.groundLevel - 90)
        self.playerGroup.empty()
        self.playerGroup.add(self.player)
        otherPlayer = Player(otherPID, self.walkRight[0], self.width // 4, self.groundLevel - 90)
        self.otherPlayerGroup.empty()
        self.otherPlayers = dict()
        self.otherPlayers[otherPID] = otherPlayer
        self.otherPlayerGroup.add(self.otherPlayers[otherPID])
        for player in self.otherPlayerGroup:
            player.rect.centerx = self.width // 4
            player.rect.bottom = self.groundLevel - 90

    # World Generation

    def drawBlock(self, type, x, y):
        # draws a sequence of blocks from the y position to the bottom of the screen
        self.backgroundGroup.add(BackgroundBlock(type, x, y))
        for i in range(1, ((self.groundLevel) - (y + 30)) // 30 + 1):
            self.backgroundGroup.add(BackgroundBlock(self.dirtBottom, x, self.groundLevel - (30 * i)))

    def drawBlackBlock(self, x, y):
        # draws a sequence of black blocks from the y position to the bottom of the screen
        for i in range((self.groundLevel - y) // 30):
            self.blackBlockGroup.add(BackgroundBlock(self.black, x, y + (30 * i)))

    def holesInHills(self, hillCount):
        # handles the increasingly difficulty procedural generation by spawning more and more holes in the hills
        if self.numHoles == None:
            if hillCount <= 3:
                self.numHoles = random.choice([1, hillCount])
            else:
                self.numHoles = random.choice([1,3])
        if self.consecutiveHoles >= self.numHoles:
            self.consecutiveHoles = 0
            self.noHill = False
            self.numHoles = None
            self.previousWasBlock = True
            self.canSpawnEnemies = True
        else:
            choice = random.choice([1, 0, 0])
            if choice == 1 or self.consecutiveHoles > 0:
                self.consecutiveHoles += 1
                self.noHill = True
                self.previousWasBlock = False
                self.canSpawnEnemies = False
                if self.decreasing:
                    self.drawTransparent(self.width, self.lastHillBlock)
                else:
                    self.drawTransparent(self.width, self.lastHillBlock - 30)
            elif choice == 0:
                self.noHill = False
                self.previousWasBlock = True
                self.canSpawnEnemies = True

    def drawTransparent(self, x, y):
        # draws a transparent block that prevents enemies falling off platforms and into holes
        self.transparentGroup.add(BackgroundBlock(self.transparentBlock, x, y - 30))
        self.transparentGroup.add(BackgroundBlock(self.transparentBlock, x, y))
        self.transparentGroup.add(BackgroundBlock(self.transparentBlock, x, y + 30))

    def drawAirBarrier(self, x):
        # same as drawTransparent but draws an entire screen height of transparent blocks
        for i in range(self.height // 30):
            self.transparentGroup.add(BackgroundBlock(self.transparentBlock, x, (30 * i)))

    def generateHill(self, height):
        # generates the next row of a hill up until a maximum height
        self.lastHillX = self.width
        if self.hillCount == 0:
            self.consecutiveHoles = 0
        elif self.hillCount == 1:
            self.holesInHills(1)
        elif self.hillCount == 2:
            self.holesInHills(2)
        elif self.hillCount >= 3:
            self.holesInHills(3)
        if self.noHill:
            self.drawBlackBlock(self.width, self.hillBlocks[-1] + 60)
        if not self.noHill:
            self.lastHillBlock = self.hillBlocks[-1]
            if not self.decreasing:
                self.consecutiveHoles = 0
                nextMove = random.choice(["up", "straight"])
                grassType = random.choice(self.grassTypes)
                if len(self.hillBlocks) == 1:
                    self.drawBlock(grassType, self.width, self.lastHillBlock)
                    self.hillBlocks.append(self.lastHillBlock)
                elif nextMove == "straight" or self.goStraight:
                    self.drawBlock(grassType, self.width, self.lastHillBlock)
                    self.hillBlocks.append(self.lastHillBlock)
                    self.goStraight = False
                elif nextMove == "up":
                    self.drawBlock(grassType, self.width, self.lastHillBlock - 30)
                    self.hillBlocks.append(self.lastHillBlock - 30)
                    self.goStraight = True
                    if self.lastHillBlock - 30 < height:
                        self.decreasing = True
            else:
                self.consecutiveHoles = 0
                nextMove = random.choice(["down", "straight"])
                grassType = random.choice(self.grassTypes)
                if nextMove == "straight" or self.goStraight:
                    self.drawBlock(grassType, self.width, self.lastHillBlock)
                    self.hillBlocks.append(self.lastHillBlock)
                    self.goStraight = False
                elif nextMove == "down":
                    self.goStraight = True
                    if self.lastHillBlock + 30 <= self.groundLevel - 90:
                        self.drawBlock(grassType, self.width, self.lastHillBlock + 30)
                        self.hillBlocks.append(self.lastHillBlock + 30)
                    else:
                        self.drawingHill = False
                        self.decreasing = False
                        self.goStraight = False
                        self.hillBlocks = [self.groundLevel - 120]
                        self.hillCount += 1
                        self.drawBlock(grassType, self.width, self.groundLevel - 90)

    def createGround(self):
        # creates the ground at the very beginning
        for col in range(self.cols + 1):
            grassType = random.choice(self.grassTypes)
            self.drawBlock(grassType, 30 * col, self.groundLevel - 90)
        self.madeBackground = True

    def deleteGround(self):
        # deletes the ground when it's more than 2 screen widths behind the player to save CPU time
        for block in self.backgroundGroup:
            if block.rect.right < -2 * self.width:
                block.kill()

    def drawQuestionBlock(self, x, y):
        # draws a question block
        self.questionBlockGroup.add(QuestionBlock(self.questionBlock, x, y))
        self.backgroundGroup.add(QuestionBlock(self.questionBlock, x, y))

    def drawAirBlock(self, x, y):
        # draws an air block
        self.backgroundGroup.add(BackgroundBlock(self.airBlock, x, y))

    # Random Events
    def randomHole(self):
        # generates a random hole with its width and frequency depending on how far the player is
        if self.hillCount <= 1:
            number = random.randint(0, 1000)
            if number > 990:
                self.drawingHole = True
                self.holeWidth = random.randrange(30, 90, 30)
        elif self.hillCount == 2:
            number = random.randint(0, 100)
            if number > 99:
                self.drawingHole = True
                self.holeWidth = random.randrange(60, 120, 30)
        elif self.hillCount == 3:
            number = random.randint(0, 100)
            if number > 95:
                self.drawingHole = True
                if not self.drawingAirBlock:
                    self.randomAirBlock(True)
                self.holeWidth = random.randrange(90, 240, 30)
        elif self.hillCount > 3:
            self.drawingHole = True
            self.holeWidth = 1000

    def randomHill(self, draw=False):
        # randomly decides to generate a hill
        number = random.randint(0, 100000)
        if number >= 99000 or draw:
            self.drawingHill = True
            self.hillHeight = random.randint(self.height // 3, self.height // 2)

    def randomAirBlock(self, draw=False):
        # randomly decides to generate a hole
        number = random.randint(0, 10000)
        if number >= 9900 or self.hillCount > 3 or draw:
            self.drawingAirBlock = True
            self.isQuestionBlock = False
            self.blockLength = random.randrange(90, 180, 30)
            self.airBlockHeight = random.randint(self.groundLevel - 250, self.groundLevel - 200)

    def newAirBlock(self, y):
        # generates a new airBlock directly after an existing airBlock to create a platform system
        toDraw = random.choice([True, False])
        direction = 1
        if self.hillCount >= 1:
            if self.airBlockNumber == None:
                self.airBlockNumber = random.randrange(4 * self.hillCount, 8 * self.hillCount)
            if self.consecutiveAirBlocks < self.airBlockNumber:
                toDraw = True
                self.consecutiveAirBlocks += 1
            else:
                toDraw = False
                self.randomHill(True)
            if y < 200:
                direction = -1
            elif y < self.groundLevel - 400:
                direction = random.choice([1, -1])
            elif y > self.groundLevel - 150:
                direction = 1
        if toDraw:
            self.drawingAirBlock = True
            self.blockLength = random.randrange(90, 180, 30)
            if direction == 1:
                self.airBlockHeight = random.randrange(y - 150, y - 100)
            elif direction == -1:
                self.airBlockHeight = random.randrange(y + 100, y + 150)
        else:
            self.consecutiveAirBlocks = 1
            self.drawingAirBlock = False
            self.airBlockNumber = None

    def randomQuestionBlock(self):
        # randomly decides to draw a questionBlock
        choice = random.choice([True, False, False, False, False])
        if choice == True:
            self.drawingQuestionBlock = True
            return True

    def backgroundPic(self):
        # draws the pictures in the background
        if self.backgroundSkyGroup.get_sprite(-1).rect.right < self.width:
            self.backgroundSkyGroup.add(Background(self.background, self.height, self.width - 10))
        if self.mountainsGroup.get_sprite(-1).rect.right < self.width:
            self.mountainsGroup.add(Background(self.mountains, self.height, self.width - 10))

    # Player Movement

    def scrollRight(self):
        # handles the players' scroll to the right
        if self.player.rect.x >= self.width // 2:
            self.isScrollingRight = True
        else:
            self.isScrollingRight = False
        if self.isScrollingRight and self.isMovingRight:
            self.drawNew = True
            self.scrollX += self.speed
            if not self.lastBlock == None:
                self.lastBlock -= self.speed
            for enemy in self.enemyGroup:
                enemy.rect.x -= self.speed
            for player in self.otherPlayerGroup:
                player.rect.centerx -= self.speed
            for block in self.backgroundGroup:
                block.rect.x -= self.speed
                if block.rect.right > self.width:
                    self.drawNew = False
            for block in self.questionBlockGroup:
                block.rect.x -= self.speed
            for weapon in self.floatingWeaponGroup:
                weapon.rect.x -= self.speed
            for bg in self.backgroundSkyGroup:
                bg.rect.x -= 1
            for bg in self.mountainsGroup:
                bg.rect.x -= 5
            for block in self.transparentGroup:
                block.rect.x -= self.speed
            for block in self.blackBlockGroup:
                block.rect.x -= self.speed
            self.lastHillX -= self.speed
            if self.scrollX % 30 == 0 and self.drawNew and self.playerDraws:
                self.lastBlock = self.width
                if not self.drawingHill and not self.drawingHole and not self.hillCount > 3:
                    grassType = random.choice(self.grassTypes)
                    self.drawBlock(grassType, self.width, self.groundLevel - 90)
                elif self.drawingHill:
                    self.generateHill(self.hillHeight)
                elif self.drawingHole:
                    self.holeWidthCount += 30
                    if self.holeWidthCount <= self.holeWidth:
                        if self.drawingHill:
                            self.drawingHole = False
                        if self.drawingAirBlock:
                            self.drawTransparent(self.width, self.groundLevel - 90)
                        else:
                            self.drawAirBarrier(self.width)
                        self.drawBlackBlock(self.width, self.groundLevel - 60)
                    else:
                        self.drawingHole = False
                        grassType = random.choice(self.grassTypes)
                        self.drawBlock(grassType, self.width, self.groundLevel - 90)
                        self.holeWidthCount = 0
                if self.drawingAirBlock:
                    self.blockLengthCount += 30
                    if self.blockLengthCount <= self.blockLength:
                        if self.randomQuestionBlock() and not self.isQuestionBlock:
                            self.drawQuestionBlock(self.width, self.airBlockHeight)
                            self.isQuestionBlock = True
                            self.drewQuestionBlock = True
                        else:
                            self.drawAirBlock(self.width, self.airBlockHeight)
                    else:
                        self.drawingAirBlock = False
                        self.blockLengthCount = 0
                        self.newAirBlock(self.airBlockHeight)

    def scrollLeft(self):
        # handles the players' scroll to the left
        if self.player.rect.x <= self.width / 8 and not self.scrollX == 0:
            self.isScrollingLeft = True
        else:
            self.isScrollingLeft = False
        if self.isScrollingLeft and self.isMovingLeft:
            self.scrollX -= self.speed
            if not self.lastBlock == None:
                self.lastBlock += self.speed
            for block in self.backgroundGroup:
                block.rect.x += self.speed
            for enemy in self.enemyGroup:
                enemy.rect.x += self.speed
            for player in self.otherPlayerGroup:
                player.rect.centerx += self.speed
            for block in self.questionBlockGroup:
                block.rect.x += self.speed
            for weapon in self.floatingWeaponGroup:
                weapon.rect.x += self.speed
            for bg in self.backgroundSkyGroup:
                bg.rect.x += 1
            for bg in self.mountainsGroup:
                bg.rect.x += 5
            for block in self.transparentGroup:
                block.rect.x += self.speed
            for block in self.blackBlockGroup:
                block.rect.x += self.speed
            self.lastHillX += self.speed

    def moveRight(self):
        # moves the player right
        if self.isMovingRight and not self.isScrollingRight:
            self.player.moveRight()

    def moveLeft(self):
        # moves the player left
        if self.isMovingLeft and not self.isScrollingLeft and not self.player.rect.left <= 10:
            self.player.moveLeft()

    def jump(self):
        # makes the player jump
        if self.isJumping:
            self.isOnBlock()
            if self.isJumping:
                self.player.jump()

    def fall(self):
        # makes the player fall
        if not self.isOnBlock():
            self.player.fall()

    def changePic(self):
        # inspired by https://www.youtube.com/watch?v=UdsNBIzsmlI&t=833s
        # changes the players' pictures to create an animation
        if self.isMovingRight:
            self.spriteIndex = self.walkRightCount
            if self.walkRightCount >= 10:
                self.spriteIndex = self.walkRightCount % 10
            self.walkRightCount += 1
            self.player.changePic(self.walkRight[self.spriteIndex])
        elif self.isMovingLeft:
            self.spriteIndex = self.walkLeftCount
            if self.walkLeftCount >= 10:
                self.spriteIndex = self.walkLeftCount % 10
            self.walkLeftCount += 1
            self.player.changePic(self.walkLeft[self.spriteIndex])

    def inHole(self):
        # returns whether or not the player is in a hole
        collisions = pygame.sprite.groupcollide(self.playerGroup, self.blackBlockGroup, False, False)
        if len(collisions) > 0:
            self.isJumping = False
            return True


    # Collisions

    def hitQuestionMarkBlock(self):
        # handles the player's collision with a question block
        for questionBlock in self.questionBlockGroup:
            if (questionBlock.rect.left <= self.player.rect.right <= questionBlock.rect.right or questionBlock.rect.left <= self.player.rect.right <= questionBlock.rect.right) and questionBlock.rect.top <= self.player.rect.top <= questionBlock.rect.bottom:
                choice = random.choice([1,1])
                if choice == 0:
                    self.newWeapon = self.machineGun
                    newWeapon = "machineGun"
                elif choice == 1:
                    self.newWeapon = self.shotgun
                    newWeapon = "shotgun"
                self.floatingWeaponGroup.add(FloatingWeapon(self.newWeapon, questionBlock.rect.centerx, questionBlock.rect.top - 15))
                self.questionBlockGroup.remove(questionBlock)
                return(newWeapon, questionBlock.rect.x, questionBlock.rect.top - 15)

    def isOnBlock(self):
        # returns whether the player is standing on a block or in the air
        if not self.inHole():
            if self.isJumping:
                for block in self.backgroundGroup:
                    if self.player.rect.bottom >= block.rect.top and not self.player.rect.top >= block.rect.top and block.rect.left + 10 < self.player.rect.right and self.player.rect.left < block.rect.right - 10:
                        self.player.rect.bottom = block.rect.top
                        self.player.fallSpeed = 0
                        self.isJumping = False
                        return True
            else:
                for block in self.backgroundGroup:
                    if self.player.rect.bottom >= block.rect.top and not self.player.rect.top >= block.rect.top and block.rect.left <= self.player.rect.centerx <= block.rect.right:
                        self.player.rect.bottom = block.rect.top
                        self.player.fallSpeed = 0
                        self.isJumping = False
                        return True
            return False

    def collisions(self):
        # prevents the player from running through walls
        inHole = self.inHole()
        collisions = pygame.sprite.groupcollide(self.playerGroup, self.backgroundGroup, False, False)
        if len(collisions) > 0:
            for player in collisions:
                for block in collisions[player]:
                    if (block.rect.left <= self.player.rect.left <= block.rect.right or block.rect.left <= self.player.rect.right <= block.rect.right) and (block.rect.top <= self.player.rect.top <= block.rect.bottom or block.rect.top <= self.player.rect.bottom <= block.rect.bottom) and not inHole:
                        if self.player.fallSpeed != 0:
                            self.player.rect.top += 10
                            self.isJumping = False
                            self.player.fallSpeed = 0
                        else:
                            self.isJumping = False
                    if block.rect.left <= self.player.rect.right <= block.rect.left + 10 and not self.isJumping:
                        self.player.rect.right = block.rect.left
                    elif block.rect.right - 10 <= self.player.rect.left <= block.rect.right and not self.isJumping:
                        self.player.rect.left = block.rect.right

    def bulletCollision(self):
        # handles collisions between bullets and sprites
        collisions = pygame.sprite.groupcollide(self.enemyGroup, self.bulletGroup, False, True)
        collisions2 = pygame.sprite.groupcollide(self.enemyGroup, self.otherBulletGroup, False, True)
        collisions3 = pygame.sprite.groupcollide(self.bulletGroup, self.backgroundGroup, True, False)
        collisions4 = pygame.sprite.groupcollide(self.otherBulletGroup, self.backgroundGroup, True, False)
        collisions5 = pygame.sprite.groupcollide(self.enemyBulletGroup, self.backgroundGroup, True, False)
        for enemy in collisions:
            self.enemyDead.append(enemy)
            self.score += 1
        for enemy in collisions2:
            self.enemyDead.append(enemy)

    def playerHit(self):
        # handles collisions between the enemies' bullets and the players
        hits = pygame.sprite.groupcollide(self.playerGroup, self.enemyBulletGroup, False, True)
        for hit in range(len(hits)):
            self.player.hitByBullet()
        hits2 = pygame.sprite.groupcollide(self.otherPlayerGroup, self.enemyBulletGroup, False, True)

    def offScreen(self):
        if self.player.rect.bottom >= self.groundLevel:
            self.player.health = 0


    # Weapons

    def deleteBullets(self):
        # deletes bullets when off screen
        for bullet in self.bulletGroup:
            if bullet.rect.bottom < 0:
                bullet.kill()
        for bullet in self.otherBulletGroup:
            if bullet.rect.bottom < 0:
                bullet.kill()

    def changeWeapon(self):
        # changes weapons when the player runs into one
        collisions = pygame.sprite.groupcollide(self.playerGroup, self.floatingWeaponGroup, False, True)
        if len(collisions) > 0:
            self.currentGun = self.newWeapon
            self.shotgunAmmo = 10
            self.machineGunAmmo = 100
            for player in collisions:
                for weapon in collisions[player]:
                    return weapon.rect.x

    def moveBullet(self):
        # moves all the bullets
        for bullet in self.bulletGroup:
            bullet.move()
        for bullet in self.otherBulletGroup:
            bullet.move()
        for bullet in self.enemyBulletGroup:
            bullet.move()


    # Enemies

    def moveEnemy(self):
        # moves the enemies towards the first player
        if len(self.otherPlayers) == 0 or self.otherDead:
            target = self.player.rect.centerx
        else:
            for player in self.otherPlayers:
                otherPlayersCenter = self.otherPlayers[player].rect.right + self.scrollX
                if otherPlayersCenter > self.player.rect.centerx + self.scrollX:
                    target = otherPlayersCenter - self.scrollX
                else:
                    target = self.player.rect.centerx
        for enemy in self.enemyGroup:
            self.enemyHitsHole(enemy)
            enemy.move(target)
            if enemy.rect.bottom > self.groundLevel - 80 and not enemy.timeAlive < 10:
                if target > enemy.rect.centerx:
                    enemy.rect.centerx -= 10
                elif target < enemy.rect.centerx:
                    enemy.rect.centerx += 10
                enemy.rect.bottom = self.groundLevel - 90
                enemy.toMove = False

    def enemyShoot(self):
        # makes a random enemy shoot at the first player
        index = random.randint(1, len(self.enemyGroup))
        count = 1
        for enemy in self.enemyGroup:
            if not enemy.rect.bottom > self.groundLevel - 70:
                if index == count:
                    if self.player.rect.left >= enemy.rect.right:
                        direction = 1
                        enemy.shoot(self.bulletR, self.enemyBulletGroup, enemy.rect.right, enemy.rect.centery, direction)
                        return (enemy.rect.right, enemy.rect.centery, 1)
                    else:
                        direction = -1
                        enemy.shoot(self.bulletL, self.enemyBulletGroup, enemy.rect.left, enemy.rect.centery, direction)
                        return (enemy.rect.left, enemy.rect.centery, -1)
            count += 1

    def createEnemy(self):
        # creates new enemies
        newEnemy = None
        if self.drawingHill and self.canSpawnEnemies:
            if self.decreasing:
                newEnemy = Enemy(self.enemyPics, self.lastHillX, self.hillBlocks[-1] - 30)
            else:
                newEnemy = Enemy(self.enemyPics, self.width - 10, self.hillBlocks[-1])
        elif self.drawingAirBlock:
            ground = random.choice([True, False])
            if not ground or self.drawingHole:
                newEnemy = Enemy(self.enemyPics, self.width - 10, self.airBlockHeight)
            else:
                newEnemy = Enemy(self.enemyPics, self.width - 10, self.groundLevel - 90)
        elif self.drawingHole:
            pass
        else:
            newEnemy = Enemy(self.enemyPics, self.width - 10, self.groundLevel - 90)
        if newEnemy != None:
            self.enemyGroup.add(newEnemy)
            return (newEnemy.rect.x, newEnemy.rect.bottom)

    def enemyDeadAnimation(self):
        # handles the explosion animation when an enemy is shot
        for enemy in self.enemyDead:
            if enemy.picCount < 4:
                if enemy.isFacing == "R":
                    enemy.changePic(self.tankExplodeR[enemy.picCount])
                else:
                    enemy.changePic(self.tankExplodeL[enemy.picCount])
                enemy.picCount += 1
            else:
                enemy.kill()

    def enemyIsOnBlock(self, enemy):
        # returns whether the enemy is standing on a block or not
        isOnBlock = False
        for block in self.backgroundGroup:
            if enemy.rect.bottom >= block.rect.top and not enemy.rect.top >= block.rect.top and block.rect.left + 10 < enemy.rect.right and enemy.rect.left < block.rect.right - 10:
                enemy.rect.bottom = block.rect.top
                enemy.fallSpeed = 0
                isOnBlock = True
        collisions = pygame.sprite.groupcollide(self.backgroundGroup, self.enemyGroup, False, False)
        if len(collisions) > 0:
            for block in collisions:
                for enemy in collisions[block]:
                    enemy.rect.bottom = block.rect.top
                    enemy.fallSpeed = 0
                    isOnBlock = True
        return isOnBlock

    def enemyHitsHole(self, enemy):
        # makes the enemy stops moving when he's about to fall into a hole
        collisions = pygame.sprite.groupcollide(self.enemyGroup, self.transparentGroup, False, False)
        for enemy in collisions:
            for block in collisions[enemy]:
                if enemy.isFacing == "R":
                    enemy.rect.right = block.rect.left
                    enemy.canGoR = False
                elif enemy.isFacing == "L":
                    enemy.rect.left = block.rect.right
                    enemy.canGoL = False

    def enemyFall(self):
        # handles the enemies falling
        for enemy in self.enemyGroup:
            enemy.timeAlive += 1
            if not self.enemyIsOnBlock(enemy):
                enemy.fall()
            if enemy.rect.top >= self.groundLevel:
                enemy.kill()

    def enemyActions(self, time):
        # creates new enemies and makes current enemies shoot
        # gets faster based on how far into the game the player is
        if self.timer % time == 0:
            if not self.scrollX == 0:
                self.newEnemyCoordinates = self.createEnemy()
                if self.newEnemyCoordinates != None:
                    self.drewEnemy = True
        if self.timer % (random.randint(time//2, 3*time//4)) == 0:
            if len(self.enemyGroup) > 0:
                self.bulletOrigin = self.enemyShoot()
                if not self.bulletOrigin == None:
                    self.enemyShot = True

    def timerFired(self, dt):
        self.timer += 1

        # Variables needed for messages
        if self.drawingHill:
            self.drawingAirBlock = False
        playerDied = False
        if self.playerDied == None and self.player.health <= 0:
            playerDied = True
            self.playerDied = True
        self.drewEnemy = False
        self.enemyShot = False
        drewNewFloatWeapon = False
        deleteWeapon = False
        newGame = False
        self.drewQuestionBlock = False
        if self.player.health <= 0:
            self.mode = "gameOver"
        deleteCoord = self.changeWeapon()
        if not deleteCoord == None:
            deleteWeapon = True

        floatingWeapon = self.hitQuestionMarkBlock()
        if not floatingWeapon == None:
            drewNewFloatWeapon = True

        # Who draws the next block
        if len(self.otherPlayers) == 0 or self.otherDead:
            self.playerDraws = True
        else:
            for player in self.otherPlayers:
                otherCoordinate = self.otherPlayers[player].rect.right + self.scrollX
                if self.player.rect.right + self.scrollX > otherCoordinate and (self.lastBlock == None or not self.lastBlock >= self.width):
                    self.playerDraws = True
                elif self.player.rect.right + self.scrollX == otherCoordinate and self.player.PID == "Player1" and (self.lastBlock == None or not self.lastBlock >= self.width):
                    self.playerDraws = True
                else:
                    self.playerDraws = False

        # Initial player position
        x0 = self.player.rect.centerx
        y0 = self.player.rect.bottom

        # Background
        if not self.madeBackground:
            self.createGround()
        self.deleteGround()
        self.backgroundPic()

        # Player Movement
        if self.timer % 3 == 0:
            self.changePic()
        self.scrollRight()
        self.scrollLeft()
        self.moveRight()
        self.moveLeft()
        self.playerHit()
        self.fall()
        self.jump()
        self.offScreen()
        self.collisions()

        # Bullets
        self.bulletCollision()
        self.moveBullet()
        self.deleteBullets()

        # Enemies
        self.moveEnemy()
        self.enemyFall()
        self.enemyDeadAnimation()

        # Continuous Machine Gun Shooting
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.currentGun == self.machineGun and self.timer % 5 == 0:
            self.machineGunAmmo -= 1
            self.shotBullet = True
            if self.isFacing == "R":
                self.player.shoot(self.bulletR, self.bulletGroup, self.player.rect.right + 7, self.player.rect.centery - 20, 1)
            if self.isFacing == "L":
                self.player.shoot(self.bulletL, self.bulletGroup, self.player.rect.left - 7, self.player.rect.centery - 20, -1)
        if self.shotgunAmmo <= 0 or self.machineGunAmmo <= 0:
            self.currentGun = self.handgun

        # Calculates change in player position
        x1 = self.player.rect.centerx
        y1 = self.player.rect.bottom
        dx = x1 - x0
        dy = y1 - y0

        # Handles Random Ground/Increasingly Difficult Enemies
        if self.playerDraws:
            if self.otherDrawingHill:
                self.drawingHill = True
                self.otherDrawingHill = False
            elif self.otherDrawingAirBlock:
                self.drawingAirBlock = True
                self.otherDrawingAirBlock = False
            if self.hillCount == 0 and not self.drawingHill and not self.drawingHole and not self.drawingAirBlock:
                self.randomHill()
            if not self.drawingHole and not self.drawingHill:
                self.randomHole()
            if not self.drawingHill and not self.drawingAirBlock:
                self.randomAirBlock()

            if self.hillCount == 0:
                self.difficulty = "25%"
                self.enemyActions(300)
            elif self.hillCount == 1:
                self.difficulty = "50%"
                self.enemyActions(120)
            elif self.hillCount == 2:
                self.difficulty = "75%"
                self.enemyActions(60)
            elif self.hillCount == 3:
                self.difficulty = "100%"
                self.enemyActions(30)
            else:
                self.difficulty = "125%"
                self.enemyActions(30)

        # Handles the messages between players
        msg = ""
        if (self.isScrollingRight and self.isMovingRight) or dx > 0 or dy != 0:
            msg = "playerMoved %d %d R%d %d\n" % (self.player.rect.x + self.scrollX, self.player.rect.bottom, self.spriteIndex, self.hillCount)
        elif (self.isScrollingLeft and self.isMovingLeft) or dx < 0 or dy != 0:
            msg = "playerMoved %d %d L%d %d\n" % (self.player.rect.x + self.scrollX, self.player.rect.bottom, self.spriteIndex, self.hillCount)
        elif dy != 0:
            msg = "playerMoved %d %d %s %d\n" % (self.player.rect.x + self.scrollX, self.player.rect.bottom, "None", self.hillCount)
        if self.playerDraws and self.isScrollingRight and self.scrollX % 30 == 0 and (self.lastBlock == None or not self.lastBlock > self.width) and msg != "":
            if self.drawingAirBlock and not self.drawingHole:
                msg = msg[:-1] + " drawingAirBlock %d %d %d %d drawingGround %d %d\n" % (self.width + self.scrollX, self.airBlockHeight, self.blockLengthCount, self.blockLength, self.width + self.scrollX, self.groundLevel - 90)
            if self.drawingAirBlock and self.drewQuestionBlock and not self.drawingHole:
                msg = msg[:-1] + " drawingQuestionBlock %d %d drawingGround %d %d\n" % (self.width + self.scrollX, self.airBlockHeight, self.width + self.scrollX, self.groundLevel - 90)
            if self.drawingAirBlock and self.drawingHole:
                msg = msg[:-1] + " drawingAirBlock %d %d %d %d\n" % (self.width + self.scrollX, self.airBlockHeight, self.blockLengthCount, self.blockLength)
            if self.drawingAirBlock and self.drewQuestionBlock and self.drawingHole:
                msg = msg[:-1] + " drawingQuestionBlock %d %d\n" % (self.width + self.scrollX, self.airBlockHeight)
            elif self.drawingHill and not self.noHill:
                msg = msg[:-1] + " drawingHill %d %d %d %d %s\n" % (self.width + self.scrollX, self.hillBlocks[-1], self.hillHeight, self.decreasing, len(self.hillBlocks) == 1)
            elif self.drawingHill and self.noHill:
                msg = msg[:-1] + " drawingTransparent %d %d\n" % (self.width + self.scrollX, self.hillBlocks[-1])
            elif self.drawingHole:
                pass
            else:
                msg = msg[:-1] + " drawingGround %d %d\n" % (self.width + self.scrollX, self.groundLevel - 90)
            if self.drawingHole and not self.drawingAirBlock:
                msg = msg[:-1] + " drawingAirBarrier %d\n" % (self.width + self.scrollX)
            if self.drawingHole and self.drawingAirBlock:
                msg = msg[:-1] + " drawingTransparent %d %d\n" % (self.width + self.scrollX, self.groundLevel - 90)
        if self.drewEnemy:
            msg = msg[:-1] + " createdEnemy %d %d\n" % (self.newEnemyCoordinates[0] + self.scrollX, self.newEnemyCoordinates[1])
        if self.shotBullet:
            if self.currentGun == self.shotgun:
                if self.isFacing == "R":
                    msg = msg[:-1] + " shotgunBullet %d %d %d\n" % (self.player.rect.right + self.scrollX + 7, self.player.rect.centery - 20, 1)
                elif self.isFacing == "L":
                    msg = msg[:-1] + " shotgunBullet %d %d %d\n" % (self.player.rect.left - 7 + self.scrollX, self.player.rect.centery - 20, -1)
            else:
                if self.isFacing == "R":
                    msg = msg[:-1] + " shotBullet %d %d %d\n" % (self.player.rect.right + self.scrollX + 7, self.player.rect.centery - 20, 1)
                elif self.isFacing == "L":
                    msg = msg[:-1] + " shotBullet %d %d %d\n" % (self.player.rect.left - 7 + self.scrollX, self.player.rect.centery - 20, -1)
            self.shotBullet = False
        if self.enemyShot:
            msg = msg[:-1] + " enemyShot %d %d %d\n" % (self.bulletOrigin[0] + self.scrollX, self.bulletOrigin[1], self.bulletOrigin[2])
        if drewNewFloatWeapon:
            msg = msg[:-1] + " newFloat %s %d %d\n" % (floatingWeapon[0], floatingWeapon[1] + self.scrollX, floatingWeapon[2])
        if deleteWeapon:
            msg = msg[:-1] + " deleteWeapon %d\n" % (deleteCoord + self.scrollX)
        if playerDied:
            msg = msg[:-1] + " playerDied %d\n" % (self.scrollX)
        if self.newGame:
            msg = msg[:-1] + " newGame %d\n" % (self.scrollX)

        # Start a new game if both players pressed 'r'
        if self.newGame and self.otherNewGame:
            self.startNewGame()

        if msg != "":
            # print ("sending: ", msg,)
            self.server.send(msg.encode())
        while self.serverMsg.qsize() > 0:
            msg = self.serverMsg.get(False)
            try:
                msg = msg.split()
                command = msg[0]

                if "playerDied" in msg:
                    print('yeet')
                    self.otherDead = True
                    self.otherPlayerGroup.empty()
                    self.otherPlayers = dict()

                if self.otherDead:
                    if "newGame" in msg:
                        self.otherNewGame = True

                else:
                    if "createdEnemy" in msg:
                        index = msg.index("createdEnemy")
                        x = int(msg[index + 1]) - self.scrollX
                        y = int(msg[index + 2])
                        self.enemyGroup.add(Enemy(self.enemyPics, x, y))

                    if "shotBullet" in msg:
                        index = msg.index("shotBullet")
                        x = int(msg[index + 1]) - self.scrollX
                        y = int(msg[index + 2])
                        direction = int(msg[index + 3])
                        if direction == 1:
                            self.otherBulletGroup.add(Bullet(self.bulletR, x, y, 1))
                        elif direction == -1:
                            self.otherBulletGroup.add(Bullet(self.bulletL, x, y, -1))

                    if "shotgunBullet" in msg:
                        index = msg.index("shotgunBullet")
                        x = int(msg[index + 1]) - self.scrollX
                        y = int(msg[index + 2])
                        direction = int(msg[index + 3])
                        if direction == 1:
                            self.otherBulletGroup.add(Bullet(self.bulletDownR, x, y, 1, 15))
                            self.otherBulletGroup.add(Bullet(self.bulletR, x, y, 1, 0))
                            self.otherBulletGroup.add(Bullet(self.bulletUpR, x, y, 1, 15))
                        elif direction == -1:
                            self.otherBulletGroup.add(Bullet(self.bulletUpL, x, y, -1, 15))
                            self.otherBulletGroup.add(Bullet(self.bulletL, x, y, -1, 0))
                            self.otherBulletGroup.add(Bullet(self.bulletDownL, x, y, -1, -15))

                    if "enemyShot" in msg:
                        index = msg.index("enemyShot")
                        x = int(msg[index + 1]) - self.scrollX
                        y = int(msg[index + 2])
                        direction = int(msg[index + 3])
                        if direction == 1:
                            self.enemyBulletGroup.add(Bullet(self.bulletR, x, y, 1))
                        elif direction == -1:
                            self.enemyBulletGroup.add(Bullet(self.bulletL, x, y, -1))

                    if "newFloat" in msg:
                        index = msg.index("newFloat")
                        weapon = msg[index + 1]
                        if weapon == "machineGun":
                            self.newWeapon = self.machineGun
                        elif weapon == "shotgun":
                            self.newWeapon = self.shotgun
                        x = int(msg[index + 2]) - self.scrollX
                        y = int(msg[index + 3])
                        self.floatingWeaponGroup.add(FloatingWeapon(self.newWeapon, x, y))

                    if "deleteWeapon" in msg:
                        index = msg.index("deleteWeapon")
                        x = int(msg[index + 1]) - self.scrollX
                        for weapon in self.floatingWeaponGroup:
                            if x - 50 < weapon.rect.x < x + 50:
                                weapon.kill()

                    if len(msg) > 5:
                        if "drawingHill" in msg:
                            index = msg.index("drawingHill")
                            x = int(msg[index+1]) - self.scrollX
                            y = int(msg[index+2])
                            self.hillHeight = int(msg[index+3])
                            decreasing = int(msg[index+4])
                            empty = msg[index+5]
                            if decreasing == 1:
                                self.decreasing = True
                            else:
                                self.decreasing = False
                            self.otherDrawingHill = True
                            if empty == "True":
                                self.hillBlocks = [self.groundLevel - 120]
                            else:
                                self.hillBlocks.append(y)
                            self.drawBlock(self.grass1, x, y)
                            self.lastBlock = x

                        elif "drawingAirBlock" in msg:
                            index = msg.index("drawingAirBlock")
                            x = int(msg[index+1]) - self.scrollX
                            y = int(msg[index+2])
                            self.blockLengthCount = int(msg[index+3])
                            self.blockLength = int(msg[index+4])
                            self.otherDrawingAirBlock = True
                            self.airBlockHeight = y
                            self.drawAirBlock(x, y)
                            self.lastBlock = x

                        if "drawingTransparent" in msg:
                            index = msg.index("drawingTransparent")
                            x = int(msg[index+1]) - self.scrollX
                            y = int(msg[index+2])
                            self.drawTransparent(x, y)
                            self.drawBlackBlock(x, y+60)
                            self.lastBlock = x

                        if "drawingAirBarrier" in msg:
                            index = msg.index("drawingAirBarrier")
                            x = int(msg[index+1]) - self.scrollX
                            self.drawAirBarrier(x)
                            self.drawBlackBlock(x, self.groundLevel-60)
                            self.lastBlock = x

                        if "drawingQuestionBlock" in msg:
                            index = msg.index("drawingQuestionBlock")
                            x = int(msg[index+1]) - self.scrollX
                            y = int(msg[index+2])
                            self.drawQuestionBlock(x, y)
                            self.lastBlock = x

                        if "drawingGround" in msg:
                            index = msg.index("drawingGround")
                            x = int(msg[index + 1]) - self.scrollX
                            y = int(msg[index + 2])
                            self.drawBlock(self.grass1, x, y)
                            self.lastBlock = x

                    if command == "myIDis":
                        myPID = msg[1]
                        self.player.changePID(myPID)

                    if command == "newPlayer":
                        newPID = msg[1]
                        x = self.width // 4
                        y = self.groundLevel - 90
                        self.otherPlayers[newPID] = Player(newPID, self.walkRight[0], x, y)
                        self.otherPlayerGroup.add(self.otherPlayers[newPID])
                        self.twoPlayer = True

                    if command == "playerMoved":
                        PID = msg[1]
                        dx = int(msg[2])
                        y = int(msg[3])
                        self.hillCount = int(msg[5])
                        direction = None
                        if msg[4] != "None":
                            direction = msg[4][0]
                            index = int(msg[4][1:])
                        self.otherPlayers[PID].rect.x = dx - self.scrollX
                        if direction == "R":
                            self.otherPlayers[PID].changePic(self.walkRight[index])
                        elif direction == "L":
                            self.otherPlayers[PID].changePic(self.walkLeft[index])
                        self.otherPlayers[PID].rect.bottom = y

            except:
                print("failed")
            self.serverMsg.task_done()

    def redrawAll(self, screen):
        if self.mode == "gameMode":
            self.backgroundSkyGroup.draw(screen)
            self.mountainsGroup.draw(screen)
            self.blackBlockGroup.draw(screen)
            self.playerGroup.draw(screen)
            self.backgroundGroup.draw(screen)
            self.enemyGroup.draw(screen)
            self.enemyBulletGroup.draw(screen)
            self.otherPlayerGroup.draw(screen)
            self.bulletGroup.draw(screen)
            self.otherBulletGroup.draw(screen)
            self.floatingWeaponGroup.draw(screen)

            # Draws health bar
            pygame.draw.rect(screen, (0, 0, 0), (self.player.rect.left - 10, self.player.rect.top - 15, self.player.rect.width + 20, 6))
            pygame.draw.rect(screen, (0, 255, 0), ((self.player.rect.left - 8, self.player.rect.top - 14, (self.player.rect.width + 16) * self.player.health / 100, 4)))

            # Draws the instructions at the start screen
            if self.scrollX <= self.width:
                instructions1 = self.font.render("1. Press Space to shoot", True, (0, 0, 0))
                instructions2 = self.font.render("2. Press Up arrow to jump", True, (0, 0, 0))
                instructions3 = self.font.render("3. The enemies spawn and shoot faster and faster", True, (0, 0, 0))
                instructions4 = self.font.render("4. The holes in the hills get bigger and bigger and the holes", True, (0, 0, 0))
                instructions4i = self.font.render("in the ground get more frequent", True, (0, 0, 0))
                instructions5 = self.font.render("5. You get points for killing enemies", True, (0, 0, 0))
                instructions6 = self.font.render("6. Try to survive as long as possible!", True, (0, 0, 0))
                screen.blit(instructions1, (20-self.scrollX, 20))
                screen.blit(instructions2, (20-self.scrollX, 40))
                screen.blit(instructions3, (20-self.scrollX, 60))
                screen.blit(instructions4, (20-self.scrollX, 80))
                screen.blit(instructions4i, (20-self.scrollX, 100))
                screen.blit(instructions5, (20-self.scrollX, 120))
                screen.blit(instructions6, (20-self.scrollX, 140))
            # Draws the HUD
            else:
                score = self.font.render("Killed: " + "%d " %(self.score), True, (0, 0, 0))
                screen.blit(score, (self.width - 200, 45))
                speed = self.font.render("Difficulty = %s" % self.difficulty, True, (0, 0, 0))
                screen.blit(speed, (self.width - 200, 20))
                if self.currentGun == self.shotgun:
                    screen.blit(self.shotgunSymbol, (20, 20))
                    ammo = self.font.render("%s" % self.shotgunAmmo, True, (255, 0, 0))
                    screen.blit(ammo, (100, 25))
                elif self.currentGun == self.machineGun:
                    screen.blit(self.machineGunSymbol, (20, 20))
                    ammo = self.font.render("%s" % self.machineGunAmmo, True, (255, 0, 0))
                    screen.blit(ammo, (140, 25))
                else:
                    screen.blit(self.handgunSymbol, (20, 20))
                    ammo = self.font.render("Infinite", True, (255, 0, 0))
                    screen.blit(ammo, (100, 25))
        # Draws the game over screen
        elif self.mode == "gameOver":
            bgColor = (255, 0, 0)
            screen.fill(bgColor)
            gameOver = self.font.render("Game Over!", True, (0, 0, 0))
            gameOverSize = gameOver.get_width()
            screen.blit(gameOver, (self.width//2 - gameOverSize//2, self.height//2-50))
            score = self.font.render("You Killed " + "%d " %(self.score) + "Enemies!", True, (0, 0, 0))
            scoreSize = score.get_width()
            screen.blit(score, (self.width // 2 - scoreSize // 2, self.height //2))
            if len(self.otherPlayerGroup) == 0 or self.otherDead:
                restart = self.font.render(self.text, True, (0, 0, 0))
                restartSize = restart.get_width()
                screen.blit(restart, (self.width // 2 - restartSize // 2, self.height / 2 + 25))
            else:
                wait = self.font.render("Wait for your teammate to finish!", True, (0, 0, 0))
                waitSize = wait.get_width()
                screen.blit(wait, (self.width // 2 - waitSize // 2, self.height / 2 + 50))

    def run(self, serverMsg=None, server=None):
        # from 112 pygame mini lecture
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        self.init()
        self.server = server
        self.serverMsg = serverMsg
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    playing = False
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()


#serverMsg = Queue(100)
#threading.Thread(target=handleServerMsg, args=(server, serverMsg)).start()

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def startGame(HOST, PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, PORT))
    serverMsg = Queue(100)
    threading.Thread(target=handleServerMsg, args=(server, serverMsg)).start()
    print("connected to server")
    game = PygameGame()
    game.run(serverMsg, server)
    return (server, serverMsg)


def multiplayerSetup():
    PORT = int(input("Input PORT as it appeared in the server output: "))
    HOST = input("Input HOST as it appeared in the server.py output: ")
    try:
        startGame(HOST, PORT)
    except:
        print("You may have inputted something wrong, please try again")
        multiplayerSetup()

def main():
    multiplayer = input("Are you playing on two different computers? [y/n]: ")
    while multiplayer.strip() != "y" and multiplayer.strip() != "n":
        multiplayer = input("Please type either 'y' or 'n'")
    if multiplayer == "y":
        multiplayerSetup()
    else:
        PORT = int(input("Input PORT as it appeared in server output: "))
        HOST = ""
        startGame(HOST, PORT)

main()
