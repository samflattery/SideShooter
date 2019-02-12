import pygame
from Weapons import Bullet


class Player(pygame.sprite.Sprite):
    def __init__(self, PID, pic, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pic
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedX = 5
        self.speedY = -30
        self.gravity = 3
        self.fallSpeed = 0
        self.health = 100
        self.PID = PID

    def changePID(self, PID):
        self.PID = PID

    def moveRight(self):
        self.rect.x += self.speedX

    def moveLeft(self):
        self.rect.x -= self.speedX

    def jump(self):
        self.rect.y += self.speedY

    def fall(self):
        self.rect.y += self.fallSpeed
        self.fallSpeed += self.gravity

    def hitByBullet(self):
        self.health -= 5

    def changePic(self, pic):
        # Changes the players picture for the animation
        self.image = pic

    def shoot(self, pic, group, x, y, direction, angle=0):
        # Adds a bullet to the bullet group
        group.add(Bullet(pic, x, y, direction, angle))
