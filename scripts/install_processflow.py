import sys
import os
import argparse

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../modules/')
from Util import *

parser = argparse.ArgumentParser(description="install processflow",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-w", "--workdir",
                    help="working directory -- where conda env was installed")
parser.add_argument("-v", "--version",
                    help="version -- 'nightly' or 'latest'")

args = parser.parse_args()
workdir = args.workdir
version = args.version

try:
    conda_setup = CondaSetup.CondaSetup(workdir)

    # for now hard code till we want to expand
    # we can then make these as arguments to the script
    env_name = 'processflow'
    processflow_setup = ProcessFlowSetup.ProcessFlowSetup(conda_setup, env_name, version)

except Exception as err:
    print("FAIL in creating processflow environment")
    print("Error message: {e}".format(e=err))
    status = FAILURE
    sys.exit(status)


sys.exit(status)











