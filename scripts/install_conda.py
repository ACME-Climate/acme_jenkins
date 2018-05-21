import sys
import os
import argparse

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../modules/')

import CondaSetup
import ACMEDIAGSSetup

from Const import *
from Util import *


parser = argparse.ArgumentParser(description="install acme_diags",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-w", "--workdir",
                    help="working directory where miniconda and acme_diags env will be created")
parser.add_argument("-p", "--python_version", default = 'py2', 
                    choices = ['py2', 'py3'])

args = parser.parse_args()
workdir = args.workdir
py_ver = args.python_version

status = SUCCESS

try:
    conda_setup = CondaSetup.CondaSetup(workdir, py_ver)

except:
    print("FAIL in installing anaconda")
    status = FAILURE
    sys.exit(status)

sys.exit(status)



