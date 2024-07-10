from piece import Piece


class Balls(object):
    # Set some default values for the class attributes
    Piece = Piece.NoPiece
    liberties = 0
    x = -1
    y = -1
    def __str__(self):
        return str(self.Piece) # To print array board in a good way


    def __init__(self, Piece, x, y):
        # Setting instance
        self.Piece = Piece
        self.liberties = 0
        self.x = x
        self.y = y

    def getPiece(self):
        return self.Piece

    def getLiberties(self):
        return self.liberties

    def setLiberties(self, liberties):
        self.liberties = liberties

    # def getTop(self, boardArray):
    #     # Get the piece above this instance on the board
    #     if self.y == 0:
    #         # If this piece is at the top of the board, return None
    #         return None
    #     else:
    #         # Otherwise, return the piece above this one in the boardArray
    #         return boardArray[self.y - 1][self.x]
    #
    # def getRight(self, boardArray):
    #     # Get the piece to the right of this instance on the board
    #     if self.x == 6:
    #         # If this piece is at the right edge of the board, return None
    #         return None
    #     else:
    #         # Otherwise, return the piece to the right of this one in the boardArray
    #         return boardArray[self.y][self.x + 1]
    #
    # def getLeft(self, boardArray):
    #     # Get the piece to the left of this instance on the board
    #     if self.x == 0:
    #         # If this piece is at the left edge of the board, return None
    #         return None
    #     else:
    #         # Otherwise, return the piece to the left of this one in the boardArray
    #         return boardArray[self.y][self.x - 1]
    #
    # def getDown(self, boardArray):
    #     # Get the piece below this instance on the board
    #     if self.y == 6:
    #         # If this piece is at the bottom of the board, return None
    #         return None
    #     else:
    #         # Otherwise, return the piece below this one in the boardArray
    #         return boardArray[self.y + 1][self.x]
