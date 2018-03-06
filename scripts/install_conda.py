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

args = parser.parse_args()
workdir = args.workdir
status = SUCCESS

try:
    conda_setup = CondaSetup.CondaSetup(workdir)

except:
    print("FAIL in installing anaconda")
    status = FAILURE
    sys.exit(status)

sys.exit(status)



