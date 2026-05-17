import pygame

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, group, collision_sprites):

        super().__init__(group)

        self.animations = {
            "left": [],
            "right": [],
            "up": [],
            "down": []
        }

        for i in range(4):
            self.animations["left"].append(
                pygame.image.load(f"left_{i}.png").convert_alpha()
            )

        for i in range(4):
            self.animations["right"].append(
                pygame.image.load(f"right_{i}.png").convert_alpha()
            )

        for i in range(4):
            self.animations["up"].append(
                pygame.image.load(f"up_{i}.png").convert_alpha()
            )

        for i in range(4):
            self.animations["down"].append(
                pygame.image.load(f"down_{i}.png").convert_alpha()
            )

        self.stand = True
        self.state = "down"
        self.frame = 0

        if not self.stand:
            self.image = self.animations[self.state][0]
        else:
            self.image = pygame.image.load(f"{self.state}_0.png").convert_alpha()

        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.math.Vector2()

        self.speed = 500

        self.collision_sprites = collision_sprites

        self.hitbox = self.rect.inflate(-60, -60)

    def input(self):

        keys = pygame.key.get_pressed()

        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
            self.state = "up"
            self.stand = False

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.state = "down"
            self.stand = False
            
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.state = "left"
            self.stand = False

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.state = "right"
            self.stand = False

        self.stand = self.direction.x == 0 and self.direction.y == 0
        self.direction = self.direction.normalize() if self.direction else self.direction

    def animate(self):
        if self.stand:
            self.image = self.animations[self.state][0]
        else:
            self.frame += 0.15
            if self.frame >= len(self.animations[self.state]):
                self.frame = 0
            self.image = self.animations[self.state][int(self.frame)]

    def move(self, dt):

        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        self.hitbox.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def collision(self, direction):

        for sprite in self.collision_sprites:

            if sprite.rect.colliderect(self.hitbox):

                if direction == 'horizontal':

                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left

                    if self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right

                if direction == 'vertical':

                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top

                    if self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom

    def update(self, dt):

        self.input()

        self.move(dt)

        self.animate()