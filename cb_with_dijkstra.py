import numpy as np
import pandas as pd
import heapq as hq
import copy

class Board(object):
  def __init__(self,board_x=None, n_colors=None, board=None, dim=2):

    if board is None:
      color_samples = np.random.randint(1,n_colors + 1,size = board_x ** dim)
      board_specs = []
      self.dim = dim
      for i in range(dim):
        board_specs.append(board_x)
      self.board = np.asarray(color_samples).reshape(board_specs)
      self.board_x = board_x
    else:
      self.board = board
      self.board_x = self.board.shape[0]

    self.build_nodes()
    self.build_edges()
    self.build_collapsed_edges()
    self.dijkstra()

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
      self.attached_nodes.append(nodelist)

    self.touched_nodes = self.graph.node[self.graph.adjacent.isin(nodelist)]
    self.graph = self.graph[self.graph.adjacent.isin(nodelist) == False]

  def take_turn(self,color):
    if color == self.current_color:
      return

    correct_color_nodes = self.node_info.node[self.node_info.color == color]
    matched_nodes = self.touched_nodes.node[self.touched_nodes.node.isin(correct_color_nodes)]

    self.attach(matched_nodes.tolist())

  def get_adjacent(self, position):
    x = position
    s = {}
    for i in range(len(x)):
      s[i] = []

    for i in range(len(x)): # For each dimension of the board we add to s a list of coordinates to check that are in the range of the board's width.
      if x[i] > 0:
        s[i].append(x[i] - 1)
      if x[i] < self.board_x - 1:
        s[i].append(x[i] + 1)

    adjacent = []
    for dim, sp in s.iteritems():
      for coord in sp:
        all_coord_pre = []
        for i in range(len(x)):
          if i != dim: # For all dimensions of x other than the dimension we are changing, the coordinate values are the same.
            all_coord_pre.append(x[i])
          else:
            all_coord_pre.append(coord) # For the dimensions of x  we are changing, the new coordinate values are used.
        adjacent.append(all_coord_pre)

    return adjacent

  def build_nodes(self):
    self.edges = []
    self.nodes = np.ones((self.board.shape)).astype(int) * -1
    indices = np.where(self.nodes == -1)
    x = []
    for i in range(len(indices)):
      x.append(indices[i])

    indices = zip(*x) # This is a nifty way of zipping all the items of a list
    next_node = 0
    node_info = []
    while indices != []:
      x = indices[0]
      node_info.append((next_node,self.board[x]))
      self.node_traverse(indices[0], next_node, self.board[x])
      indices = np.where(self.nodes == -1)
      x = []
      for i in range(len(indices)):
        x.append(indices[i])
      indices = zip(*x)
      next_node += 1
    self.n_nodes = next_node
    self.node_info = pd.DataFrame.from_records(data=node_info, columns=['node','color'])
    self.node_info_dict = {}
    for index, val in self.node_info.iterrows():
      self.node_info_dict[index] = val.color

  def node_traverse(self,position,node_num,color):
    #var = raw_input('Press Enter')
    ## print position, node_num, color
    x = position

    if self.nodes[tuple(x)] != -1:
      ## print 'i have been set'
      return 1

    if self.board[tuple(x)] == color:
      ## print 'i match'

      self.nodes[tuple(x)] = int(node_num)
    else:
      ## print 'not a match'
      self.edges.append(tuple(x))
      return -1
    adjacent = self.get_adjacent(position)
    edge_values = []
    for adj in adjacent:
      edge_values.append(self.node_traverse(adj,self.nodes[tuple(x)],color))
    if -1 in edge_values:
      self.edges.append(tuple(position))

  def build_edges(self):
    graph = []
    for position in set(self.edges):
      x = position

      node = self.nodes[tuple(x)]
      color = self.board[tuple(x)]
      adjacent = self.get_adjacent(position)
      for adj in adjacent:
        adj_node = self.nodes[tuple(adj)]
        if node != adj_node:
          graph.append((node, adj_node))
    graph = list(set(graph))
    self.graph = pd.DataFrame.from_records(data=graph,columns=['node','adjacent'])

  def build_collapsed_edges(self):
    self.collapsed_edges = {}
    for node in self.graph.node.unique():
      self.collapsed_edges[node] = {}
      self.collapsed_edges[node]['all_colors'] = set()
      all_adj = set(self.graph.adjacent[self.graph.node == node])
      for adj in all_adj:
        adj_col = int(self.node_info.color[self.node_info.node == adj])
        if adj_col not in self.collapsed_edges[node].keys():
          self.collapsed_edges[node][adj_col] = set()
        self.collapsed_edges[node][adj_col].add(adj)
        self.collapsed_edges[node]['all_colors'].add(adj)

  def dijkstra(self):
    self.distances = {} # Minimum distance values given a key of initial_node and subsequent_node
    self.threads = {} # A set of minimal threads given a key of initial_node and subsequent_node
    for initial_node in self.collapsed_edges.keys():
      self.distances[initial_node] = {}
      self.threads[initial_node] = {}
      unvisited = set()
      # We use a heap structure to keep track of a priority queue such that nodes with the smallest tentative distance among those remaining are at the top of the heap
      # The first value of the tuple is the tentative distance (used for sorting), and the second value of the tuple is the node index.
      priority_queue = [(0, initial_node)] 
      for subsequent_node in self.graph.node.unique():
          self.threads[initial_node][subsequent_node] = set()
          unvisited.add(subsequent_node) # To start, all nodes are unvisited
          # To start, the tentative distance values of all nodes except the starting node are infinite
          if subsequent_node != initial_node:
            self.distances[initial_node][subsequent_node] = float("inf") 
          else:
            self.distances[initial_node][subsequent_node] = 0
      while len(unvisited) > 0: # So long as we have unvisited nodes we continue the algorithm
        current_selection = hq.heappop(priority_queue)
        current_node = current_selection[1]
        if current_node in unvisited:
          unvisited.remove(current_node)
          current_distance = current_selection[0]
          current_threads = self.threads[initial_node][current_node]
          check_neighbors = self.collapsed_edges[current_node]['all_colors'].intersection(unvisited) # All visited neighbors already have their absolute minimum distance values given
          for neighbor in check_neighbors:
            tentative_distance = self.distances[initial_node][neighbor]
            if current_distance + 1 <= tentative_distance: # This is a unique case of dijkstra's algorithm in that the edge distance is always 1.
              neighbor_color = self.node_info_dict[neighbor]
              if current_distance + 1 < tentative_distance: # If this new way of arriving at the neighboring node is better than before, any stored threads are erased, the distance value is updated and a new entry is added to the priority queue. 
                self.threads[initial_node][neighbor] = set()
                self.distances[initial_node][neighbor] = current_distance + 1 
                hq.heappush(priority_queue, (current_distance + 1, neighbor))
              if len(current_threads) == 0: # This is the case only for the starting node.
                self.threads[initial_node][neighbor].add(tuple([neighbor_color]))
              else:
                for add_thread in current_threads: # For each minimal thread from the initial to the current node, we extend the thread by adding the neighbor_color and add it to the set of minimal threads from the initial node to the neighboring node.
                  add_thread += tuple([neighbor_color])
                  self.threads[initial_node][neighbor].add(add_thread)
            
          

# b = Board(10,5,None,3)  