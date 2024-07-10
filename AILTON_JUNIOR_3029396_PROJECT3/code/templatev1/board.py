from collections import namedtuple
import copy
from typing import List, Any
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QFrame, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt, QBasicTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QBrush, QColor
from piece import Piece
from balls import Balls
from game_logic import GameLogic


class Board(QFrame):
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new click location
    updateTimerSignal = pyqtSignal(int, int)  # signal sent when the timer is updated
    updateTurn = pyqtSignal(int)  # signal sent player turn
    checkStonePosition = pyqtSignal(object, int, int, int)  # checkStonePosition = pyqtSignal(object, int, int)
    checkLibertyForCatchStone = pyqtSignal(object, int, int,
                                           int)  # check if player scored by sending the last position insert into array
    gameOverSignal = pyqtSignal(str)
    territorySignal = pyqtSignal(int, int)
    # changeObjectInArray = pyqtSignal(int, int, int)  # check if player scored by sending the last position insert into array
    changePieceY = 0
    changePieceX = 0

    boardWidth = 7  # board width
    boardHeight = 7  # board height
    timerSpeed = 1000  # timer set to 1 sec
    counter = 120 # countdown
    counterWhite = 120
    player_turn = 2  # turn stat with black stone (2 - black / 1- white)
    ellipseLocations = []  # attribute to store multiple ellipse locations
    positionBusy = -1
    black_score = 0
    white_score = 0
    white_territory_final = 0
    black_territory_final = 0
    ko_rule_variable = [False, -1, -1, -1]

    # boardArray = []

    def __init__(self, parent):
        super().__init__(parent)
        self.boardArray = None
        self.boardArray_int = None
        self.boardArrayCopy = None
        # labels
        self.label_timeRemaining = None
        self.label_clickLocation = None
        self.label_player_turn = None
        self.white_score = 0
        self.black_score = 0
        self.isStarted = None
        self.timer = None
        self.player_turn = 2
        self.boardArray_int = None
        self.count_turn_passed = 0
        self.white_territory_final = 0
        self.black_territory_final = 0
        self.initBoard()

    def initBoard(self):
        self.timer = QBasicTimer()
        self.isStarted = False
        self.start()
        self.white_score = 0
        self.black_score = 0
        self.ko_rule_variable = [False, -1, -1, -1]
        self.count_turn_passed = 0
        self.white_territory_final = 0
        self.black_territory_final = 0

        # Board populated with 0 (no piece)
        self.boardArray = [[Balls(Piece.NoPiece, i, j) for i in range(Board.boardWidth)] for j in
                           range(Board.boardHeight)]

        # used to check array positions
        self.boardArray_int = [[0 for _ in range(Board.boardWidth)] for _ in range(Board.boardHeight)]
        self.printBoardArray()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def printBoardArray(self):
        '''prints the boardArray in an attractive way'''
        print("boardArray:")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.boardArray]))
        print("\n copy:\n ")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.boardArray_int]))

    def squareWidth(self):
        # return self.contentsRect().width() / Board.boardWidth
        return self.contentsRect().width() / (Board.boardWidth - 1)

    def squareHeight(self):
        # return self.contentsRect().height() / Board.boardHeight
        return self.contentsRect().height() / (Board.boardHeight - 1)

    def start(self):
        # Start the game
        self.isStarted = True
        self.timer.start(self.timerSpeed, self)

    def timerEvent(self, event):
        try:
            # initiate timer for currently player turn
            if self.player_turn == 2:
                # verify count_turn_passed = 2, if it is means there was 2 passes turn in row (game over)
                self.counter -= 1
                self.counterWhite = self.counterWhite
                self.updateTimerSignal.emit(self.counter, self.counterWhite)
                # times up
                if self.counter <= 0:
                    msgTimesUp = "black"
                    self.gameOverSignal.emit(msgTimesUp)

            elif self.player_turn == 1:
                # verify count_turn_passed = 2, if it is means there was 2 passes turn in row (game over)
                self.counterWhite -= 1
                self.counter = self.counter
                self.updateTimerSignal.emit(self.counter, self.counterWhite)
                if self.counterWhite <= 0:
                    msgTimesUp = "white"
                    self.gameOverSignal.emit(msgTimesUp)

            # 2 pass turn in row or time up, game over
            if self.count_turn_passed == 2 or Board.counter == 0:
                print("Game over")
                self.calculate_territory(self.boardArray_int)
                gameOVer = 'yes'
                # # call game over pop up
                self.gameOverSignal.emit(gameOVer)
        except Exception as e:
            print(e)

    def calculate_territory(self, board):
        white_territory = []
        black_territory = []

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[j][i] == 1:
                    white_territory.append((i, j))
                elif board[j][i] == 2:
                    black_territory.append((i, j))
        # update territory
        self.white_territory_final = len(white_territory)
        self.black_territory_final = len(black_territory)

        self.territorySignal.emit(self.white_territory_final, self.black_territory_final)



    def paintEvent(self, event):
        '''paints the board and the pieces of the game'''
        painter = QPainter(self)
        self.drawBoardSquares(painter)

        # Draw the ellipse if a location is set
        for ellipse_info in self.ellipseLocations:
            self.drawEllipse(painter, ellipse_info)

    def reset(self):
        # Redesenha o conteúdo usando eraseRect para limpar toda a área de desenho
        painter = QPainter(self)
        painter.eraseRect(self.rect())
        self.update()

    # Update array object
    # make the stone surranded into 0 (No piece)
    # also apply the KO rule by making the stone Unavailable for 1 turn
    def updateArrays(self, y, x, stone_player):
        print('entrou na alteracao')
        self.ko_rule_variable[0] = True
        self.ko_rule_variable[1] = x
        self.ko_rule_variable[2] = y
        self.ko_rule_variable[3] = stone_player
        self.boardArray[x][y].Piece = Piece.NoPiece
        self.boardArray_int[x][y] = 0

    def drawEllipse(self, painter, ellipse_info):
        '''draws an ellipse at the specified location'''

        try:
            '''draws an ellipse at the specified location'''
            painter.save()
            x, y = ellipse_info[
                'location']  # store location into array (very important to make sure each player has different stones colors)

            # Extract color from ellipse_info or use a default color
            color = ellipse_info.get('color', (0, 0, 0))
            color = QColor(*color)
            painter.translate(self.squareWidth() * x + self.squareWidth() * 0.7,
                              self.squareHeight() * y + self.squareHeight() * 0.7)

            # painter.setPen(color)
            painter.setBrush(color)
            radius = self.squareWidth() / 3
            center = QPoint(round(radius), round(radius))
            painter.drawEllipse(center, round(radius), round(radius))
            painter.restore()
        except Exception as e:
            print(f"Error in drawEllipse: {e}")

    # Update player turn, the timer will be rest only if turn change
    def changeTurn(self):
        if self.player_turn == 1:
            self.player_turn = 2
            self.updateTurn.emit(self.player_turn)  # end the turn, change lbl ----> it has to be improved

        elif self.player_turn == 2:
            self.player_turn = 1
            self.updateTurn.emit(self.player_turn)  # end the turn, change lbl ----> it has to be improved

        self.counter = 120
        self.counterWhite = 120
        self.start()
        try:
            # update territory
            self.calculate_territory(self.boardArray_int)
        except Exception as e:
            print(e)

    def mousePressEvent(self, event):
        '''this event is automatically called when the mouse is pressed'''
        clickLoc = "click location [" + str(event.position().x()) + "," + str(
            event.position().y()) + "]"  # the location where a mouse click was registered
        # print("mousePressEvent() - " + clickLoc)
        # TODO you could call some game logic here
        self.mousePosToColRow(event)  # calls mousePosToColRow
        self.clickLocationSignal.emit(clickLoc)
        self.printBoardArray()

    def mousePosToColRow(self, event):
        '''convert the mouse click event to a row and column'''
        xPosition = event.position().x()
        yPosition = event.position().y()
        xCoordinate = xPosition / self.squareWidth()
        yCoordinate = yPosition / self.squareHeight()
        x = round(xCoordinate)  # - 1
        y = round(yCoordinate)  # - 1
        # print(f'first {x, y}')  # to delete

        # send data to game_logic, it'll check if a stone can be placed on the board/ array
        # change variable  positionBusy = 0 (there's no stone placed)
        self.checkStonePosition.emit(self.boardArray_int, y, x, self.player_turn)

        if self.positionBusy == 0:
            # Add color by checking the turn/player
            if self.player_turn == 2:
                color = (0, 0, 0)
            else:
                color = (255, 255, 255)

            # Store the location where the ellipse should be drawn in the list
            self.ellipseLocations.append({'location': (x - 1, y - 1), 'color': color})
            try:
                self.boardArray[y][x].Piece = Piece.Black if self.player_turn == 2 else Piece.White
                if self.player_turn == 2:
                    self.boardArray_int[y][x] = 2
                    # check if current player scored
                    self.checkLibertyForCatchStone.emit(self.boardArray_int, y, x, self.player_turn)
                else:
                    self.boardArray_int[y][x] = 1
                    # check if current player scored
                    self.checkLibertyForCatchStone.emit(self.boardArray_int, y, x, self.player_turn)
            except Exception as e:
                print(f"Error in add x,r array {e}")
            # If valid move, update turn and change lbl, rest timer
            self.updateTurn.emit(self.player_turn)  # Update player turn label
            self.changeTurn()  # Update player_turn variable
            self.count_turn_passed = 0
        else:
            print(f"position {y}, {x} is busy")  # to delete

        self.update()

    def drawBoardSquares(self, painter):
        """draw all the square on the board"""
        # cpnverting in hex
        color_hex = "#7689de"
        color_hex2 ="#cedef0"
        # square colours
        color = QColor(color_hex)
        color2 = QColor(color_hex2)
        # setting the default colour of the brush
        brush = QBrush(Qt.BrushStyle.SolidPattern)  # calling SolidPattern to a variable
        brush.setColor(color)  # setting color to wood type of color
        painter.setBrush(brush)

        for row in range(0, Board.boardHeight):
            for col in range(0, Board.boardWidth):

                painter.save()
                colTransformation = self.squareWidth() * col  # setting this value equal the transformation in the
                # column direction
                rowTransformation = self.squareHeight() * row  # setting this value equal the transformation in the
                # row direction
                painter.translate(colTransformation, rowTransformation)
                painter.fillRect(col, row, round(self.squareWidth()), round(self.squareHeight()), brush)  # passing
                # the above variables and methods as a parameter
                painter.restore()

                # changing the colour of the brush so that a checkered board is drawn
                if brush.color() == color:  # if the brush color of square is color
                    brush.setColor(color2)  # set the next color of the square to color2
                else:  # if the brush color of square is color2
                    brush.setColor(color)  # set the next color of the square to color

    def resetGame(self):
        '''clears pieces from the board'''
        self.ellipseLocations = []
        self.update()
