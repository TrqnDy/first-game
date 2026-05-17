from os import walk

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

        self.setup()

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

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.display_surface.fill((0, 0, 0))
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.player.rect.center)

            pygame.display.update()

        pygame.quit()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        self.player = player
        self.distance = 140
        self.player_direction = self.player.direction

        super().__init__(groups)
        self.gun_surf = pygame.image.load("gun.png").convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player.direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.mouse.get_pos()
        player_pos = self.player.rect.center
        self.player_direction = (mouse_pos - player_pos).normalize_ip()

    def rotate(self):
        angle = self.player_direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.gun_surf, -angle)
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player.direction * self.distance)

if __name__ == '__main__':
    game = SurvivorGame()
    game.run()