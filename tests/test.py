import sys
sys.path.append('../')
import foofah_libs.operators as Operations
from foofah_libs.operators import add_ops
from foofah_libs.generate_prog import create_python_prog
import uuid
from foofah import a_star_search, reconstruct_path
import os
from timeit import default_timer as timer
import time
import json
import argparse

DEBUG_LEVEL = 0
TIMEOUT = 70
EPSILON = 1
BOUND = float("inf")

ALGO_BFS = 0
ALGO_A_STAR = 1
ALGO_A_STAR_NAIVE = 2
ALGO_AWA = 3

def unit_test(file_name, search_algo, if_batch, p1off, p2off, p3off):
  test_data = None
  with open(file_name, 'rb') as f:
    test_data = json.load(f)

  source = [map(str, x) for x in test_data['InputTable']]
  target = [map(str, x) for x in test_data['OutputTable']]
  test_table = [map(str, x) for x in test_data['TestingTable']]
  test_answer = [map(str, x) for x in test_data['TestAnswer']]

  final_node = None
  open_nodes = None
  closed_nodes = None

  # Synthesis starts
  start = timer()

  if search_algo == ALGO_BFS:
    final_node, open_nodes, closed_nodes = a_star_search(raw_data = source, target = target, ops = add_ops(), debug = DEBUG_LEVEL,
                                                         timeout = TIMEOUT, batch = if_batch, algo = search_algo,
                                                         p1 = not p1off, p2 = not p2off, p3 = not p3off)

  elif search_algo == ALGO_A_STAR:
    final_node, open_nodes, closed_nodes = a_star_search(raw_data = source, target = target, ops =  add_ops(), debug = DEBUG_LEVEL,
                                                         timeout = TIMEOUT, batch = if_batch, epsilon = EPSILON,
                                                         bound = BOUND, algo = search_algo, p1 = not p1off,
                                                         p2 = not p2off,
                                                         p3 = not p3off)

  elif search_algo == ALGO_A_STAR_NAIVE:
    final_node, open_nodes, closed_nodes = a_star_search(raw_data = source, target = target, ops = add_ops(), debug = DEBUG_LEVEL,
                                                         timeout = TIMEOUT, batch = if_batch, epsilon = EPSILON,
                                                         bound = BOUND, algo = search_algo, p1 = not p1off,
                                                         p2 = not p2off,
                                                         p3 = not p3off)
  end = timer()
  path = reconstruct_path(final_node)

  actual_steps = []
  h_steps = []
  states = []

  program = create_python_prog(path, source)

  for i, n in enumerate(reversed(list(path))):
      remaining_steps = len(path) - i - 1
      actual_steps.append(remaining_steps)
      h_steps.append(n.get_h_score())
      states.append(n.contents)

  num_visited = len(closed_nodes)
  nodes_created = open_nodes.qsize() + len(closed_nodes)


  # Verify that the synthesize program is "perfect"
  try:
    for i, node in enumerate(reversed(path)):
      if i > 0:
        op = node.operation[0]
        if op['num_params'] == 1:
            test_table = op['fxn'](test_table)
        else:
            test_table = op['fxn'](test_table, node.operation[1])

  except:
      test_table = None

  # We synthesized a perfect program
  if len(path) > 0 and test_table == test_answer:
    return end - start

  # We synthesized a wrong program
  elif len(path) > 0:
    return -1

  # We get a timeout
  else:
    return -2

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--test_dir', type=str, default='data', help="Directory that contains all the test files")
  parser.add_argument('--output', type=str, default='foofah_batch.csv', help="File name of the result")
  parser.add_argument('--search_algo', type=int, default=1,
                        help="Searh algorithm: 0 = BFS, 1 (default) = A*, 2 = naive heuristic")
  parser.add_argument('--no_batch', action='store_true', default=False, help="Disable batch")
  parser.add_argument('--globalPruneOff', action='store_true', default=False, help="turn off global pruning rules")
  parser.add_argument('--opPruneOff', action='store_true', default=False, help="turn off operator pruning rules")

  parser.add_argument('--wrap1off', action='store_true', default=False, help="turn off 1st wrap operator")
  parser.add_argument('--wrap2off', action='store_true', default=False, help="turn off 2nd wrap operator")
  parser.add_argument('--wrap3off', action='store_true', default=False, help="turn off 3rd wrap operator")


  args = parser.parse_args()
  test_dir = args.test_dir
  output_file = args.output
  search_algo = args.search_algo
  if_batch = not args.no_batch
  op_prune_off = args.opPruneOff

  wrap1off = args.wrap1off
  wrap2off = args.wrap2off
  wrap3off = args.wrap3off

  p1off = False
  p2off = False
  p3off = False

  if op_prune_off:
      Operations.PRUNE_1 = False

  if wrap1off:
      Operations.WRAP_1 = False
  
  if wrap2off:
      Operations.WRAP_2 = False
  
  if wrap3off:
      Operations.WRAP_3 = False

  global_prune_off = args.globalPruneOff

  if global_prune_off:
      p1off = True
      p2off = True
      p3off = True



  test_result = {}

  start = timer()

  print "-" * 100
  print "test set:", output_file
  print

  for file_name in os.listdir(test_dir):
    benchmark_id = file_name[:-6]
    test_case_id = file_name[-5]
    time = unit_test(test_dir + '/' + file_name, search_algo, if_batch, p1off, p2off, p3off)
    if time >= 0:
      print "test", benchmark_id, '[sample_size=' + test_case_id + ']:','perfect program', str(round(time, 2)), 's' 
      if benchmark_id in test_result.keys():
        test_result[benchmark_id][test_case_id] = str(time) + ':s'
      else:
        test_result[benchmark_id] = {}
        test_result[benchmark_id][test_case_id] = str(time) + ':s'
    elif time == -1:
      print "test", benchmark_id, '[sample_size=' + test_case_id + ']:', 'wrong program ' 
      if benchmark_id in test_result.keys():
        test_result[benchmark_id][test_case_id] = str(time) + ':f'
      else:
        test_result[benchmark_id] = {}
        test_result[benchmark_id][test_case_id] = str(time) + ':f'

    else:
      print "test", benchmark_id, '[sample_size=' + test_case_id + ']:', 'no program    ','timeout' 
      if benchmark_id in test_result.keys():
        test_result[benchmark_id][test_case_id] = ''
      else:
        test_result[benchmark_id] = {}
        test_result[benchmark_id][test_case_id] = ''

  end = timer()
  
  print
  print "test is finished:", (end - start), "seconds"
  print

  # Save the result in ./test_result
  
  f = open(output_file, 'w')
  f.write(',')

  for i in range(1,6):
    if i < 5:
      f.write(str(i) + ',')
    else:
      f.write(str(i) + '\n')

  benchmark_ids = test_result.keys()
  benchmark_ids.sort()

  for id in benchmark_ids:
    value = test_result[id]
    f.write(id + ',')
    for i in range(1,6):
      if i < 5:
        if str(i) in value.keys():
          f.write(str(value[str(i)]) + ',')
        else:
          f.write('not found' + ',')
      else:
        if str(i) in value.keys():
          f.write(str(value[str(i)]) + '\n')
        else:
          f.write('not found' + '\n')

if __name__ == "__main__":
    main()

