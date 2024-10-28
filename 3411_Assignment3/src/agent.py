#!/usr/bin/python3

"""
I used the basic alpha beta search given in the starter code as a base. I change the iteration function from 
            this_eval = -alphabeta(3-player, depth+1, boards, -beta, -alpha, best_move, boards)
            to:
            this_eval = -alphabeta(3-player, depth+1, boards[r], -beta, -alpha, best_move, boards)
To be more specific, I let one party to iterate on the board based on the previous move made by its opponent. As is 
specified by the rules of super tic tac toe.
                                
What's more, I set some evaluation function and limits for my alphabeta function.
1. When depth is exceeding some steps I will knock it off. Based on my test, it is getting very very slow when you do 10 depth alpha beta search. The 
returned value is the best pieces' difference out of all 9 boards times 20 till that moment.
2. An absolute death for simulation. Whenever the agent tries to make a move that won't get itself an instant victory but will lead the game into
the board that the opponent will only need to make one move to win. In this case, no value is too low to highlight this scenario.
3. When in the late games, the board(9x9) is likely to be full, the edge condition, if not specified will lead into an infinite loop.

Other than that, this asnwer is pretty similar to the sample code provided.
"""






import socket
import sys
import numpy as np

# a board cell can hold:
#   0 - Empty
#   1 - We played here
#   2 - Opponent played here
EMPTY = 0
PLAYER = 1
OPPONENT = 2
MIN_EVAL = -1000000
MAX_EVAL = 1000000
# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
s = [".", "X", "O"]
curr = 0  # this is the current board to play in




def print_board_row(bd, a, b, c, i, j, k):
    print(" "+s[bd[a][i]]+" "+s[bd[a][j]]+" "+s[bd[a][k]]+" | "
             + s[bd[b][i]]+" "+s[bd[b][j]]+" "+s[bd[b][k]]+" | "
             + s[bd[c][i]]+" "+s[bd[c][j]]+" "+s[bd[c][k]])

# Print the entire board


def print_board(board):
    print_board_row(board, 1, 2, 3, 1, 2, 3)
    print_board_row(board, 1, 2, 3, 4, 5, 6)
    print_board_row(board, 1, 2, 3, 7, 8, 9)
    print(" ------+-------+------")
    print_board_row(board, 4, 5, 6, 1, 2, 3)
    print_board_row(board, 4, 5, 6, 4, 5, 6)
    print_board_row(board, 4, 5, 6, 7, 8, 9)
    print(" ------+-------+------")
    print_board_row(board, 7, 8, 9, 1, 2, 3)
    print_board_row(board, 7, 8, 9, 4, 5, 6)
    print_board_row(board, 7, 8, 9, 7, 8, 9)
    print()

def board_full(boards):
    taken_slots = 0
    for b in boards:
        taken_slots+= count_taken_slots(b)
    return taken_slots == 49
    

def count_taken_slots(board):
    taken_slots = 0
    for cell in board[1:10]:
        if cell != EMPTY:
            taken_slots += 1
    return taken_slots

def count_player_slot(player, board):
    taken_slots = 0
    taken_slots = 0
    for cell in board[1:10]:
        if cell == player:
            taken_slots += 1
    return taken_slots  

# choose a move to play
def play():
    print_board(boards)
    best_move = np.zeros(49, dtype=np.int32)
    m = count_taken_slots(boards[curr])
    alphabeta(1, m, boards[curr], MIN_EVAL, MAX_EVAL, best_move, boards)
    chosen_move = best_move[m]
    print("place piece on board", curr, " place ", chosen_move)
    place(curr, chosen_move, 1)
    return chosen_move

# place a move in the global boards


def place(board, num, player):
    global curr
    boards[board][num] = player
    curr = num

# read what the server sent us and
# parse only the strings that are necessary


def parse(string):
    if "(" in string:
        command, args = string.split("(")
        args = args.split(")")[0]
        args = args.split(",")
    else:
        command, args = string, []

    if command == "second_move":
        print("second move function called")
        place(int(args[0]), int(args[1]), 2)
        return play()  # choose and return the second move

    elif command == "third_move":
        print("third move function called")
        place(int(args[0]), int(args[1]), 1)
        place(curr, int(args[2]), 2)
        return play()

    elif command == "next_move":
        print("next move function called")
        # place the previous move (chosen by opponent)
        place(curr, int(args[0]), 2)
        return play()  # choose and return our next move

    elif command == "win":
        print("Yay!! We win!! :)")
        return -1

    elif command == "loss":
        print("We lost :(")
        return -1

    return 0

# alpha-beta algorithm


def alphabeta(player, depth, board, alpha, beta, best_move, boards):
    # print("depth is ", depth)
    best_eval = MIN_EVAL
    if game_won(3-player, board):
        return -1000 + depth
    if depth > 6:
        value = 0
        for b in boards:
            value = max((count_player_slot(player, b) - count_player_slot(3-player, b)),value)
        return value*20
    if board_full(boards):
         return 0
    
    this_move = 0
    for r in range(1, 10):
        if board[r] == EMPTY:
            this_move = r
            board[r] = player
            # if we can not win the game by making move r, and that move will give opponent victory, abandon it.
            if (not game_won(player, board)) and potential_threat(r):
                board[r] = EMPTY
                continue

            this_eval = -alphabeta(3-player, depth+1,
                                   boards[r], -beta, -alpha, best_move, boards)
            board[r] = EMPTY
            # - 7*count_player_slot(3-player, boards[r])
            if this_eval > best_eval:
                best_move[depth] = r
                best_eval = this_eval
                if best_eval > alpha:
                    alpha = best_eval
                    if alpha >= beta:
                        return (alpha)
    if this_move == 0:
        return 0  # Draw
    return alpha


def potential_threat(next_move):
    nxt_board = boards[next_move]

    opponent = 2
    lines = [
        (1, 2, 3), (4, 5, 6), (7, 8, 9),
        (1, 4, 7), (2, 5, 8), (3, 6, 9),
        (1, 5, 9), (3, 5, 7)
    ]
    for a, b, c in lines:
        if nxt_board[a] == nxt_board[b] == opponent and nxt_board[c] == EMPTY:
            return True
        if nxt_board[a] == nxt_board[c] == opponent and nxt_board[b] == EMPTY:
            return True
        if nxt_board[b] == nxt_board[c] == opponent and nxt_board[a] == EMPTY:
            return True
    return False


def game_won(p, bd):
    return ((bd[1] == p and bd[2] == p and bd[3] == p)
            or (bd[4] == p and bd[5] == p and bd[6] == p)
            or (bd[7] == p and bd[8] == p and bd[9] == p)
            or (bd[1] == p and bd[4] == p and bd[7] == p)
            or (bd[2] == p and bd[5] == p and bd[8] == p)
            or (bd[3] == p and bd[6] == p and bd[9] == p)
            or (bd[1] == p and bd[5] == p and bd[9] == p)
            or (bd[3] == p and bd[5] == p and bd[7] == p))


# connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[2])  # Usage: ./agent.py -p (port)

    s.connect(('localhost', port))
    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = parse(line)
            if response == -1:
                s.close()
                return
            elif response > 0:
                s.sendall((str(response) + "\n").encode())


if __name__ == "__main__":
    main()
