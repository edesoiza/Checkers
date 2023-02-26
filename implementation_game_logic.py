import numpy as np
class CheckersGame:
    def __init__(self, n):
        """
        Constructor
        
        Args:
            n (int): number of rows of pieces per player
            
        Attributes:
            self.player1 = Player Class Object for player 1
            self.player2 = Player Class Object for player 2
            self.board = Board Class Object for the game
            self.turn = turn count of game
            self.attempt_types = dictionary of attempt functions given an input
            self.turn_types = dictionary of turn functions given an input

        Returns: None
        """
        nrows = 2 * n + 2
        ncols = 2 * n + 2
        self.player1 = Player(1, nrows)
        self.player2 = Player(2, nrows)
        self.board = CheckerBoard(nrows, ncols, self.player1, self.player2)

        self.turn = 1
        self.mod_to_player = {1:self.player1, 0:self.player2}
        self.attempt_types = {"move": self._can_move_piece, "jump": self._can_jump_piece}
        self.turn_types = {"move":self.board.move_piece, "jump": self.board.jump_piece}

    def get_curr_player(self):
        return self.mod_to_player[self.turn %  2]

    def get_other_player(self):
        return self.mod_to_player[(self.turn + 1) % 2]

    def _play(self):
        """
        Sets up the beginning of a turn by printing out important game info
        and set up for the user's turn
        
        Returns: None
        """
        print(self.board)
        print("current turn is {}".format(self.turn))
        print("current player is {}".format(self.get_curr_player()))
        print("what type of move would you like to make")

        turn_type = input().lower()
        if turn_type not in self.turn_types:
            print("invalid turn type")
            self._play()

        self.start_turn(turn_type)

    def start_turn(self, turn_type):
        """
        The primary logic for a turn, given a type of turn, will request certain
        information from the user to have a complete and successful turn
        
        Input: 
            turn_type (str): the type of turn being attempted
            
        Returns: None
        """
        print("current loc")
        try:
            curr_loc = self.tuple_loc()
            self.board.check_loc(curr_loc, self.get_curr_player(), self.get_curr_player())
        except:
            print("invalid current loc")
            self.start_turn(turn_type)

        print("new loc")
        try:
            new_loc = self.tuple_loc()
            self.board.check_loc(new_loc, self.get_curr_player())
        except:
            print("invalid new loc")
            self.start_turn(turn_type)

        attempt_possible = self.attempt_types[turn_type](curr_loc, new_loc)
        if not attempt_possible:
            print("attempt was not possible to complete")
            self._play()

        self.turn_types[turn_type](curr_loc, new_loc)
        if turn_type == "jump":
            self.get_other_player().piece_count -= 1
        self.end_turn(new_loc)

    def tuple_loc(self):
        """
        Takes in a console line input and turns into a tuple containing the 
        location index for a piece

        Returns: tuple[int]
        """
        raw_loc = input().split()
        loc_tup = tuple([int(x) for x in raw_loc])
        return loc_tup

    def _can_move_piece(self, curr_loc, new_loc):
        """
        Checks if piece at location can move to a new location

        Input:
            curr_loc (tuple): current location index of the piece
            new_loc (tuple): new location index of the piece

        Returns: bool
        """
        curr_loc_r, curr_loc_c = curr_loc
        new_loc_r, new_loc_c = new_loc
        piece = self.board.board[curr_loc_r][curr_loc_c]
        if abs(new_loc_c - curr_loc_c) == 1:
            if not piece.king and curr_loc_r - new_loc_r == 1:
                return True
            elif piece.king and abs(new_loc_r - curr_loc_r) == 1:
                return True
        return False

    def _can_jump_piece(self, curr_loc, new_loc):
        """
        Checks if piece at location can jump another piece

        Input:
            curr_loc (tuple): current location index of the piece
            new_loc (tuple): new location index of the piece
        
        Returns: bool
        """
        curr_loc_r, curr_loc_c = curr_loc
        new_loc_r, new_loc_c = new_loc
        curr_piece = self.board.board[curr_loc_r][curr_loc_c]

        r_diff = curr_loc_r - new_loc_r
        c_diff = curr_loc_c - new_loc_c

        jumpover_r, jumpover_c = self.board.get_jumpover_piece_loc(curr_loc, new_loc)
        jumpover_piece = self.board.board[jumpover_r][jumpover_c]

        if (abs(r_diff) == 2 and abs(c_diff) == 2 and jumpover_piece and 
        jumpover_piece != curr_piece):
            if curr_piece.king or (not curr_piece.king and r_diff > 0):
                return True
        return False
    
    def end_turn(self, loc):
        """
        Ends turn and updates values to prepare for the next turn of gameplay
        
        Input:
            loc (tuple): location index of a piece
            
        Returns: None
        """
        self.check_for_kingship(loc)

        if self._check_winner():
            self._winner()
        
        self.turn += 1
        self.board.flip_board()

        self._play()

    def check_for_kingship(self, loc):
        """
        Checks if the piece being moved for the turn can be kinged

        Input:
            loc (tuple): location index of the piece
        
        Returns: None
        """
        loc_r, loc_c = loc
        if loc_r == 0:
            self.board.board[loc_r][loc_c].king_piece()

    def _check_winner(self):
        """
        Checks if there has been a winner at the end of a turn
        
        Returns: bool
        """
        if self.get_other_player().piece_count == 0:
            return True
        return False

    def _winner(self):
        """
        Congratulates the winner and closes the game

        Returns: None
        """
        print("You win!!!!")
        quit()

class Board: 
    def __init__(self, nrows, ncols, p1, p2):
        """
        Constructor 
        Arg:
            nrows (int): number of rows 
            ncols (int): number of columns
            p1 (Player): player 1 class object
            p2 (Player): player 2 class object

        Attributes:
            self.player1 = p1
            self.player2 = p2
            self.piece1 = a piece corresponding to player 1
            self.piece2 = a piece corresponding to player 2
            self.board = array of board
            self.view = simplify array of self.board

        Returns: None
        """
        self.player1 = p1
        self.player2 = p2
        self.piece1 = Piece(self.player1)
        self.piece2 = Piece(self.player2)
        self.board  = self._create_board(nrows, ncols)
        self.view = self._get_repr_board()

    def _create_board(self, nrows, ncols):
        """
        Initializes the board given the dimensions of rows and columns
        
        Input:
            nrows (int): number of rows
            ncols (int): number of columns
        
        Returns: None
        """
        raise NotImplementedError("Board Creation Must be Implemented in Subclass")
    
    def _get_repr_board(self):
        """
        Generates a simple representation of the board attribute
        
        Returns: None
        """
        raise NotImplementedError("Board Representation Must be Implemented in Subclass")

    def check_loc(self, loc, current_player, expected_val = None):
        """
        Checks to see if the provided location is not only existent but also
        contains the expected value
        
        Input:
            loc (tuple): location index
            current_player (Player): the current player for the turn
            expected_value (None or Player): the expected value in the index
            
        Returns: None or Exception
        """
        loc_r, loc_c = loc
        try:
            loc_on_board = self.board[loc_r][loc_c]

        except:
            raise Exception("not valid")

        if expected_val and expected_val != current_player:
            raise Exception("not a valid location")
        
    def move_piece(self, curr_loc, new_loc):
        """
        If piece at loc can move, moves piece 

        Input:
            curr_loc (tuple): current location index of the piece
            new_loc (tuple): new location index of the piece

        Returns: None
        """
        curr_loc_r, curr_loc_c = curr_loc
        new_loc_r, new_loc_c = new_loc

        temp = self.board[curr_loc_r][curr_loc_c]
        self.board[curr_loc_r][curr_loc_c] = self.board[new_loc_r][new_loc_c]
        self.board[new_loc_r][new_loc_c] = temp
        
    def _remove_piece(self, loc):
        """
        Removes piece from board 

        Input:
            loc (tuple): location index of piece

        Returns: None
        """
        r_loc, c_loc = loc
        self.board[r_loc][c_loc] = None

    def flip_board(self):
        """
        Flips board and its representation
        
        Returns: None
        """
        self.board = np.rot90(np.rot90(self.board))
        self.view = self._get_repr_board()

    def __str__(self):
        """
        Str representation of board 

        Returns: str
        """
        return np.array2string(self.view, separator = " ")

class CheckerBoard(Board):
    def __init__(self, nrows, ncols, p1, p2):
        self.player1 = p1
        self.player2 = p2
        self.piece1 = CheckerPiece(self.player1)
        self.piece2 = CheckerPiece(self.player2)
        self.board  = self._create_board(nrows, ncols)
        self.view = self._get_repr_board()

    def _create_board(self, nrows, ncols):
        """
        Initializes the board given the dimensions of rows and columns
        
        Input:
            nrows (int): number of rows
            ncols (int): number of columns
        
        Returns: ndarray
        """
        board = np.full((nrows, ncols), None)
        for i in range(nrows):
            if i >= (nrows / 2 + 1):
                piece = self.piece1
            elif i <= (nrows / 2 - 2):
                piece = self.piece2
            else:
                continue

            if i % 2:
                board[i,0::2] = piece
            else:
                board[i,1::2] = piece
        return board
        
    def _get_repr_board(self):
        """
        Generate a simple representation of the numpy array that is 
        used for the board
        
        Returns: ndarray
        """
        p1_overwrite = np.where(self.board == self.piece1, 1, self.board)
        p2_overwrite = np.where(p1_overwrite == self.piece2, 2, p1_overwrite)
        none_overwrite = np.where(p2_overwrite == None, 0, p2_overwrite)
        return none_overwrite

    def get_jumpover_piece_loc(self, curr_loc, new_loc):
        """
        Finds and returns the location index of the piece in between the points
        that the piece jumps from
        
        Inputs:
            curr_loc (tuple): current location index of the piece
            new_loc (tuple): new location index of the piece
            
        Returns: tuple[int]
        """
        curr_loc_r, curr_loc_c = curr_loc
        new_loc_r, new_loc_c = new_loc

        r_diff_mid = (curr_loc_r + new_loc_r) // 2
        c_diff_mid = (curr_loc_c + new_loc_c) // 2

        return((r_diff_mid, c_diff_mid))

    def jump_piece(self, curr_loc, new_loc):
        """
        Not only removes the piece that is jumped over but also moves the piece
        from one point to another
        
        Input:
            curr_loc (tuple): current location index of the piece
            new_loc (tuple): new location index of the piece
            
        Returns: None
        """
        self._remove_piece(self.get_jumpover_piece_loc(curr_loc, new_loc))
        self.move_piece(curr_loc, new_loc)

class Piece: 
    '''
    Class that represents a piece
    '''
    def __init__(self, player):
        """
        Constructor
        """
        self.player = player

class CheckerPiece(Piece):
    def __init__(self, player):
        self.player = player
        self.king = False

    def king_piece(self):
        self.king = True

class Player:
    """
    Player class for maneuvering pieces on board
    """
    def __init__(self, player_num, nrows):
        """
        Constructor

        """
        self.player_num = player_num
        n = (nrows - 2) // 2
        self.piece_count = n * (n+1)

    def __str__(self):
        return "player {}".format(self.player_num)

if "__main__" == __name__:
    n = 3
    game = CheckersGame(n)
    game._play()
