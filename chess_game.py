import pygame
import copy

pygame.init() 
SIZE = 600 
SQUARE = SIZE // 8
def next_move(turn_move):
    if turn_move == "white":
        return "black"
    else:
        return "white"

def is_in_check(board, color):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if isinstance(p, King) and p.color == color:
                return is_square_attacked(board, r, c, color)
    return False

def is_square_attacked(board, row, col, color):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p.color != color:

                # DÙNG can_attack nếu có
                if hasattr(p, "can_attack"):
                    if p.can_attack(c, r, board, col, row):
                        return True

                # fallback cho các quân còn lại
                else:
                    if p.can_move(c, r, board, col, row):
                        return True

    return False

def is_valid_move(board, sr, sc, tr, tc, color):
    piece = board[sr][sc]
    captured = board[tr][tc]

    # simulate
    board[tr][tc] = piece
    board[sr][sc] = None

    # tìm vua
    king_pos = None
    for r in range(8):
        for c in range(8):
            if isinstance(board[r][c], King) and board[r][c].color == color:
                king_pos = (r, c)

    in_check = is_square_attacked(board, king_pos[0], king_pos[1], color)

    # undo
    board[sr][sc] = piece
    board[tr][tc] = captured

    return not in_check

def simulate_move(board, sr, sc, tr, tc):
    new_board = copy.deepcopy(board)
    new_board[tr][tc] = new_board[sr][sc]
    new_board[sr][sc] = None
    return new_board

class Piece:
    def __init__(self, color, image):
        self.color = color
        self.image = image

    def move(self, start, end, board):
        if end[0] != start[0] or end[1] != start[1]:
            board[end[0]][end[1]] = self
            board[start[0]][start[1]] = None

class Pawn(Piece):
    def __init__(self, color, image):
        super().__init__(color, image)
        self.first_move = True

    def promote(self, row): 
        if self.color == "white" and row == 0: 
            print("q = queen; r = rook; b = bishop; k = knight") 
            choice = input("").lower() 
            if choice == "q": 
                return Queen("white", white_queen_img) 
            elif choice == "r": 
                return Rook("white", white_rook_img) 
            elif choice == "b": 
                return Bishop("white", white_bishop_img) 
            elif choice == "n": 
                return Knight("white", white_knight_img) 
        if self.color == "black" and row == 7: 
            print("q = queen; r = rook; b = bishop; k = knight") 
            choice = input("").lower() 
            if choice == "q": 
                return Queen("black", black_queen_img) 
            elif choice == "r": 
                return Rook("black", black_rook_img) 
            elif choice == "b": 
                return Bishop("black", black_bishop_img) 
            elif choice == "n": 
                return Knight("black", black_knight_img) 
        return self
    
    def can_move(self, col, row, board, next_move_col, next_move_row):
        target = board[next_move_row][next_move_col]
        if target == None:
            if self.first_move:
                if next_move_col == col and abs(next_move_row - row) == 1:
                    self.first_move = False
                    return True
                elif next_move_col == col and abs(next_move_row - row) == 2:
                    if self.color == "white" and row == 6 and board[row-1][col] == None:
                        self.first_move = False
                        return True
                    elif self.color == "black" and row == 1 and board[row+1][col] == None:
                        self.first_move = False
                        return True
            else:
                if next_move_col == col and abs(next_move_row - row) == 1:
                    return True
                
        else:
            if target.color != self.color:
                if self.color == "white":
                    if next_move_row == row - 1 and abs(next_move_col - col) == 1:
                        return True
                else:
                    if next_move_row == row + 1 and abs(next_move_col - col) == 1:
                        return True
        return False
    
    def can_attack(self, col, row, board, nc, nr):
        if self.color == "white":
            return nr == row - 1 and abs(nc - col) == 1
        else:
            return nr == row + 1 and abs(nc - col) == 1
                    
class Rook(Piece):
    def can_move(self, col, row, board, next_move_col, next_move_row):
        target = board[next_move_row][next_move_col]
        if target != None and target.color == self.color:
            return False
        
        if col == next_move_col:
            step = 1 if next_move_row > row else -1
            for r in range(row + step, next_move_row, step):
                if board[r][col] != None:
                    return False
            return True
        
        elif row == next_move_row:
            step = 1 if next_move_col > col else -1
            for c in range(col + step, next_move_col, step):
                if board[row][c] != None:
                    return False
            return True
        return False

    def can_attack(self, col, row, board, nc, nr):
        return self.can_move(col, row, board, nc, nr)

class Knight(Piece):

    def can_move(self, col, row, board, next_move_col, next_move_row):
        target = board[next_move_row][next_move_col]
        if target != None and target.color == self.color:
            return False
        dx = abs(next_move_col - col)
        dy = abs(next_move_row - row)
        if (dx, dy) in [(1,2), (2,1)]:
            return True
        return False
    
    def can_attack(self, col, row, board, nc, nr):
        return (abs(nc - col), abs(nr - row)) in [(1,2),(2,1)]
        
class Bishop(Piece):
    def can_move(self, col, row, board, next_move_col, next_move_row):
        target = board[next_move_row][next_move_col]
        if (target != None and target.color == self.color) or abs(next_move_col - col) != abs(next_move_row - row):
            return False
        step_row = -1 if next_move_row > row else 1
        step_col = -1 if next_move_col > col else 1
        check_row, check_col = row, col
        while abs(check_row - next_move_row)!= 1 and abs(check_col - next_move_col) != 1:
            check_col -= step_col
            check_row -= step_row
            if board[check_row][check_col] != None:
                return False
            
        return True
    
    def can_attack(self, col, row, board, nc, nr):
        return self.can_move(col, row, board, nc, nr)

class Queen(Piece):
    def can_move(self, col, row, board, next_move_col, next_move_row):
        target = board[next_move_row][next_move_col]
        if target != None and target.color == self.color:
            return False
        
        if abs(next_move_col - col) != abs(next_move_row - row) and row != next_move_row and col != next_move_col:
            return False
        else:
            if  abs(next_move_col - col) == abs(next_move_row - row): #like bishop
                step_row = -1 if next_move_row > row else 1
                step_col = -1 if next_move_col > col else 1
                check_row, check_col = row, col
                while abs(check_row - next_move_row)!= 1 and abs(check_col - next_move_col) != 1:
                    check_col -= step_col
                    check_row -= step_row
                    if board[check_row][check_col] != None:
                        return False
                return True
            
            elif col == next_move_col: #move like a rook
                step = 1 if next_move_row > row else -1
                for r in range(row + step, next_move_row, step):
                    if board[r][col] != None:
                        return False
                return True
            
            elif row == next_move_row:
                step = 1 if next_move_col > col else -1
                for c in range(col + step, next_move_col, step):
                    if board[row][c] != None:
                        return False
                return True
            
            return False

    def can_attack(self, col, row, board, nc, nr):
        return self.can_move(col, row, board, nc, nr)

class King(Piece):

    def __init__(self, color, image):

        super().__init__(color, image)

        self.first_move = True


    def can_move(self, c, r, board, nc, nr):
        if board[nr][nc] and board[nr][nc].color == self.color:
            return False

        return abs(nc - c) <= 1 and abs(nr - r) <= 1

    def can_attack(self, col, row, board, nc, nr):
        return self.can_move(col, row, board, nc, nr)
    
class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SIZE, SIZE))
        pygame.display.set_caption("Chess.com")

        self.board_img = pygame.image.load("chess_board.png")
        self.board_img = pygame.transform.scale(self.board_img, (SIZE, SIZE))

        self.load_images()
        self.setup_board()
        self.turn_move = "white"
        self.selected = None

        self.dragging = False
        self.drag_piece = None
        self.drag_from = None
        self.mouse_pos = (0,0)

    def load_images(self):
        global white_pawn_img, white_rook_img, white_knight_img
        global white_bishop_img, white_queen_img, white_king_img
        global black_pawn_img, black_rook_img, black_knight_img
        global black_bishop_img, black_queen_img, black_king_img

        def load(name):
            return pygame.transform.scale(pygame.image.load(name), (SQUARE,SQUARE))

        white_pawn_img = load("white_pawn.png")
        white_rook_img = load("white_rook.webp")
        white_knight_img = load("white_knight.webp")
        white_bishop_img = load("white_bishop.webp")
        white_queen_img = load("white_queen.png")
        white_king_img = load("white_king.webp")

        black_pawn_img = load("black_pawn.png")
        black_rook_img = load("black_rook.png")
        black_knight_img = load("black_knight.png")
        black_bishop_img = load("black_bishop.png")
        black_queen_img = load("black_queen.png")
        black_king_img = load("black_king.png")

    def setup_board(self):
        self.board = [[None]*8 for _ in range(8)]

        # black
        self.board[0][0] = Rook("black", black_rook_img)
        self.board[0][1] = Knight("black", black_knight_img)
        self.board[0][2] = Bishop("black", black_bishop_img)
        self.board[0][3] = Queen("black", black_queen_img)
        self.board[0][4] = King("black", black_king_img)
        self.board[0][5] = Bishop("black", black_bishop_img)
        self.board[0][6] = Knight("black", black_knight_img)
        self.board[0][7] = Rook("black", black_rook_img)

        for i in range(8):
            self.board[1][i] = Pawn("black", black_pawn_img)

        # white
        self.board[7][0] = Rook("white", white_rook_img)
        self.board[7][1] = Knight("white", white_knight_img)
        self.board[7][2] = Bishop("white", white_bishop_img)
        self.board[7][3] = Queen("white", white_queen_img)
        self.board[7][4] = King("white", white_king_img)
        self.board[7][5] = Bishop("white", white_bishop_img)
        self.board[7][6] = Knight("white", white_knight_img)
        self.board[7][7] = Rook("white", white_rook_img)

        for i in range(8):
            self.board[6][i] = Pawn("white", white_pawn_img)

    def handle_click(self, row, col):
        if self.selected is None:
            if self.board[row][col] is not None:
                self.selected = (row, col)
        else:
            start_row, start_col = self.selected
            piece = self.board[start_row][start_col]
            if piece and self.turn_move == self.board[start_row][start_col].color and piece.can_move(start_col, start_row, self.board, col, row) and is_valid_move(self.board, start_row, start_col, row, col, self.turn_move):
                piece.move(
                    (start_row, start_col),
                    (row, col),
                    self.board
                )
                self.turn_move = next_move(self.turn_move)
                if isinstance(piece, Pawn):
                    self.board[row][col] = piece.promote(row)
            self.selected = None

    def draw(self):
        self.screen.blit(self.board_img, (0,0))

        # vẽ quân cờ (trừ quân đang kéo)
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece:
                    if self.dragging and piece == self.drag_piece:
                        continue
                    self.screen.blit(piece.image, (c*SQUARE, r*SQUARE))

        # vẽ quân đang kéo theo chuột
        if self.dragging and self.drag_piece:
            x, y = self.mouse_pos
            self.screen.blit(self.drag_piece.image, (x - SQUARE//2, y - SQUARE//2))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # bắt đầu kéo
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    row = y // SQUARE
                    col = x // SQUARE

                    if self.board[row][col] and self.board[row][col].color == self.turn_move:
                        self.dragging = True
                        self.drag_piece = self.board[row][col]
                        self.drag_from = (row, col)
                        self.mouse_pos = event.pos

                # kéo theo chuột
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.mouse_pos = event.pos

                # thả quân
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging:
                        x, y = event.pos
                        row = y // SQUARE
                        col = x // SQUARE

                        sr, sc = self.drag_from
                        piece = self.drag_piece

                        if piece and piece.color == self.turn_move:
                            if piece.can_move(sc, sr, self.board, col, row) and is_valid_move(self.board, sr, sc, row, col, self.turn_move):
                                piece.move((sr, sc), (row, col), self.board)
                                self.turn_move = next_move(self.turn_move)

                                if isinstance(piece, Pawn):
                                    self.board[row][col] = piece.promote(row)

                        # reset drag
                        self.dragging = False
                        self.drag_piece = None
                        self.drag_from = None
                        self.mouse_pos = (0,0)

            self.draw()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()