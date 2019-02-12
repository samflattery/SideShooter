import pygame
import math


class FloatingWeapon(pygame.sprite.Sprite):
    # the class that generates the floating weapons that the player can collect
    def __init__(self, pic, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pic
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def kill(self):
        pygame.sprite.Sprite.kill(self)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pic, x, y, direction=1, angle=0):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.transform.scale(pic, (15, 5))
        self.image = pic
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedX = 15
        self.direction = direction
        self.angle = angle
        self.speedY = 15

    def move(self):
        # moves the bullet in the direction of the angle
        self.rect.centerx += self.speedX * math.cos(math.radians(self.angle)) * self.direction
        self.rect.centery += self.speedY * math.sin(math.radians(self.angle)) * self.direction
