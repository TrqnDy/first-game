import pygame, sys
from buttom_and_font import Button

pygame.init()

pygame.display.set_caption("Menu")

BG = pygame.image.load("Background.png")

def get_font(size):
    return pygame.font.Font("font.ttf", size)


def main_menu():
    SCREEN = pygame.display.set_mode((1280, 720))
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")

        PLAY_BUTTON = Button(
            image=pygame.transform.scale(
                pygame.image.load("Options Rect.png"), (500, 100)
            ),
            pos=(640, 250),
            text_input="Chess",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="White"
        )

        OPTIONS_BUTTON = Button(
            image=pygame.transform.scale(
                pygame.image.load("Options Rect.png"), (700, 100)
            ),
            pos=(640, 400),
            text_input="Survivor",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="White"
        )

        BLOCK_BLAST_BUTTON = Button(
            image=pygame.transform.scale(
                pygame.image.load("Quit Rect.png"), (900, 100)
            ),
            pos=(640, 550),
            text_input="Block Blast",
            font=get_font(75),
            base_color="#d7fcd4",
            hovering_color="White"
        )

        SCREEN.blit(MENU_TEXT, MENU_TEXT.get_rect(center=(640, 100)))

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, BLOCK_BLAST_BUTTON]:

            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:

                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    return "Chess"

                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    return "Survivor"

                if BLOCK_BLAST_BUTTON.checkForInput(MENU_MOUSE_POS):
                    return "Block_Blast"

        pygame.display.update()