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
            self.turn_types = dictionary of turn functions given an input
        Returns: None
        """
        super(CheckersGame, self).__init__()
        nrows = 2 * n + 2
        ncols = 2 * n + 2
        self.player1 = Player(1, nrows)
        self.player2 = Player(2, nrows)
        self.board = CheckerBoard(nrows, ncols, self.player1, self.player2)

        self.turn = 1
        self.mod_to_player = {1:self.player1, 0:self.player2}
        self.turn_types = {"move":self.move_piece, "jump": self.jump_piece}

    def get_curr_player(self):
        return self.mod_to_player[self.turn %  2]

    def get_other_player(self):
        return self.mod_to_player[(self.turn + 1) % 2]

    def tuple_loc(self, input_val = None):
        """
        Takes in a console line input and turns into a tuple containing the 
        location index for a piece. Or returns False if the input was "resign"
        Returns: tuple[int] or False
        """
        raw_loc = list(input_val)
        try:
            row = ord(raw_loc[0].upper())
            col = int(raw_loc[1])
        except:
            raise Exception("Invalid input")
        loc_tup = tuple([row - 65, col - 1])
        return loc_tup

    def de_tuple_loc(self, loc_tuple):
        row, col = loc_tuple
        row = chr(row + 65)
        col = str(col + 1)

        return row + col

    def can_move_piece(self, curr_loc, new_loc):
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
        try:
            self.board.check_loc(new_loc, None)
        except:
            return False

        if abs(new_loc_c - curr_loc_c) == 1:
            if not piece.king and curr_loc_r - new_loc_r == 1:
                return True
            elif piece.king and abs(new_loc_r - curr_loc_r) == 1:
                return True
        return False

    def can_jump_piece(self, curr_loc, new_loc):
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
        try:
            self.board.check_loc(new_loc, None)
        except:
            return False

        r_diff = curr_loc_r - new_loc_r
        c_diff = curr_loc_c - new_loc_c
        j_r, j_c = self.board._get_jumpover_piece_loc(curr_loc, new_loc)

        jumpover_piece = self.board.board[j_r][j_c]
        if not isinstance(jumpover_piece, CheckerPiece):
            return False
        if jumpover_piece.player != self.get_other_player():
            return False
        if (abs(r_diff) == 2 and abs(c_diff) == 2 and jumpover_piece and 
        jumpover_piece != curr_piece):
            return True
        return False

    def move_piece(self, curr_loc, new_loc):
        return self.board.move_piece(curr_loc, new_loc)

    def jump_piece(self, curr_loc, new_loc):
        return self.board.jump_piece(curr_loc, new_loc)
    
    def _check_for_kingship(self, loc):
        """
        Checks if the piece being moved for the turn can be kinged
        Input:
            loc (tuple): location index of the piece
        
        Returns: None
        """
        loc_r, loc_c = loc
        if loc_r == 0:
            self.board.board[loc_r][loc_c].king_piece()

    def _check_draw(self):
        """
        Checks if there is a possible draw in the match

        Returns: bool
        """
        can_opponent_move = self._can_move_any()
        self.turn += 1
        can_current_move = self._can_move_any()
        self.turn -= 1
        return not can_current_move and not can_opponent_move

    def _check_winner(self):
        """
        Checks if there has been a winner at the end of a turn
        
        Returns: bool
        """
        if self.get_other_player().piece_count == 0 or not self._can_move_any():
            return True
        return False

    def _can_move_any(self):
        """
        Iterates over the current player's pieces to see if they can move any 
        of their pieces
        
        Returns: bool
        """
        for i, row in enumerate(self.board.board):
            for j, p in enumerate(row):
                if (isinstance(p, CheckerPiece) and 
                p.player == self.get_curr_player()):
                    move_options = self.get_possible_moves((i,j))
                    jump_options = self.get_possible_jumps((i,j))
                    if len(move_options) > 0 or len(jump_options) > 0:
                        return True
        return False

    def get_possible_moves(self, loc):
        """
        Collects the possible moves a piece can make. Returns the location it
        can move to
        
        Input:
            loc (tuple): location of a piece
            
        Returns: list[tuple]
        """
        i, j = loc
        piece = self.board.board[i][j]
        possible_moves = []
        if piece.king:
            if self.can_move_piece((i,j), (i+1, j-1)):
                possible_moves.append((i+1, j-1))
            if self.can_move_piece((i,j), (i+1, j+1)):
                possible_moves.append((i+1, j+1))
        if self.can_move_piece((i,j), (i-1,j-1)):
            possible_moves.append((i-1,j-1))
        if self.can_move_piece((i,j), (i-1,j+1)):
            possible_moves.append((i-1,j+1))

        return possible_moves

    def get_possible_jumps(self, loc, ol = None, current_path = None):
        """
        Collects the possible jumps a piece can make. Returns the locations it
        can move to
        
        Input:
            loc (tuple): location of a piece
            
        Returns: list
        """
        i, j = loc
        possible_jumps = []

        if ol:
            oi, oj = ol
            original_piece = self.board.board[oi][oj]
            piece = original_piece
        else:
            piece = self.board.board[i][j]
            ol = loc
            current_path = []

        if not isinstance(piece, CheckerPiece):
            return possible_jumps

        if piece.king:
            king_jump_locations = [(i+2, j-2), (i+2, j+2)]
            for location in king_jump_locations:
                if self.can_jump_piece((loc), location):
                    new_loc = location
                    self._get_additional_jumps(new_loc, possible_jumps, ol, 
                    current_path)

        regular_jump_locations = [(i-2, j-2), (i-2, j+2)]
        for location in regular_jump_locations:
            if self.can_jump_piece(loc, location):
                new_loc = location
                self._get_additional_jumps(new_loc, possible_jumps, ol, 
                current_path)

        return possible_jumps

    def _get_additional_jumps(self, loc, possible_jumps, ol, current_path):
        """
        Given that a piece can jump from one place to another, examines if it
        can move farther down the board
        
        Input:
            loc (tuple): location to be checked for additional jumps
            possible_jumps (list): list of currently possible jump paths
            ol (tuple): original location of the piece
            current_path (list): the current path of locatiosn the peice will 
            travel

        Returns: None
            """
        possible_jumps.append(tuple(loc))
        current_path += [loc]
        more_possible_jumps = self.get_possible_jumps(loc, ol, current_path)
        if more_possible_jumps:
            mapped_p_moves = [current_path + [x] for x in more_possible_jumps]
            
            possible_jumps += mapped_p_moves

    def complete_turn(self, choice, board_loc, possible_moves, possible_jumps):
        """
        By being given all possible options, accesses the choice index of the
        possible moves and jumps list in order to complete the requested move
        
        Input:
            choice (int): option selected
            board_loc (tuple): location of piece
            possible_moves (list): list of possible moves
            possible_jumps (list): list of possible jumps
            
        Returns: tuple
        """
        nmoves = len(possible_moves)

        if choice <= nmoves:
            board_new_loc = self.tuple_loc(possible_moves[choice - 1])
            self.board.move_piece(board_loc, board_new_loc)
        else:
            move_selection = possible_jumps[choice - nmoves - 1]
            if isinstance(move_selection, list):
                for i in possible_jumps[choice - nmoves - 1][:-1]:
                    board_new_loc = i
                    self.board.jump_piece(board_loc, board_new_loc)
                    board_loc = i
            else:
                board_new_loc = possible_jumps[choice - nmoves - 1]
                self.board.jump_piece(board_loc, board_new_loc)
        return board_new_loc

    def end_turn(self, loc):
        """
        Ends turn and updates values to prepare for the next turn of gameplay
        
        Input:
            loc (tuple): location index of a piece
            
        Returns: None
        """
        self._check_for_kingship(loc)

        self.turn += 1
        self.board._flip_board()
        if self._check_draw():
            return "draw"

        if self._check_winner():
            return "winner"

class OnlineCheckersGame():
    def __init__(self, game_options):
        raise NotImplementedError("Online was not implemented")

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

    def _create_board(self, nrows, ncols):
        """
        Initializes the board given the dimensions of rows and columns
        
        Input:
            nrows (int): number of rows
            ncols (int): number of columns
        
        Returns: None
        """
        raise NotImplementedError("Board Creation Must be Implemented in Subclass")

    def check_loc(self, loc, expected_val = None):
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
        if loc_r < 0 or loc_c < 0:
            raise Exception("not a valid location")
        try:
            loc_on_board = self.board[loc_r][loc_c]

        except:
            raise Exception("not valid")

        if isinstance(loc_on_board, CheckerPiece):
            if loc_on_board.player != expected_val:
                raise Exception("invald location")
        else:
            if loc_on_board != expected_val:
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

    def _flip_board(self):
        """
        Flips board and its representation
        
        Returns: None
        """
        self.board = np.rot90(np.rot90(self.board))
        
class CheckerBoard(Board):
    def __init__(self, nrows, ncols, p1, p2):
        self.player1 = p1
        self.player2 = p2
        self.board  = self._create_board(nrows, ncols)

    def _create_board(self, nrows, ncols):
        """
        Initializes the board given the dimensions of rows and columns
        
        Input:
            nrows (int): number of rows
            ncols (int): number of columns
        
        Returns: ndarray
        """
        board = np.full((nrows, ncols), None)

        for i, row in enumerate(board):
            for j, _ in enumerate(row):
                if i >= (nrows / 2 + 1):
                    piece = CheckerPiece(self.player1)
                elif i <= (nrows / 2 - 2):
                    piece = CheckerPiece(self.player2)
                else:
                    continue
                if i % 2 == 0 and j % 2 != 0:
                    board[i][j] = piece
                elif i % 2 != 0 and j % 2 == 0:
                    board[i][j] = piece

        return board
    
    def check_for_piece(self, loc):
        """
        Checks to see if given a location, that a Checker piece is there
        
        Inputs:
            loc (tuple): location index for board matrix
            
        Returns: None or Exception
        """
        i, j = loc
        if not isinstance(self.board[i][j], CheckerPiece):
            raise Exception()

    def _get_jumpover_piece_loc(self, curr_loc, new_loc):
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
        self._remove_piece(self._get_jumpover_piece_loc(curr_loc, new_loc))
        self.move_piece(curr_loc, new_loc)

    def to_lst_grid(self):
        """
        Converts board into a list of values
        
        Returns: list
        """
        grid = []
        for row in self.board:
            row_lst = []
            for slot in row:
                if slot == None:
                    row_lst.append(" ")
                elif isinstance(slot, CheckerPiece):
                    row_lst.append(str(slot.value))
            grid.append(row_lst)
        return grid

    def _remove_piece(self, loc):
        """
        Removes piece from board 
        Input:
            loc (tuple): location index of piece
        Returns: None
        """
        board = self.board
        r_loc, c_loc = loc
        board[r_loc][c_loc] = None
        self.board = board

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