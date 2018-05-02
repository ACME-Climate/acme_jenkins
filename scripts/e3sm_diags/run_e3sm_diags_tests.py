import sys
import os
import argparse

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../../modules/')

import CondaSetup
import ACMEDIAGSSetup

from Const import *
from Util import *

#
# python scripts/acme_diags/run_acme_diags_tests.py -w $WORKDIR -e acme_diags_env_dev -t all_sets -b master -m "model_vs_obs" -d vcs -i
#

parser = argparse.ArgumentParser(description="install acme_diags",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-w", "--workdir",
                    help="working directory where anaconda and acme_diags were installed")
parser.add_argument("-e", "--env_name",
                    help="environment name")
parser.add_argument("-i", "--build_tests", action='store_true',
                    help="whether tests should be built first when running system tests")
parser.add_argument("-t", "--test_type", choices=['system', 'all_sets'],
                    help="whether to run 'system tests' or 'all sets tests'")
parser.add_argument("-b", "--git_branch", default='master',
                    help="git branch to get tests from")
parser.add_argument("-m", "--obs_or_model", choices=['model_vs_obs', 'model_vs_model'],
                    nargs='?',
                    help="run model_vs_obs or model_vs_model")
parser.add_argument("-d", "--backend", choices=['vcs', 'mpl'],
                    help="backend type: 'vcs' or 'mpl'")

args = parser.parse_args()
workdir = args.workdir
status = SUCCESS

try:
    conda_setup = CondaSetup.CondaSetup(workdir)
except:
    print("FAIL in setting up conda")
    status = FAILURE
    sys.exit(status)

# for now hard code till we want to expand
# we can then make these as arguments to the script
env_name = args.env_name

acme_diags_setup = ACMEDIAGSSetup.ACMEDIAGSSetup(conda_setup, env_name)
status = acme_diags_setup.get_tests(args.build_tests)

if args.test_type == 'system':

    if status != SUCCESS:
        sys.exit(status)
    status = acme_diags_setup.run_system_tests()

else:
    # running all sets tests
    status = acme_diags_setup.run_sets_tests(args.obs_or_model,
                                             args.backend,
                                             args.git_branch)
    if status != SUCCESS:
        sys.exit(status)

sys.exit(status)    



