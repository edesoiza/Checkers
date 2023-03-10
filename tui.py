from igl import CheckersGame, CheckerPiece
import os
from math import floor
from rich import print

class TUI:
    def __init__(self, nplayers, nrows):
        self.game = CheckersGame(nrows)
        self.nplayers = nplayers
        self.active = True
        self.end_turn_options = {"winner": self._winner, "draw": self._draw}

    def repr_board(self):
        """
        Prints out a colored string representation of the game board for the 
        user
        """
        cols = "  "
        for i, _ in enumerate(self.game.board.board): 
            if i < 9:
                cols = cols + str(i + 1) + " "
            elif i < 99:
                cols = cols + str(i + 1)
            else:
                break
        print(cols)

        for i, row in enumerate(self.game.board.board):
            if i < 26:
                row_str = chr(i + 65) + " "
            elif i >= 26:
                row_str = chr(floor((i - 26) / 26) + 65) + chr(i % 26 + 65)
            elif i >= 99:
                row_str = "  "

            for spot in row:
                if isinstance(spot, CheckerPiece):
                    if spot.king:
                        typing = "K"
                    else:
                        typing = "0"
                    if spot.player == self.game.board.player1:
                        color = "red"
                    else:
                        color = "yellow"
                else:
                    typing = "0"
                    color = "white"
                icon = "[bold {}]{}[/bold {}]|".format(color,typing,color)
                row_str = row_str + icon
            print(row_str)

    def play(self, error = None):
        """
        Primary Function of the TUI, Displays all important information to user
        to properly play the Checkers Game
        
        Input:
            error (None or int): intended to print what went wrong following
            clearing the console
            
        Returns: None
        """
        while self.active:
            clear()
            if error == 1:
                print("invalid move, please select another piece")
            elif error:
                print("invalid choice, please select from 1 to {}".format(error))

            self.repr_board()
            print("The current turn is {}".format(self.game.turn))
            print("The current player is {}".format(self.game.get_curr_player()))

            print("What piece location would you like to move")
            print("(You can also type resign to quit the game)")
            turn_choice = input()
            if turn_choice == "resign":
                self._quit()
            try:
                board_loc = self.game.tuple_loc(turn_choice)
                self.game.board.check_loc(board_loc, self.game.get_curr_player())
                self.game.board.check_for_piece(board_loc)
                possible_moves = self._display_possible_moves(board_loc)
                nmoves = len(possible_moves)
                possible_jumps = self._display_possible_jumps(board_loc, nmoves)
                noptions = nmoves + len(possible_jumps)
            except:
                self.play(1)

            print("Please select one of the options")
            try:
                choice = int(input())
                if choice > noptions:
                    raise Exception("Invalid move choice")
            except:
                self.play(noptions)
            end_loc = self.game.complete_turn(choice, board_loc, 
            possible_moves, possible_jumps)

            end = self.game.end_turn(end_loc)
            if end:
                self.end_turn_options[end]()

    def _display_possible_moves(self, loc):
        """
        Prints the possible move-type options to the console. Returns a list of
        them and the number of them.

        Input:
            loc (tuple): location of a checker piece

        Returns: tuple
        """
        possible_moves = self.game.get_possible_moves(loc)
        possible_moves = [self.game.de_tuple_loc(x) for x in possible_moves]
        i = 0
        for move in possible_moves:
            i += 1
            print(str(i) + ". move to " + move)
        return possible_moves

    def _display_possible_jumps(self, loc, i):
        """
        Prints the possible move-type options to the console. Returns a list of
        them and then the number of options in addition to moves.

        Input:
            loc (tuple): location of a checker piece

        Returns: tuple
        """
        possible_jumps = self.game.get_possible_jumps(loc)
        for jump in possible_jumps:
            i += 1
            if isinstance(jump, list) and len(jump) > 1:
                output = str(i) + ". jump to " + self.game.de_tuple_loc(jump[0])
                for val in jump[1:-1]:
                    output = output + " to " + self.game.de_tuple_loc(val)
                print(output)
            else:
                jump = self.game.de_tuple_loc(jump)
                print(str(i) + ". jump to " + jump)
        return possible_jumps

    def _draw(self):
        """
        Notifies player of a possible draw
        """
        print("There appears to have been a draw! Have a nice day")
        self.active = False
        quit()

    def _winner(self):
        """
        Congratulates the winner and closes the game
        """
        print("{}, You win!!!!".format(self.game.get_other_player()))
        self.active = False
        quit()

    def _quit(self):
        """
        Thanks the player and quits the game
        """
        print("thank you for playing the game! Have a nice day")
        self.active = False
        quit()

class OnlineTUI(TUI):
    def __init__(self, nrows):
        raise NotImplementedError("OnlineTUI has not been implemented")
        
def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
        