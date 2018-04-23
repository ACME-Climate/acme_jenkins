import sys
import os
import time
import argparse
import shutil

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../modules/')

from Util import *

parser = argparse.ArgumentParser(description="install conda",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--testdir",
                    help="parent testdir where old dated test subdirectories are to be cleaned up")
parser.add_argument("-n", "--ndays",
                    action="store", type=int,
                    help="number of days, test directories older than specified <ndays> will be removed")
args = parser.parse_args()

testdir = args.testdir
ndays = args.ndays

if os.path.isdir(testdir) == False:
    print('ERROR, test dir ' + testdir + ' does not exist')
    sys.exit(FAILURE)

seconds = ndays * 24 * 3600

now = time.time()
for a_file in os.listdir(testdir):
    the_file = os.path.join(testdir, a_file)
    if os.stat(the_file).st_mtime < (now - seconds):
 
        print("FOUND...: {f}".format(f=the_file))
        print("Removing {f}".format(f=the_file))
        #shutil.rmtree(the_file)
        # os.unlink(the_file)
        if os.path.isdir(the_file):
            cmd = "/bin/rm -rf {to_be_removed}".format(to_be_removed=the_file)
            ret_code = run_cmd(cmd, True, True, True)
    
