# Create a test result folder
mkdir test_result

# Create a generated figures folder
mkdir figures

# Test a-start batch with full prune
python test.py --test_dir data --output ./test_result/ted_batch.csv

# Test bfs
python test.py --search_algo 0 --test_dir data --output ./test_result/bfs.csv

# Test rule-based heuristic
python test.py --search_algo 2 --test_dir data --output ./test_result/rule_based.csv

# Test a-start no batch with full prune
python test.py --no_batch --test_dir data --output ./test_result/ted_no_batch.csv

# Test a-start batch with global prune
python test.py --opPruneOff --test_dir data --output ./test_result/ted_batch_global_prune.csv

# Test a-start batch with op prune
python test.py --globalPruneOff --test_dir data --output ./test_result/ted_batch_op_prune.csv

# Test a-start batch with no prune
python test.py --globalPruneOff --opPruneOff --test_dir data --output ./test_result/ted_batch_no_prune.csv

# Test bfs with no prune
python test.py --globalPruneOff --opPruneOff --search_algo 0 --test_dir data --output ./test_result/bfs_no_prune.csv

# Test bfs with no wrap
python test.py --wrap1off --wrap2off --wrap3off --test_dir data --output ./test_result/ted_batch_no_wrap.csv

# Test bfs with wrap 1
python test.py --wrap2off --wrap3off --test_dir data --output ./test_result/ted_batch_w1.csv

# Test bfs with wrap 1 & wrap2
python test.py --wrap3off --test_dir data --output ./test_result/ted_batch_w1_w2.csv

# Figure 11(a)
python figure_11_a.py

# Figure 11(b)
python figure_11_b.py

# Figure 11(c)
python figure_11_c.py

# Figure 12(a)
python figure_12_a.py

# Figure 12(b)
python figure_12_b.py

# Figure 12(c)
python figure_12_c.py