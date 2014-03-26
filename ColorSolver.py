import numpy as np
import ColorBoard as cb
import time
import copy
import operator

class BoardSolver(object):
  def __init__(self, board=None, board_x=None,n_colors=None ):
    if board is None:
      self.board = cb.Board(board_x=board_x,n_colors=n_colors)
    else:
      self.board = cb.Board(board=board)

  def solve(self, max_depth, eval_depth, paths, type='brute'):
    self.max_depth = max_depth
    self.eval_depth = eval_depth
    self.completed = False
    start_time = time.time()
    self.brute(copy.deepcopy(self.board), 0, paths, self.board.matched)
    print 'Done in:', time.time() - start_time
    if self.completed:
      print self.max_depth, 'moves to completion'
    else:
      print 'Not completed'

  def brute(self, board, depth, paths, prior_matches):
    #If our new configuration isn't better than the last (more matched squares) return
    if depth > 0:
      if board.matched == prior_matches:
        #print 'not improved'
        return

    #If we have more colors left than turns before we hit the max, return
    if depth > self.max_depth - len(board.remaining_colors):
      #print 'not enough moves left'
      return

    # If the board is complete, and the number of moves is better than the last try,
    # reset max_depth. Return.
    if board.is_complete:
      #print 'completed', depth
      self.completed = True
      if depth < self.max_depth:
        self.max_depth = depth
      return

    colors = set(board.remaining_colors) - set([board.current_color])
    matched = board.matched

    for c in colors:
      b = cb.Board(board=board.board)
      b.take_turn(c)
      self.brute(b, depth + 1, paths, matched)

  def eval(self, board, depth, sequence, prior_matches):
    if board.matched == prior_matches:
      #print 'not improved'
      return [(sequence, 0)]

    # If the board is complete, and the number of moves is better than the last try,
    # reset max_depth. Return.
    if board.is_complete:
      #print 'completed', depth
      self.completed = True
      if depth < self.max_depth:
        self.max_depth = depth
      return [(sequence, 1000)]

    if depth == self.eval_depth:
      return [(sequence, board.matched - prior_matches)]

    moves = []

    colors = board.remaining_colors
    for c in colors:
      c_seq = [x for x in sequence]
      c_seq.append(c)
      b = cb.Board(board=board.board)
      b.take_turn(c)
      moves = moves + self.eval(b, depth + 1, c_seq, prior_matches)

    return moves


  def dumb(self, board, depth):
    if board.is_complete:
      return depth

    depths = []

    move_size = {}
    for c in board.remaining_colors:
      b = cb.Board(board=board.board)
      b.take_turn(c)
      b.traverse((0,0),c)
      move_size[c] = b.tf_board.sum()

    biggest = max(move_size, key=move_size.get)

    depths.append(self.brute(b, depth + 1))

    return min(depths)
