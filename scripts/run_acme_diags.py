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
                    help="working directory where miniconda and acme_diags were installed")

args = parser.parse_args()
workdir = args.workdir
status = SUCCESS

try:
    conda_setup = CondaSetup.CondaSetup(workdir)
except:
    print("FAIL in setting up conda")
    status = FAILURE
    sys.exit(status)

try:
    # for now hard code till we want to expand
    # we can then make these as arguments to the script
    env_name = 'acme_diags_master'
    env_file_url = 'https://raw.githubusercontent.com/ACME-Climate/acme_diags/master/conda/acme_diags_env_dev.yml'

    acme_diags_setup = ACMEDIAGSSetup.ACMEDIAGSSetup(conda_setup, env_name, env_file_url)
except:
    print("FAIL in creating acme_diags environment")
    status = FAILURE
    sys.exit(status)

status = acme_diags_setup.install_tests()
if status != SUCCESS:
    sys.exit(status)

status = acme_diags_setup.run_tests()

sys.exit(status)    


