import numpy as np
import pandas as pd

class Board(object):
  def __init__(self,board_x=None, n_colors=None, board=None):

    if board is None:
      color_samples = np.random.randint(1,n_colors + 1,size = board_x * board_x)
      self.board = np.asarray(color_samples).reshape((board_x,board_x))
      self.board_x = board_x
    else:
      self.board = board
      self.board_x = self.board.shape[0]

    self.build_nodes()
    self.build_edges()

    self.attach([0])

  @property
  def matched(self):
    return self.attached.sum()

  @property
  def remaining_colors(self):
    return list(np.unique(self.board))

  @property
  def current_color(self):
    return int(self.board[0,0])

  @property
  def is_complete(self):
    if len(self.remaining_colors) == 1:
      return True
    return False

  def attach(self,nodelist):
    if not hasattr(self,'attached_nodes'):
      self.attached_nodes = nodelist
    else:
      self.attached_nodes += nodelist

    self.touched_nodes = self.graph.node[self.graph.adjacent.isin(nodelist)]
    self.graph = self.graph[self.graph.adjacent.isin(nodelist) == False]

  def take_turn(self,color):
    if color == self.current_color:
      return

    correct_color_nodes = self.node_info.node[self.node_info.color == color]
    #print 'right colored nodes', correct_color_nodes.tolist()
    #print 'touched_nodes', self.touched_nodes
    matched_nodes = self.touched_nodes[self.touched_nodes.isin(correct_color_nodes)]
    #print matched_nodes.tolist()
    matched_nodes = matched_nodes.tolist()
    self.attach(matched_nodes)

    mask = np.equal(self.nodes, self.attached_nodes[0])


    #print mask

    for node in self.attached_nodes:
      mask = np.logical_or(np.equal(self.nodes, node), mask)

    #print mask

    inv_mask = np.logical_not(mask)

    self.board = self.board * inv_mask #turn matched nodes to zero
    self.board = self.board + (mask * color)




  def get_adjacent(self, position):
    x,y = position
    xs = []
    ys = []

    if x > 0:
      xs.append(x - 1)
    if x < self.board_x - 1:
      xs.append(x + 1)

    if y > 0:
      ys.append(y - 1)
    if y < self.board_x - 1:
      ys.append(y + 1)

    adjacent = []
    for coord in xs:
      adjacent.append([coord,y])

    for coord in ys:
      adjacent.append([x,coord])

    return adjacent

  def build_nodes(self):
    self.edges = []
    self.nodes = np.ones((self.board.shape)).astype(int) * -1
    indices = np.where(self.nodes == -1)
    x,y = indices
    indices = zip(x,y)
    next_node = 0
    node_info = []
    while indices != []:
      x,y = indices[0]
      node_info.append((next_node,self.board[x,y]))
      self.node_traverse(indices[0], next_node, self.board[x,y])
      indices = np.where(self.nodes == -1)
      x,y = indices
      indices = zip(x,y)
      next_node += 1
    self.n_nodes = next_node
    self.node_info = pd.DataFrame.from_records(data=node_info, columns=['node','color'])

  def node_traverse(self,position,node_num,color):
    #var = raw_input('Press Enter')
    #print position, node_num, color
    x,y = position

    if self.nodes[x,y] != -1:
      #print 'i have been set'
      return 1

    if self.board[x,y] == color:
      #print 'i match'
      self.nodes[x,y] = node_num
    else:
      #print 'not a match'
      self.edges.append(tuple(position))
      return -1

    adjacent = self.get_adjacent(position)
    edge_values = []
    for adj in adjacent:
      edge_values.append(self.node_traverse(adj,self.nodes[x,y],color))
    if -1 in edge_values:
      self.edges.append(tuple(position))

  def build_edges(self):
    graph = []
    for position in set(self.edges):
      x,y = position
      node = self.nodes[x,y]
      color = self.board[x,y]
      adjacent = self.get_adjacent(position)
      for adj in adjacent:
        adj_x, adj_y = adj
        adj_node = self.nodes[adj_x,adj_y]
        if node != adj_node:
          graph.append((node, adj_node))
    graph = list(set(graph))
    self.graph = pd.DataFrame.from_records(data=graph,columns=['node','adjacent'])
