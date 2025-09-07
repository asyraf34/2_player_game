import pygame, sys
pygame.init()

import numpy as np

# global variables
WIDTH, HEIGHT = 750, 750
MESSAGE_MARGIN = 40
yellow = (255, 227, 56)
green = (0, 128, 0)
white = (255, 255, 255)
black = (0, 0, 0)
gray = (80, 80, 80)
boardcolor = pygame.Color("lightcyan3")
linecolor = pygame.Color("mistyrose4")
playercolor = [ None, black, white ]
font = pygame.font.SysFont("comicsans",24)

# create window
screen = pygame.display.set_mode((WIDTH, HEIGHT+MESSAGE_MARGIN))
pygame.display.set_caption("OMOK")

# player
# 1: black player 1 (or human player), who moves first
# 2: white player 2 (or AI)

# game state
state = np.zeros((15, 15), dtype=np.int16)
# the first move by player 1 on the center
state[7, 7] = 1

# player turn (1 or 2)
current_player = 2

# selected cell
selected_cell = None

# create a surface object, image is drawn on it.
CELL_WIDTH, CELL_HEIGHT = WIDTH/15, HEIGHT/15
RADIUS = CELL_WIDTH * 0.5 - 1

def _message_margin(txt, backgr, textcol):
    rect = pygame.Rect( (0, HEIGHT), (WIDTH, MESSAGE_MARGIN) )
    pygame.draw.rect(screen, backgr, rect)
    pos_text = font.render(txt, True, textcol)
    pos_rect = pos_text.get_rect()
    pos_rect.center = ( WIDTH/2, HEIGHT + MESSAGE_MARGIN/2 )
    screen.blit(pos_text, pos_rect)

# show the message (turn, win, tie) on the bottom of screen
def show_msg():
    if is_gameover:
        if tie:
            txt = "Tie!"
        else:
            if winner == 1: # turn of yellow
                txt = "Black Wins!"
            else:
                txt = "White Wins!"

    else:
        if current_player == 1: # turn of yellow
            txt = "Black's Turn"
        else:
            txt = "White's Turn"
    _message_margin(txt, black, white)

def draw_board(surf, state):
    surf.fill(boardcolor)

    for i in range(15): # index of row
        # locate a line at i-th col
        x = CELL_WIDTH/2 + CELL_WIDTH * i
        pygame.draw.line(surf, linecolor, (x, CELL_HEIGHT/2), (x, HEIGHT-CELL_HEIGHT/2), width=2)

    for i in range(15): # index of row
        # locate a line at i-th row
        y = CELL_HEIGHT/2 + CELL_HEIGHT * i
        pygame.draw.line(surf, linecolor, (CELL_WIDTH/2, y), (WIDTH-CELL_WIDTH/2, y), width=2)

    for i in range(15): # index of row
        for j in range(15): # index of col
            if state[i, j] == 0:
                continue
            center = (j * CELL_WIDTH + CELL_WIDTH/2, i * CELL_HEIGHT + CELL_HEIGHT/2)
            pygame.draw.circle(surf, playercolor[state[i, j]], center, RADIUS, width=0)

def cell_coord(pos):
    # get row and col & return
    # note that y -> row number, x -> col number
    return (int(pos[1] / CELL_HEIGHT), int(pos[0] / CELL_WIDTH))

adjcells = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1)
]

# return all possible actions that player can takes
def possible_moves(player, state):
    ret = list()
    
    for i in range(15):
        for j in range(15):
            if any([ True if i + adj[0] >= 0 and i + adj[0] < 15  and j + adj[1] >=0 and j + adj[1] < 15 and state[i, j] == 0 and state[i+adj[0], j+adj[1]] > 0 else False for adj in adjcells ]):
                ret.append((i, j))
    return ret

def make_move(player, state, action):
    state[action[0], action[1]] = player

# examine if the board is full
def game_over(state):
    return state.min() > 0

# return true if player wins by the last move
def win(player, state, last_move):
    x, y = last_move

    # horizontal: to right
    cnt = 1
    for i in range(1, 5):
        if y + i < 15 and state[x, y + i] == player:
            cnt += 1
        else:
            break
    # horizontal: to left
    for i in range(1, 5):
        if y - i >= 0 and state[x, y - i] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True
    
    # vertical: to down
    cnt = 1
    for i in range(1, 5):
        if x + i < 15 and state[x + i, y] == player:
            cnt += 1
        else:
            break
    # horizontal: to up
    for i in range(1, 5):
        if x - i >= 0 and state[x - i, y] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True

    # diagonal: to down right
    cnt = 1
    for i in range(1, 5):
        if y + i < 15 and x + i < 15 and state[x + i, y + i] == player:
            cnt += 1
        else:
            break
    # horizontal: to up left
    for i in range(1, 5):
        if y - i >= 0 and x - i >= 0 and state[x - i, y - i] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True

    # diagonal: to up right
    cnt = 1
    for i in range(1, 5):
        if y + i < 15 and x - i >= 0 and state[x - i, y + i] == player:
            cnt += 1
        else:
            break
    # horizontal: to down left
    for i in range(1, 5):
        if y - i >= 0 and x + i < 15 and state[x + i, y - i] == player:
            cnt += 1
        else:
            break

    if cnt >= 5:
        return True
    return False

is_gameover = False
winner = 0
tie = False
running = True

while running:
    pygame.time.delay(200)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not is_gameover:
            # calculate the clicked piece
            idx = cell_coord(pygame.mouse.get_pos())
            #print(idx)
            #print(possible_moves(current_player, state))

            # clicked out of board such as message box
            if (idx[0] <  0 or idx[0] >= 15) or (idx[1] < 0 or idx[1] >= 15):
                break

            # idx is a move
            if idx in possible_moves(current_player, state):
                make_move(current_player, state, idx)

                # examine if the game is over
                if win(current_player, state, idx):
                    is_gameover = True
                    winner = current_player
                    break

                # if no more empty cell
                elif game_over(state):
                    is_gameover = True
                    tie = True
                    break

                # switch player for the next turn
                current_player = 3 - current_player

    draw_board(screen, state)
    show_msg()
    pygame.display.update()


pygame.quit()
sys.exit()