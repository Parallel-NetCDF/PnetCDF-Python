import glob, os, sys, unittest, struct, tempfile
from pncpy import __version__
import mpi4py

# can also just run
# python -m unittest discover . 'tst*py'

# Find all test files.
test_files = glob.glob('tst_*.py')
# test_files = ["tst_dims.py", "tst_atts.py", "tst_atts_cdf2.py", "tst_var_type.py", "tst_var_indexer.py",\
#               "tst_var_put_var1.py", "tst_var_get_var1.py", "tst_var_put_var.py", "tst_var_get_var.py",\
#               "tst_var_put_vara.py", "tst_var_get_vara.py", "tst_var_put_vars.py", "tst_var_get_vars.py"]


# Build the test suite from the tests found in the test files.
testsuite = unittest.TestSuite()
for f in test_files:
    m = __import__(os.path.splitext(f)[0])
    testsuite.addTests(unittest.TestLoader().loadTestsFromModule(m))

# Run the test suite.
def test(verbosity=1):
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(testsuite)

if __name__ == '__main__':
    import numpy, cython
    sys.stdout.write('\n')
    sys.stdout.write('PnetCDF-python version: %s\n' % __version__)
    sys.stdout.write('mpi4py version: %s\n' % mpi4py.__version__)
    sys.stdout.write('numpy version           %s\n' % numpy.__version__)
    sys.stdout.write('cython version          %s\n' % cython.__version__)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(testsuite)
    if not result.wasSuccessful():
        sys.exit(1)
