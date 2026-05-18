from os import walk
from math import atan2, degrees
import pygame
from buttom_and_font import Button
from player import Player
from pytmx.util_pygame import load_pygame
from random import choice

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

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100
        self.score = 0

        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_position = []

        self.load_images()
        self.setup()

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
            else:
                self.spawn_position.append((obj.x, obj.y))

    def run(self):
        while True:
            dt = self.clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == self.enemy_event:

                    enemy_class = choice([Bat, Blob, Skeleton])

                    enemy_class(
                        choice(self.spawn_position),
                        (self.all_sprites, self.enemy_sprites),
                        self.player,
                        self.collision_sprites,
                        self.bullet_sprites
                    )

            self.input()
            self.display_surface.fill((0, 0, 0))
            self.all_sprites.update(dt)
            self.gun_timer()
            self.all_sprites.draw(self.player.rect.center)
            option_menu = Option_menu(self.display_surface, self.player.score)
            option_menu.draw()

            if option_menu.check_click():
                return "menu"

            pygame.display.update()

        #pygame.quit()

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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, bullet_sprites):
        super().__init__(groups)
        self.player = player
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.bullet_sprites = bullet_sprites
        self.direction = pygame.math.Vector2()

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt):
        self.animate(dt)
        direction = (
            pygame.math.Vector2(self.player.rect.center) -
            pygame.math.Vector2(self.hitbox_rect.center)
        )

        if direction.length() != 0:
            self.direction = direction.normalize()

        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision_walls("horizontal")

        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision_walls("vertical")

        self.rect.center = self.hitbox_rect.center

        if self.bullet_collision():
            self.player.score += self.point_after_death
            self.kill()

    def collision_walls(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                    self.rect.centerx = self.hitbox_rect.centerx
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    self.rect.centery = self.hitbox_rect.centery

    def bullet_collision(self):
        for bullet in self.bullet_sprites:
            if self.hitbox_rect.colliderect(bullet.rect):
                bullet.kill()
                return True
        return False

class Bat(Enemy):
    def __init__(self, pos, groups, player, collision_sprites, bullet_sprites):

        frames = [
            pygame.image.load(f"bat_{i}.png").convert_alpha()
            for i in range(4)
        ]

        super().__init__(
            pos,
            frames,
            groups,
            player,
            collision_sprites,
            bullet_sprites
        )

        self.speed = 350
        self.point_after_death = 30

class Blob(Enemy):
    def __init__(self, pos, groups, player, collision_sprites, bullet_sprites):
        frames = [
            pygame.image.load(f"blob_{i}.png").convert_alpha()
            for i in range(4)
        ]

        super().__init__(
            pos,
            frames,
            groups,
            player,
            collision_sprites,
            bullet_sprites
        )
        self.speed = 100
        self.point_after_death = 10

class Skeleton(Enemy):
    def __init__(self, pos, groups, player, collision_sprites, bullet_sprites):
        self.skeleton_frames = [
            pygame.image.load(f"skeleton_{i}.png").convert_alpha()
            for i in range(4)
        ]

        super().__init__(
            pos,
            self.skeleton_frames,
            groups,
            player,
            collision_sprites,
            bullet_sprites
        )
        self.speed = 150
        self.point_after_death = 20

class Option_menu:
    def __init__(self, display_surface, score):
        self.display_surface = display_surface
        self.score = score

        self.font_score = pygame.font.Font(None, 70)
        self.font_back = pygame.font.Font(None, 40)

        self.back_button = Button(
            None,
            (1130, 20),
            "Back to main menu",
            self.font_back,
            "white",
            "red"
        )

    def draw(self):
        # Score
        score_surf = self.font_score.render(
            f"Score: {self.score}",
            True,
            "white"
        )

        self.display_surface.blit(score_surf, (20, 20))

        # Back button
        self.back_button.changeColor(pygame.mouse.get_pos())
        self.back_button.update(self.display_surface)

    def check_click(self):
        if pygame.mouse.get_pressed()[0]:
            if self.back_button.checkForInput(pygame.mouse.get_pos()):
                return True

        return False

if __name__ == '__main__':
    game = SurvivorGame()
    game.run()