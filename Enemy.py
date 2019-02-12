import pygame
from Weapons import Bullet


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pic, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.pic = pic
        self.image = pic[0]
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.bottom = y
        self.speed = 1
        self.gravity = 3
        self.fallSpeed = 0
        self.toMove = True
        self.picCount = 0
        self.isFacing = "L"
        self.timeAlive = 0
        self.canGoR = True
        self.canGoL = True

    def move(self, x):
        # the enemy moves towards the target it is given
        if self.toMove:
            if x > self.rect.right and self.canGoR:
                self.rect.centerx += self.speed
                self.image = self.pic[1]
                self.isFacing = "R"
            elif x < self.rect.left and self.canGoL:
                self.rect.centerx -= self.speed
                self.image = self.pic[0]
                self.isFacing = "L"
            else:
                pass

    def shoot(self, pic, group, x, y, direction):
        # shoots a bullet
        group.add(Bullet(pic, x, y, direction))

    def kill(self):
        pygame.sprite.Sprite.kill(self)

    def fall(self):
        self.rect.y += self.fallSpeed
        self.fallSpeed += self.gravity

    def changePic(self, pic):
        # changes picture for the explosion animation
        self.image = pic
