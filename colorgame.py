import ColorBoard2 as cb
from optparse import OptionParser
import sys

def main():
  user_pass = " ".join(sys.argv)
  parser = OptionParser()

  parser.add_option("-b","--boardsize", dest="board_size", type="int", help="Length of 1 side of the board", default=10)
  parser.add_option("-c","--colors", dest="n_colors", type="int", help="Number of colors to use", default=5)

  (opt, args) = parser.parse_args()

  good_board = 0
  while good_board == 0:
    board = cb.Board(board_x=opt.board_size,n_colors=opt.n_colors)
    if not board.is_complete:
      good_board = 1

  turn = 0
  while not board.is_complete:
    print board.board
    input = raw_input("Enter a color or exit):")
    if input == 'exit':
      return
    board.take_turn(int(input))
    turn += 1

  print 'Board Completed in ', turn, 'turns!'

if __name__ == '__main__':

	try:
		main()

	finally:
		print 'Done'
