import ColorBoard as cb
import ColorSolver as cs
from optparse import OptionParser
import sys, os
import numpy as np

def main():
  user_pass = " ".join(sys.argv)
  parser = OptionParser()

  parser.add_option("--create",dest="create", action="store_true", help="Create Boards & Save them to the Directory", default=False)
  parser.add_option("-n","--num_boards", dest="n_boards", type="int", help="Number of boards to create", default=10)
  parser.add_option("-d","--directory", dest="dir", type="str", help="Location of Saved Boards (or where to write the boards)", default='./')
  parser.add_option("-b","--boardsize", dest="board_size", type="int", help="Length of 1 side of the board", default=10)
  parser.add_option("-c","--colors", dest="n_colors", type="int", help="Number of colors to use", default=4)
  parser.add_option("-m","--max_moves", dest="max_moves", type="int", help="Maximum number of moves to test per recursion", default=10)
  parser.add_option("-e","--eval_depth", dest="eval_depth", type="int", help="Maximum number of moves to pre-check", default=2)
  parser.add_option("-p","--paths", dest="paths", type="int", help="Maximum number of paths to explore after eval", default=1)


  (opt, args) = parser.parse_args()

  if opt.create:
    for n in range(opt.n_boards):
      good_board = 0
      while good_board == 0:
        board = cb.Board(board_x=opt.board_size,n_colors=opt.n_colors)
        if not board.is_complete:
          good_board = 1
      print 'board created'
      np.save(os.path.join(opt.dir,'board' + str(n)), board.board)
  else:
    for n in range(opt.n_boards):
      board = np.load(os.path.join(opt.dir,'board' + str(n) +'.npy'))
      solver = cs.BoardSolver(board=board)
      solver.solve(opt.max_moves, opt.eval_depth, opt.paths)

if __name__ == '__main__':

	try:
		main()

	finally:
		print 'Done'
