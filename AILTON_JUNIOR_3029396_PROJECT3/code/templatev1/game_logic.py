from balls import Balls
from PyQt6.QtCore import pyqtSlot


class GameLogic:
    array = []

    def __init__(self):
        self.player_turn = 2

    def make_connection(self, board):
        '''this handles a signal sent from the board class'''
        # when the checkStonePosition is emitted in board the setClickLocation slot receives it
        print("get it ==========================")
        board.checkStonePosition.connect(self.checkingStonePositionsBusy)

