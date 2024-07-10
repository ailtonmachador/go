from PyQt6.QtWidgets import QDockWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, \
    QHBoxLayout
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QPainter, QBrush, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QFrame
from PyQt6.QtGui import QTextDocument
from piece import Piece
from balls import Balls
from board import Board


class ScoreBoard(QDockWidget):
    '''# base the score_board on a QDockWidget'''

    def __init__(self):
        super().__init__()
        self.board = None
        self.player_turn = Board.player_turn
        self.scoreWhite = Board.white_score
        self.scoreBlack = Board.black_score
        self.white_territory_final = Board.white_territory_final
        self.black_territory_final = Board.black_territory_final
        self.ellipseLocations = Board.ellipseLocations
        self.black_final_score = 0
        self.white_final_score = 0
        '''initiates ScoreBoard UI'''
        self.resize(200, 200)
        self.setWindowTitle('ScoreBoard')

        # Main  Layout
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self)

        # Sublayouts
        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()
        self.layout3 = QVBoxLayout()

        # create two labels which will be updated by signals
        self.label_clickLocation = QLabel("Click Location: ")
        self.label_timeRemainingB = QLabel("Time Remaining\n Black stone: ")
        self.label_territoryB = QLabel("Black Territory: ")
        self.label_territoryW = QLabel("White Territory: ")
        self.label_timeRemainingW = QLabel("Time Remaining\n White stone: ")
        self.label_player_turn = QLabel("Player turn: Black")
        self.label_score = QLabel("SCORE:")
        self.label_white_score = QLabel("White player:\n Stones capture")
        self.label_black_score = QLabel("Black player:\n Stones capture")

        # create buttons
        self.button = QPushButton("PASS TURN")
        self.resetBtn = QPushButton("REST GAME")
        self.howToPlayBtn = QPushButton("How to Play")

        # add widgets to sublayouts

        # layout 1 to lbls for black stone player
        self.layout1.addWidget(self.label_timeRemainingB)
        self.layout1.addWidget(self.label_black_score)
        self.layout1.addWidget(self.label_territoryB)

        # layout 2 to lbls for white stone player
        self.layout2.addWidget(self.label_timeRemainingW)
        self.layout2.addWidget(self.label_white_score)
        self.layout2.addWidget(self.label_territoryW)

        # layout 3 to buttons, player turn
        self.layout3.addWidget(self.label_player_turn)
        self.layout3.addWidget(self.button)
        self.layout3.addWidget(self.resetBtn)
        self.layout3.addWidget(self.howToPlayBtn)

        # Adiciona os sublayouts ao layout principal
        self.mainLayout.addLayout(self.layout1)
        self.mainLayout.addLayout(self.layout3)
        self.mainLayout.addLayout(self.layout2)

        # style for layouts white
        self.label_territoryB.setStyleSheet("background-color: black; margin: 5; color: white")
        self.label_timeRemainingB.setStyleSheet("background-color: black; margin: 5; color: white")
        self.label_black_score.setStyleSheet("background-color: black; margin: 5; color: white")
        self.label_player_turn.setStyleSheet(
            "background-color: none; margin: 7; padding-top: 0; font-size: 16px; alignment: AlignVCenter;")

        # style for layouts QVBoxLayout
        self.mainWidget.setStyleSheet("""
                   QVBoxLayout {
                       background-color: gray;
                   }
                   QPushButton {
                       padding-top: 0;
                       margin: 5px;
                   }
                   QLabel {
                       background-color: white;
                       margin: 7px;
                       font: 14pt sans-serif;
                       
                   }                   
               """)

        self.mainWidget.setLayout(self.mainLayout)

        self.setWidget(self.mainWidget)

    def make_connection(self, board):
        '''this handles a signal sent from the board class'''
        # when the clickLocationSignal is emitted in board the setClickLocation slot receives it
        board.clickLocationSignal.connect(self.setClickLocation)
        # when the updateTimerSignal is emitted in the board the setTimeRemaining slot receives it
        board.updateTimerSignal.connect(self.setTimeRemaining)
        board.updateTurn.connect(self.setTurn)
        # board.checkStonePosition.connect(self.checkingStonePositionsBusy)
        board.checkStonePosition.connect(self.rules)
        # capture stone if surrond enemy
        board.checkLibertyForCatchStone.connect(self.checkLibertyForCatchStone)
        # change elements in array obeject
        # board.changeObjectInArray.connect(self.changeObject)
        self.board = board  # Store the instance of the Board class
        self.button.clicked.connect(self.passTurn)
        self.resetBtn.clicked.connect(self.reset)
        self.howToPlayBtn.clicked.connect(self.howToPlay)
        board.gameOverSignal.connect(self.gameOver)
        board.territorySignal.connect(self.territory)



    @pyqtSlot(int, int)
    def territory(self, white_territory_final, black_territory_final):
        try:
            black = str(black_territory_final)
            white = str(white_territory_final)
            self.label_territoryW.setText("White territory: " + white)
            self.label_territoryB.setText("black territory: " + black)
        except Exception as e:
          print(e)

    @pyqtSlot(str)
    def gameOver(self, msgTimesUp: str):
        # get final score
        self.finalScore()

        try:
            if msgTimesUp == 'black':
                gameOverMsg = "Black stone player, your time is up,\n you have loose"
            elif msgTimesUp == 'white':
                gameOverMsg = "White stone player, your time is up,\n you have loose"

            else:
                if self.white_final_score > self.black_final_score:
                    gameOverMsg = (
                        f"Game over\n White stone player has won  \n score: White: {self.white_final_score}\n\n,     Black: {self.black_final_score}\n\n"
                        f"White has {self.scoreWhite} black pieces captured and\n"
                        f"Has won {self.board.white_territory_final} territory (pieces placed on the board)\n\n"
                        f"Black has {self.scoreBlack} white pieces captured and\n"
                        f"Has won {self.board.black_territory_final} territory (pieces placed on the board) ")
                elif self.white_final_score < self.black_final_score:
                    gameOverMsg = (
                        f"Game over\n Black stone player has won  \n score: White: {self.white_final_score}     Black: {self.black_final_score}\n\n"
                        f"White has {self.scoreWhite} black pieces captured and\n"
                        f"Has won {self.board.white_territory_final} territory (pieces placed on the board)\n\n"
                        f"Black has {self.scoreBlack} white pieces captured and\n"
                        f"Has won {self.board.black_territory_final} territory (pieces placed on the board) ")
                else:
                    gameOverMsg = (
                        f"Game over\n It is a draw \n score: white {self.white_final_score},   Black {self.black_final_score}\n\n"
                        f"White has {self.scoreBlack} black pieces captured and"
                        f"Has won {self.white_territory_final} territory (pieces placed on the board)\n\n"
                        f"Black has {self.scoreWhite} white pieces captured and"
                        f"Has won {self.black_territory_final} territory (pieces placed on the board)")
            # create box msg
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Game Over")
            msg_box.setInformativeText(gameOverMsg)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            # show box msg
            result = msg_box.exec()

            if result == QMessageBox.StandardButton.Ok:
                msg_box.close()

        except Exception as e:
            print(e)

    def howToPlay(self):
        try:
            # create box msg
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("How to Play Go")

            text = ("Go is a strategic board game for two players, originating in China. \n"
                    " The objective is to control more territory on the board than the opponent. \n"
                    "Players take turns placing stones (black and white) on empty intersections of the board.\n"
                    " Stones surround territories, and groups of stones can be captured if they run out of liberties.\n"
                    " The game ends when both players consecutively pass their turns (by pressing the 'pass turn' button),\n"
                    " and the winner is determined by controlled territory and captured stones.\n"
                    " You can reset the game by clicking 'reset game'\n"
                    " Each player has 120 seconds to make a move; if time runs out, the player loses.\n"
                    "Each stone captured by a player is worth 1.75 points, and each stone on the board is worth 1 point.\n"
                    "Clicking 'pass turn' twice ends the game, and the winner is determined along with each player's score.")

            # Use QTextDocument to apply styles to the text
            text_document = QTextDocument()
            text_document.setPlainText(text)
            text_html = text_document.toHtml()

            msg_box.setInformativeText(text_html)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: lightgray;
                    font: 20pt "Arial"; 
                    font-weight: bold; 
                }
                QPushButton {
                    background-color: lightblue;
                    margin: 10px;
                    font: 20pt "Arial"; 
                    font-weight: bold; 
                }
               QLabel {
                    background-color: none;
                    margin: 5px;
                    font: 20pt "Arial"; 
                    font-weight: bold; 
                }
            """)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            # show box msg
            result = msg_box.exec()

            # Aqui você pode adicionar mais lógica conforme necessário após o fechamento da caixa de mensagem
            if result == QMessageBox.StandardButton.Ok:
                msg_box.close()
        except Exception as e:
            print(e)




    # if click on pass turn button it will change the turn
    def reset(self):
        try:
            print('entrou no reset')
            self.board.boardArray = [[Balls(Piece.NoPiece, i, j) for i in range(Board.boardWidth)] for j in
                                     range(Board.boardHeight)]
            self.board.boardArray_int = [[0 for _ in range(self.board.boardWidth)] for _ in
                                         range(self.board.boardHeight)]
            self.board.isStarted = False
            self.board.white_score = 0
            self.board.black_score = 0
            self.board.white_territory_final = 0
            self.board.black_territory_final = 0
            self.scoreBlack = 0
            self.scoreWhite = 0
            self.label_black_score.setText(f'Black stone player:\nStones captured: {self.scoreBlack}')
            self.label_white_score.setText(f'White stone player:\nStones captured: {self.scoreWhite}')
            # self.board.printBoardArray()
            self.board.player_turn = 2
            # self.board.initBoard()
            self.board.changePieceX = 0
            self.board.changePieceY = 0
            self.board.black_score = 0
            self.board.white_score = 0

            self.board.resetGame()
            self.board.initBoard()
            self.update()
        except Exception as e:
            print(e)

    def passTurn(self):
        try:
            # variable to control how many times user pass
            # if pass 2 in row  then it's game over
            self.board.count_turn_passed += 1

            turn = self.board.player_turn
            print(f"truno : {turn}")
            '''updates the player turn label to show the current player turn'''
            player = ''
            next_turn_player = 0
            if turn == 1:
                player = 'White'
                next_turn_player = 2
                if self.scoreWhite > 0:
                    self.scoreWhite -= 1  # player looses 1 prisoner if pass his turn
                    # update lbl
                    self.label_white_score.setText(f'White stone player:\nStones captured: {self.scoreWhite}')

            elif turn == 2:
                player = 'black'
                next_turn_player = 1
                if self.scoreBlack > 0:
                    self.scoreBlack -= 1  # player looses 1 prisoner if pass his turn
                    # update lbl
                    self.label_black_score.setText(f'Black stone player:\nStones captured: {self.scoreBlack}')

            update = "Player Turn: " + str(player)
            self.label_player_turn.setText(update)
            self.player_turn = next_turn_player  # update instance variable player_turn
            self.board.changeTurn()
        except Exception as e:
            print(e)

    # change in the array object the element surrounded
    def changeStoneElementInArrayObject(self, x, y, stone_player):
        # print('entrou no change')
        try:
            obejctY = y
            obejctX = x
            # set to 0 (no piece) stone surranded
            self.board.updateArrays(obejctY, obejctX, stone_player)

            # print('passou por   board.alteraTest')
        except Exception as e:
            print(e)

    # Rules
    # It will check every game rule before place stone
    @pyqtSlot(object, int, int, int)
    def rules(self, boardArray_int, y, x, turn):
        # check if there's no stone placed
        if self.checkingStonePositionsBusy(boardArray_int, y, x):
            # check liberties around where was clicked
            # print(f" before checck funct  {self.checkLibertyBeforePlaceStone(boardArray_int, y, x, turn)}")
            if not self.checkLibertyBeforePlaceStone(boardArray_int, y, x, turn):
                if self.checkLiberty(boardArray_int, y, x, turn):
                    Board.positionBusy = 0
            else:
                print("you cant do that, inside rules")
                Board.positionBusy = 1
        else:
            print("not good")
            Board.positionBusy = 1

    @pyqtSlot(object, int, int, int)
    def checkLibertyForCatchStone(self, boardArray_int, y, x, turn):
        print('\n')

        # print(f'valor y = {y}, valor x = {x} Turn inicial {turn}')  # to delete

        # used to manipulate and check stone enemy, it will be necessary for researche in
        # checkLiberty, once it check if current player is suround by enemy, in this case I swap players
        def playerTurn(turns):
            if turns == 2:
                opponent = 1
                return opponent
            elif turns == 1:
                opponent = 2
                return opponent

        def is_within_bounds(i, j):
            return 0 <= i < 7 and 0 <= j < 7

        player_opponent = playerTurn(turn)
        # print(f'oponente {player_opponent}')  # to delete

        # Suicide Rule
        try:
            # Verifica a peça à direita
            if is_within_bounds(x + 1, y) and boardArray_int[y][x + 1] == player_opponent:
                # print("entrou, direita")  # to delete
                # If found it store the opponent position
                coordOpponentY = y
                coordOpponentX = x + 1
                # check using checkLiberty if Opponent piece is suround by the player who is current turn
                # The funtion will return false if he is sunround, meaning the current player has stones around
                # Opponent player stone
                # turn = playerTurn(player_opponent) #invert enemy to check if he is suround
                # print(f'oponente {turn}')  # to delete
                # print(f'valor a ser passado y = {coordOpponentY}, valor x = {coordOpponentX}')  # to delete
                opponentSuroundForCurrentPlayer = self.checkLiberty(boardArray_int, coordOpponentY, coordOpponentX,
                                                                    player_opponent)
                print(
                    f"temliberdade funtiont {self.tem_liberdades(boardArray_int, coordOpponentY, coordOpponentX, player_opponent)}")
                print(f"a direita: {opponentSuroundForCurrentPlayer}")  # to delete
                if not opponentSuroundForCurrentPlayer:
                    # playerScore+=1
                    # print(f"score 1 , direita")
                    if turn == 2:
                        color = (0, 0, 0)
                        stone_object = Piece.Black
                    else:
                        stone_object = Piece.White
                        color = (255, 255, 255)
                    # if stone is surround, remove the ellipse
                    target_location = (coordOpponentX - 1, coordOpponentY - 1)
                    target_dict = next(
                        (item for item in self.ellipseLocations if item.get('location') == target_location), None)
                    if (y, x) in self.ellipseLocations:
                        self.ellipseLocations.remove(target_dict)
                        self.addScore(turn, 1)

            # Verifica a peça abaixo
            if is_within_bounds(x, y + 1) and boardArray_int[y + 1][x] == player_opponent:
                # print("entrou, baixo")  # to delete
                # If found it store the opponent position
                coordOpponentY = y + 1
                coordOpponentX = x
                # check using checkLiberty if Opponent piece is suround by the player who is current turn
                # The funtion will return false if he is sunround, meaning the current player has stones around
                # Opponent player stone
                # turn = playerTurn(player_opponent)  # invert enemy to check if he is suround
                # print(f'oponente {turn}')  # to delete
                # print(f'valor a ser passado y = {coordOpponentY}, valor x = {coordOpponentX}')  # to delete
                opponentSuroundForCurrentPlayer = self.checkLiberty(boardArray_int, coordOpponentY, coordOpponentX,
                                                                    player_opponent)
                print(
                    f"temliberdade funtiont {self.tem_liberdades(boardArray_int, coordOpponentY, coordOpponentX, player_opponent)}")
                # print(f"a baixo: {opponentSuroundForCurrentPlayer}")  # to delete
                if not opponentSuroundForCurrentPlayer:
                    # playerScore+=1
                    # print(f"score 1 , baixo")  # TO DELETE
                    if turn == 2:
                        color = (0, 0, 0)
                        stone_object = Piece.Black
                    else:
                        stone_object = Piece.White
                        color = (255, 255, 255)
                    # if stone is surround, remove the ellipse
                    target_location = (coordOpponentX - 1, coordOpponentY - 1)
                    target_dict = next(
                        (item for item in self.ellipseLocations if item.get('location') == target_location), None)
                    if (y, x) in self.ellipseLocations:
                        self.ellipseLocations.remove(target_dict)
                        self.addScore(turn, 1)


            if is_within_bounds(x - 1, y) and boardArray_int[y][x - 1] == player_opponent:
                print("entrou, esquerda")  # to delete
                # If found it store the opponent position
                coordOpponentY = y
                coordOpponentX = x - 1
                # check using checkLiberty if Opponent piece is suround by the player who is current turn
                # The funtion will return false if he is sunround, meaning the current player has stones around
                # Opponent player stone
                # turn = playerTurn(player_opponent)  # invert enemy to check if he is suround
                # print(f'oponente {turn}')  # to delete
                # print(f'valor a ser passado y = {coordOpponentY}, valor x = {coordOpponentX}')  # to delete
                opponentSuroundForCurrentPlayer = self.checkLiberty(boardArray_int, coordOpponentY, coordOpponentX,
                                                                    player_opponent)
                print(
                    f"temliberdade funtiont----------- {self.tem_liberdades(boardArray_int, coordOpponentY, coordOpponentX, player_opponent)}")

                try:
                    if not opponentSuroundForCurrentPlayer:
                        # playerScore+=1
                        # print(f"score 1 , esquerda")
                        if turn == 2:
                            color = (0, 0, 0)
                            stone_object = Piece.Black
                        else:
                            stone_object = Piece.White
                            color = (255, 255, 255)
                        # if stone is surround, remove the ellipse
                        target_location = (coordOpponentX - 1, coordOpponentY - 1)
                        target_dict = next(
                            (item for item in self.ellipseLocations if item.get('location') == target_location), None)
                        if (y, x) in self.ellipseLocations:
                            self.ellipseLocations.remove(target_dict)
                            self.addScore(turn, 1)
                except Exception as e:
                    print(e)

            # Verifica a peça acima
            if is_within_bounds(x, y - 1) and boardArray_int[y - 1][x] == player_opponent:
                # print("entrou, cima")  # to delete
                # If found it store the opponent position
                coordOpponentY = y - 1
                coordOpponentX = x
                # check using checkLiberty if Opponent piece is suround by the player who is current turn
                # The funtion will return false if he is sunround, meaning the current player has stones around
                # Opponent player stone
                # turn = playerTurn(player_opponent)  # invert enemy to check if he is suround
                # print(f'oponente {turn}')  # to delete
                # print(f'valor a ser passado y = {coordOpponentY}, valor x = {coordOpponentX}')  # to delete
                print(
                    f"temliberdade funtiont {self.tem_liberdades(boardArray_int, coordOpponentY, coordOpponentX, player_opponent)}")
                opponentSuroundForCurrentPlayer = self.checkLiberty(boardArray_int, coordOpponentY,
                                                                    coordOpponentX, player_opponent)
                try:

                    if not opponentSuroundForCurrentPlayer:
                        # playerScore+=1
                        print(f"score 1 , cima")  # to delete
                        if turn == 2:
                            color = (0, 0, 0)
                            stone_object = Piece.Black
                        else:
                            stone_object = Piece.White
                            color = (255, 255, 255)
                        # if stone is surround, remove the ellipse
                        target_location = (coordOpponentX - 1, coordOpponentY - 1)
                        target_dict = next(
                            (item for item in self.ellipseLocations if item.get('location') == target_location),
                            None)
                        if (y, x) in self.ellipseLocations:
                            self.ellipseLocations.remove(target_dict)
                            self.addScore(turn, 1)
                except Exception as e:
                    print(e)

            else:
                print("chegou")  # to delete
                # print('kurwa')  # to delete
        except Exception as e:
            print(e)

    # Check liberty around where user clicks to validate a move
    # If the liberty around belong to opponent player, move is invalidate
    # The algorithm for check liberty:
    # the click event will send the y and x position where user click, y,x = point in the cartesian plan
    # the algorithm will check by increasing 1 and subtracting 1 from y and x, assuming y,x are greater then 0
    # the game rule does not allow a player place a stone if around that stone is surround to opposite players stone
    # so, if a player wants to place a stone on array (y2, x2) but in the array positions
    # (y2,x1), (y1,x2), (y2, x3) and (y3, x2) there are opposite player's stone,
    # the algorithm won't allow another stone been placed  in (y2, x2) for different player.
    # suicide rule
    def checkLiberty(self, boardArray_int, y, x, turn):
        player_turn = turn
        if player_turn == 2:
            player_opponent = 1
        else:
            player_opponent = 2
        # print(f"recebeu {y}, {x}, turno = {turn}, player_opponent = {player_opponent}")
        try:
            # check 4 directions
            if 0 < x < 6 and 0 < y < 6:
                if (boardArray_int[y][x + 1] == player_opponent
                        and boardArray_int[y][x - 1] == player_opponent
                        and boardArray_int[y + 1][x] == player_opponent
                        and boardArray_int[y - 1][x] == player_opponent):
                    return False
                else:
                    return True
            # 3 directions down, up and left
            elif x == 0 and 0 < y < 6:
                # print("checked 3 directions, down up left")  # to delete
                if (boardArray_int[y][x + 1] == player_opponent
                        and boardArray_int[y + 1][x] == player_opponent
                        and boardArray_int[y - 1][x] == player_opponent):
                    return False
                else:
                    return True
            # 3 directions down, right and left
            elif y == 0 and 0 < x < 6:
                # print("checked 3 directions, right, down, left")  # to delete
                if (boardArray_int[y][x + 1] == player_opponent
                        and boardArray_int[y][x - 1] == player_opponent
                        and boardArray_int[y + 1][x] == player_opponent):
                    return False
                else:
                    return True
            # 3 directions backwards down, up and left
            elif x == 6 and 0 < y < 6:
                # print("checked 3 directions, backward down, up, left ")  # to delete
                if (boardArray_int[y][x - 1] == player_opponent
                        and boardArray_int[y + 1][x] == player_opponent
                        and boardArray_int[y - 1][x] == player_opponent):
                    return False
                else:
                    return True
            # 3 directions backwards down, up and left
            elif y == 6 and 0 < x < 6:
                # print("checked 3 directions, backward down, up, left 2")  # to delete
                if (boardArray_int[y][x + 1] == player_opponent
                        and boardArray_int[y][x - 1] == player_opponent
                        and boardArray_int[y - 1][x] == player_opponent):
                    return False
                else:
                    return True
            # check 2 directions (stone placed in corners)
            # check down and right
            elif x == 0 and y == 0:
                # print(' x = 0, y = 0')
                if (boardArray_int[y][x + 1] == player_opponent
                        and boardArray_int[y + 1][x] == player_opponent):
                    return False
                else:
                    return True
            # check 2 directions
            elif x == 0 and y == 6:
                # print('x = 0, y = 6')  # to delete
                if (boardArray_int[y][x + 1] == player_opponent
                        and boardArray_int[y - 1][x] == player_opponent):
                    return False
                else:
                    return True
            # check 2 directions
            elif y == 0 and x == 6:
                # print('y = 0, x = 6')  # to delete
                if (boardArray_int[y + 1][x] == player_opponent
                        and boardArray_int[y][x - 1] == player_opponent):
                    return False
                else:
                    return True
            # check 2 directions
            elif y == 6 and x == 6:
                # print('y = 6, x = 6')  # to delete
                if (boardArray_int[y][x - 1] == player_opponent
                        and boardArray_int[y - 1][x] == player_opponent):
                    return False
                else:
                    return True
            else:
                return True

        except Exception as e:
            print(e)

    def checkingStonePositionsBusy(self, boardArray_int, y, x):
        try:
            if boardArray_int[y][x] == 0:
                print(f"Position ({y}, {x}) is not occupied")
                return True
            else:
                print(f"Position ({y}, {x}) is occupied")
                return False
        except Exception as e:
            print(f"Error checking position: {e}")

    def checkLibertyBeforePlaceStone(self, array, line, col, turn):
        arrayToVerify = []
        arrayAlreadyVerify = []
        print(f"line {line} col {col} turn {turn}")

        # 1 Iteraction receive coordY, coordX from method checkLibertyForCatchStone
        arrayToVerify.append((line, col))
        arrayAlreadyVerify.append((line, col))

        try:
            while len(arrayToVerify) > 0:
                # Remova a linha abaixo, pois você já está iterando sobre arrayToVerify no loop for
                # arrayToVerify.pop(0)

                for pair in arrayToVerify:
                    y, x = pair
                    print("liberdade, entrou!!!")  # to delete
                    if 0 <= x < 6:
                        # check right
                        if array[y][x + 1] == turn and array[y][x + 1] != 0 and (y, x + 1) not in arrayAlreadyVerify:
                            print(f"{y}, {x + 1} turn: {turn}")
                            arrayToVerify.append((y, x + 1))
                        elif array[y][x + 1] == 0 and x + 1 != col:
                            print("1 array[y][x + 1]")  # to delete
                            return False
                    if x == 6:
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0 and x != col:
                            print("2 array[y][x]")  # to delete
                            return False
                    if x > 0:
                        # check left
                        if array[y][x - 1] == turn and array[y][x - 1] != 0 and (y, x - 1) not in arrayAlreadyVerify:
                            print(f"{y}, {x - 1} turn: {turn}")
                            arrayToVerify.append((y, x - 1))
                        elif array[y][x - 1] == 0 and x - 1 != col:
                            print("3 array[y][x - 1] ")  # to delete
                            return False
                    elif x == 0:
                        # check left
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0 and x != col:
                            print("4 array[y][x]")  # to delete
                            return False
                    if 0 <= y < 6:
                        # check down
                        if array[y + 1][x] == turn and array[y + 1][x] != 0 and (y + 1, x) not in arrayAlreadyVerify:
                            print(f"{y + 1}, {x} turn: {turn}")
                            arrayToVerify.append((y + 1, x))
                        elif array[y + 1][x] == 0 and y + 1 != line:
                            print("5 array[y + 1][x] ")  # to delete
                            return False
                    if y == 6:
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0 and y != line:
                            print("6 array[y][x] ")  # to delete
                            return False
                    if y > 0:
                        if array[y - 1][x] == turn and array[y - 1][x] != 0 and (y - 1, x) not in arrayAlreadyVerify:
                            print(f"{y - 1}, {x} turn: {turn}")
                            arrayToVerify.append((y - 1, x))
                        elif array[y - 1][x] == 0 and y - 1 != line:
                            print("7  array[y - 1][x] ")  # to delete
                            return False
                    if y == 0:
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0 and y != line:
                            print("8 array[y][x] ")  # to delete
                            return False
                    if (y, x) not in arrayAlreadyVerify:
                        arrayAlreadyVerify.append((y, x))
                    if (y, x) in arrayToVerify:
                        arrayToVerify.remove((y, x))
        except Exception as e:
            print(e)

        return True

    def tem_liberdades(self, array, line, col, turn):
        arrayToVerify = []
        arrayAlreadyVerify = []

        # 1 Iteraction receive coordY, coordX from method checkLibertyForCatchStone
        arrayToVerify.append((line, col))
        print(len(arrayToVerify))
        try:
            while len(arrayToVerify) > 0:
                # Remova a linha abaixo, pois você já está iterando sobre arrayToVerify no loop for
                # arrayToVerify.pop(0)

                for pair in arrayToVerify:
                    y, x = pair

                    print("liberdade, entrou")  # to delete
                    if 0 <= x < 6:
                        # check right
                        if array[y][x + 1] == turn and array[y][x + 1] != 0 and (y, x + 1) not in arrayAlreadyVerify:
                            print(f"{y}, {x + 1} turn: {turn}")
                            print("1 array[y][x + 1]")  # to delete
                            arrayToVerify.append((y, x + 1))
                        elif array[y][x + 1] == 0:
                            print("1 array[y][x + 1]")  # to delete
                            return False
                    if x == 6:
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            print("1 array[y][x]")  # to delete
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0:
                            print("1 array[y][x]")  # to delete
                            return False
                    if x > 0:
                        # check left
                        if array[y][x - 1] == turn and array[y][x - 1] != 0 and (y, x - 1) not in arrayAlreadyVerify:
                            print(f"{y}, {x - 1} turn: {turn}")
                            print("2 array[y][x - 1] ")  # to delete
                            arrayToVerify.append((y, x - 1))
                        elif array[y][x - 1] == 0:
                            print("2 array[y][x - 1] ")  # to delete
                            return False
                    elif x == 0:
                        # check left
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            print("1 array[y][x]")  # to delete
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0:
                            print("1 array[y][x]")  # to delete
                            return False
                    if 0 <= y < 6:
                        # check down
                        if array[y + 1][x] == turn and array[y + 1][x] != 0 and (y + 1, x) not in arrayAlreadyVerify:
                            print(f"{y + 1}, {x} turn: {turn}")
                            print("3 array[y + 1][x] ")  # to delete
                            arrayToVerify.append((y + 1, x))
                        elif array[y + 1][x] == 0:
                            print("3 array[y + 1][x] ")  # to delete
                            return False
                    if y == 6:
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            print("3 array[y][x] ")  # to delete
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0:
                            print("3 array[y][x] ")  # to delete
                            return False
                    if y > 0:
                        if array[y - 1][x] == turn and array[y - 1][x] != 0 and (y - 1, x) not in arrayAlreadyVerify:
                            print(f"{y - 1}, {x} turn: {turn}")
                            print("2  array[y - 1][x] ")  # to delete
                            arrayToVerify.append((y - 1, x))
                        elif array[y - 1][x] == 0:
                            print("2  array[y - 1][x] ")  # to delete
                            return False
                    if y == 0:
                        if array[y][x] == turn and array[y][x] != 0 and (y, x) not in arrayAlreadyVerify:
                            print(f"{y}, {x} turn: {turn}")
                            print("3 array[y][x] ")  # to delete
                            arrayToVerify.append((y, x))
                        elif array[y][x] == 0:
                            print("3 array[y][x] ")  # to delete
                            return False
                    if (y, x) not in arrayAlreadyVerify:
                        arrayAlreadyVerify.append((y, x))
                    if (y, x) in arrayToVerify:
                        arrayToVerify.remove((y, x))
        except Exception as e:
            print(e)
        print("saiu liberdades")
        self.clearElipseUpdateArrays(array, arrayAlreadyVerify)
        return True

    # it must clear elipses drawed and update arrays in case true
    def clearElipseUpdateArrays(self, boardArray_int, coordsToRemove):
        scoreForCapture = len(coordsToRemove)
        # In case return true, means there's a stone surrunded
        try:
            for pair in coordsToRemove:
                y, x = pair
                print(f"y: {y}, x: {x}")
                target_location = (x - 1, y - 1)
                # if stone is surround, remove the ellipse
                target_dict = next(
                    (item for item in self.ellipseLocations if item.get('location') == target_location), None)

                self.ellipseLocations.remove(target_dict)
                # update object array with 0 where it is surrounded
                stone_player = 2
                self.changeStoneElementInArrayObject(y, x, stone_player)
                # update copy array with 0 where it is surrounded
                boardArray_int[y][x] = 0
        except Exception as e:
            print(e)
        turn = self.board.player_turn
        self.addScore(turn, scoreForCapture)

    @pyqtSlot(str)  # checks to make sure that the following slot is receiving an argument of the type 'int'
    def setClickLocation(self, clickLoc):
        '''updates the label to show the click location'''
        self.label_clickLocation.setText("Click Location: " + clickLoc)
        # print('slot ' + clickLoc)

    @pyqtSlot(int, int)
    def setTimeRemaining(self, timeRemainingB, timeRemainingW):
        try:
            '''updates the time remaining label to show the time remaining'''
            update = "Time Remaining\n Black stone: " + str(timeRemainingB)
            self.label_timeRemainingB.setText(update)

            update2 = "Time Remaining\n White stone: " + str(timeRemainingW)
            self.label_timeRemainingW.setText(update2)
        except Exception as e:
            print(e)

    @pyqtSlot(int)
    def setTurn(self, turn):
        try:
            # print(turn)
            '''updates the player turn label to show the current player turn'''
            player = ''
            next_turn_player = 0
            if turn == 1:
                player = 'White'
                next_turn_player = 2

            elif turn == 2:
                player = 'black'
                next_turn_player = 1
            # check if ko rule is activity
            if Board.ko_rule_variable[0]:  # if True
                # if it is activied and the player who activied is playing again
                # then the rule will be desability
                if Board.ko_rule_variable[3] == turn:
                    self.koRule(False)

            update = "Player Turn: " + str(player)
            self.label_player_turn.setText(update)
            self.player_turn = next_turn_player  # update instance variable player_turn
            # print('slot1 ' + str(player))
        except Exception as e:
            print(e)

    def koRule(self, debilitated):
        if not debilitated:  # if korule = False
            Board.ko_rule_variable[0] = False
            Board.ko_rule_variable[1] = -1
            Board.ko_rule_variable[2] = -1
            Board.ko_rule_variable[3] = -1

    def addScore(self, turn, score):
        # 1 - white stone
        if turn == 1:
            # store score in the variable
            self.scoreWhite += score
            # change the label for score using the variable
            self.label_white_score.setText(f'White stone player:\nStones captured: {self.scoreWhite}')
            stone_player = 1
            # make stone surround = 0 and apply KO rule
            # self.changeStoneElementInArrayObject(y, x, stone_player)
        else:
            # store score in the variable
            self.scoreBlack += score
            # change the label for score using the variable
            self.label_black_score.setText(f'Black stone player: \nStones captured: {self.scoreBlack}')
            stone_player = 2
            # make stone surround = 0 and apply KO rule
            # self.changeStoneElementInArrayObject(y, x, stone_player)
        # self.redraw()

    def finalScore(self):
        # 1,75 because I could not calculate empty elements in the array, i'm giving extra points for capture
        self.white_final_score = self.scoreWhite * 1.75 + self.board.white_territory_final
        self.black_final_score = self.scoreBlack * 1.75 + self.board.black_territory_final
        print(self.board.white_territory_final)
