import pygame
import sys

from Survivor import SurvivorGame
from main_menu_game import main_menu
from chess_game import ChessGame

pygame.init()

while True:

    choice = main_menu()

    if choice == "Chess":

        game = ChessGame()
        result = game.run()

        if result == "menu":
            continue

    elif choice == "Survivor":

        game = SurvivorGame()
        result = game.run()

        if result == "menu":
            continue

    elif choice == "Survivor":

        game = SurvivorGame()
        result = game.run()

        if result == "menu":
            continue

    elif choice == "Block Blast":
        pass

    elif choice == "quit":
        pygame.quit()
        sys.exit()