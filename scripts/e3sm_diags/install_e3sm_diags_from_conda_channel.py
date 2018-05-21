import sys
import os
import argparse

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../../modules/')

import CondaSetup
import ACMEDIAGSSetup

from Const import *
from Util import *


parser = argparse.ArgumentParser(description="install acme_diags",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-w", "--workdir", required=True,
                    help="working directory where miniconda and acme_diags env will be created")
parser.add_argument("-e", "--env_name", required=True,
                    help="env name")

args = parser.parse_args()
workdir = args.workdir
env_name = args.env_name

status = SUCCESS

sys.stdout.flush()

try:
    conda_setup = CondaSetup.CondaSetup(workdir)
    print("after getting conda setup")
    env_name = args.env_name
    acme_diags_setup = ACMEDIAGSSetup.ACMEDIAGSSetup(conda_setup, env_name)
    acme_diags_setup.create_env_from_conda_channel(env_name)

except Exception as err:
    print("FAIL in creating {e} environment".format(e=env_name))
    print("Error message: {e}".format(e=err))
    status = FAILURE
    sys.exit(status)

sys.exit(status)




