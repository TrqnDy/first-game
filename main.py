import pygame
import sys
from os.path import join
from os import walk

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
            choice

    elif choice == "Survivor":
        game = SurvivorGame()
        result = game.run()

    elif choice == "Block Blast":
        pass
    
    elif choice == "quit":
        pygame.quit()
        sys.exit()