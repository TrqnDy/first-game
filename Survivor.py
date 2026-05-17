from os import walk
from math import atan2, degrees
import pygame
from player import Player
from pytmx.util_pygame import load_pygame

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def draw(self, target_pos):
        self.offset.x = -target_pos[0] + self.display_surface.get_width() / 2
        self.offset.y = -target_pos[1] + self.display_surface.get_height() / 2

        for sprite in self:
            if hasattr(sprite, 'ground'):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        for sprite in sorted([s for s in self if not hasattr(s, 'ground')], key=lambda s: s.rect.bottom):
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)


class SurvivorGame:
    def __init__(self):
        self.WIN_WIDTH = 1280
        self.WIN_HEIGHT = 700
        self.TILE_SIZE = 64

        pygame.init()
        self.display_surface = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        pygame.display.set_caption("Survivor")
        self.clock = pygame.time.Clock()
        self.running = True

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        self.setup()

        self.load_images()
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100

    def load_images(self):
        self.bullet_surf = pygame.image.load("bullet.png").convert_alpha()

    def input(self):
        if  pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        tmx_map = load_pygame('world.tmx')

        for x, y, image in tmx_map.get_layer_by_name('Ground').tiles():
            Sprite((x * self.TILE_SIZE, y * self.TILE_SIZE), image, self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.input()
            self.display_surface.fill((0, 0, 0))
            self.all_sprites.update(dt)
            self.gun_timer()
            self.all_sprites.draw(self.player.rect.center)

            pygame.display.update()

        pygame.quit()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        self.player = player
        self.distance = 140
        self.WIN_WIDTH = 1280
        self.WIN_HEIGHT = 700
        self.player_direction = pygame.math.Vector2(0, 1)

        super().__init__(groups)
        self.gun_surf = pygame.image.load("gun.png").convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player.direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.math.Vector2(self.WIN_WIDTH / 2, self.WIN_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, __):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = 1200
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

if __name__ == '__main__':
    game = SurvivorGame()
    game.run()