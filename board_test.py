"""
board_test.py

Unit testing of board.py.

Classes:
BoardCellTest: Tests of the board cell class. (TestCase)
"""


import unittest

import tgames.board as board


class BoardCellTest(unittest.TestCase):
	"""Tests of the board cell class. (TestCase)"""

	def setUp(self):
		self.cell = board.BoardCell('here', 'piece')

	def testContains(self):
		"""Test the in operator for BoardCell."""
		self.assertTrue('piece' in self.cell)

	def testContainsNot(self):
		"""The failure of the in operator for BoardCell."""
		self.assertFalse('p' in self.cell)

	def testHash(self):
		"""Test for the expected hash of a BoardCell."""
		self.assertEqual(hash('here'), hash(self.cell))

	def testHashEquals(self):
		"""Test for the same has for two BoardCells with the same location."""
		test_cell = board.BoardCell('here', 'knight')
		self.assertEqual(hash(test_cell), hash(self.cell))


if __name__ == '__main__':
	unittest.main()