import numpy as np
import ColorBoard as cb
import time
import copy
import operator

class BoardSolver(object):
  def __init__(self, graph_dict, node_info, attached=[0]):
    self.graph = graph_dict
    self.node_info = node_info
    self.attached = attached

  def solve(self, max_depth, max_threads, moves_between_eval=1):
    self.max_depth = max_depth
    self.max_threads = max_threads
    self.completed = False
    self.moves_between_eval = moves_between_eval
    start_time = time.time()
    self.brute(self.graph, self.attached, depth=0, eval_depth=1)
    print 'Done in:', time.time() - start_time
    if self.completed:
      print self.max_depth, 'moves to completion'
    else:
      print 'Not completed'

  def brute(self, graph, attached, depth, eval_depth):
    if depth == self.max_depth:
      return -1

    if graph.empty:
      if depth < self.max_depth:
        self.max_depth = depth
        self.completed = True
        return -2

    if eval_depth == 0:
      return self.eval(graph, attached)

    adjacent_nodes = graph.adjacent[graph.node.isin(attached)]
    available_colors = self.node_info.color[self.node_info.node.isin(adjacent_nodes)]
    print available_colors.tolist()
    print adjacent_nodes.tolist()

    scores = {}
    for color in available_colors:
      correct_color_nodes = self.node_info.node[self.node_info.color == color]
      matched_nodes = correct_color_nodes[correct_color_nodes.isin(adjacent_nodes)]
      new_graph = graph[graph.adjacent.isin(matched_nodes) == False]
      new_attached = attached + matched_nodes.tolist()
      scores[color] = self.brute(new_graph, new_attached, depth + 1, eval_depth - 1)

    print scores

    if -2 in scores.values():
      return

    color = max(scores.iteritems(), key=operator.itemgetter(1))[0]
    correct_color_nodes = self.node_info.node[self.node_info.color == color]
    matched_nodes = correct_color_nodes[correct_color_nodes.isin(adjacent_nodes)]
    new_graph = graph[graph.adjacent.isin(matched_nodes) == False]
    new_attached = attached + matched_nodes.tolist()
    self.brute(new_graph, new_attached, depth + 1, self.moves_between_eval)


  def eval(self, graph, attached):
    adjacent_nodes = graph.adjacent[graph.node.isin(attached)]
    return adjacent_nodes.count()


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
