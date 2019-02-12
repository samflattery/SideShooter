import pygame


class BackgroundBlock(pygame.sprite.Sprite):
    # The class that generates the background blocks
    def __init__(self, pic, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pic, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def kill(self):
        pygame.sprite.Sprite.kill(self)


class QuestionBlock(pygame.sprite.Sprite):
    # the class that's used to detect collisions between the player and the question blocks
    def __init__(self, pic, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pic, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Background(pygame.sprite.Sprite):
    # the class that generates the image in the background
    def __init__(self, pic, height, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pic
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.bottom = height - 90
