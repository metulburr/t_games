"""
backgammon_test.py

Unit testing for backgammon_game.py.

Classes:
MoveTest: Test move generation. (TestCase)
"""


import unittest

from tgames.board_games import backgammon_game as bg


class MoveTest(unittest.TestCase):
    """Test move generation. (TestCase)"""

    def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O', 
        rolls = [6, 5], bar = None):
        """Set up the board for a test. (None)"""
        self.board = bg.BackgammonBoard(layout = layout)
        if bar:
            self.board.bar.piece = bar
        for start, end in moves:
            self.board.move(start, end)
        raw_moves = self.board.get_moves(piece, rolls)
        self.legal_moves = set(tuple(move) for move in raw_moves)

    @unittest.skip('Test planned but not written.')
    def testBear(self):
        """Test bearing off moves."""
        pass

    @unittest.skip('Test planned but not written.')
    def testBearOver(self):
        """Test bearing off with over rolls."""
        pass

    @unittest.skip('Test planned but not written.')
    def testBearPartial(self):
        """Test bearing off with empty point rolled."""
        pass

    def testDoubles(self):
        """Test moves with doubles."""
        self.setBoard(layout = ((24, 1), (23, 1), (22, 1)), rolls = [1, 1, 1, 1])
        check = [(((0,), (1,)), ((1,), (2,)), ((1,), (2,)), ((2,), (3,))), 
            (((0,), (1,)), ((1,), (2,)), ((2,), (3,)), ((2,), (3,))), 
            (((0,), (1,)), ((1,), (2,)), ((2,), (3,)), ((3,), (4,))), 
            (((0,), (1,)), ((2,), (3,)), ((3,), (4,)), ((4,), (5,))), 
            (((1,), (2,)), ((2,), (3,)), ((2,), (3,)), ((3,), (4,))), 
            (((1,), (2,)), ((2,), (3,)), ((3,), (4,)), ((4,), (5,))), 
            (((2,), (3,)), ((3,), (4,)), ((4,), (5,)), ((5,), (6,)))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    @unittest.skip('Test planned but not written.')
    def testEnter(self):
        """Test moves from the bar."""
        pass

    @unittest.skip('Test planned but not written.')
    def testEnterBlock(self):
        """Test moves from the bar with some moves blocked."""
        pass

    def testEnterNone(self):
        """Test moves from the bar when none are legal."""
        self.setBoard(layout = ((18, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (1, 2)), rolls = [6, 6], 
            bar = ['X', 'O'])
        self.assertEqual(set(), self.legal_moves)

    def testNone(self):
        """Test a situation with no legal moves."""
        self.setBoard(layout = ((7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2), (24, 2)), rolls = [6, 6])
        self.assertEqual(set(), self.legal_moves)

    @unittest.skip('Test planned but not written.')
    def testPartial(self):
        """Test moves where only part of the move is legal."""
        pass

    def testStart(self):
        """Test the moves at the start of the game."""
        self.setBoard()
        check = [(((11,), (16,)), ((0,), (6,))), (((11,), (16,)), ((11,), (17,))), 
            (((11,), (16,)), ((16,), (22,))), (((16,), (21,)), ((0,), (6,))), 
            (((16,), (21,)), ((11,), (17,))), (((16,), (21,)), ((16,), (22,))), 
            (((0,), (6,)), ((6,), (11,))), (((11,), (17,)), ((17,), (22,)))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)

    def testStartBlock(self):
        """Test the starting moves with a simple block."""
        self.setBoard(moves = [((12,), (6,)), ((7,), (6,))])
        check = [(((11,), (16,)), ((11,), (17,))), (((11,), (16,)), ((16,), (22,))), 
            (((16,), (21,)), ((11,), (17,))), (((16,), (21,)), ((16,), (22,))), 
            (((11,), (17,)), ((17,), (22,)))]
        check = set(check)
        self.assertEqual(check, self.legal_moves)


if __name__ == '__main__':
    unittest.main()