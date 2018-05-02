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
parser.add_argument("-b", "--branch", default='master',
                    help="git branch to pull the yml file from")
parser.add_argument("-e", "--env_name", required=True,
                    help="env name")
parser.add_argument("-f", "--env_file_name",
                    help="env yaml file name")

args = parser.parse_args()
workdir = args.workdir

status = SUCCESS

try:
    conda_setup = CondaSetup.CondaSetup(workdir)
    print("after getting conda setup")
    # for now hard code till we want to expand
    # we can then make these as arguments to the script
    env_name = args.env_name
    base_url = "https://raw.githubusercontent.com/E3SM-Project/acme_diags"
    #base_url = 'https://github.com/E3SM-Project/acme_diags'
    env_file_url = "{base_url}/{branch}/conda/{f}".format(base_url=base_url,
                                                          branch=args.branch,
                                                          f=args.env_file_name)
    acme_diags_setup = ACMEDIAGSSetup.ACMEDIAGSSetup(conda_setup, env_name)
    acme_diags_setup.create_env_from_yaml_file(env_name, env_file_url)

except Exception as err:
    print("FAIL in creating acme_diags environment")
    print("Error message: {e}".format(e=err))
    status = FAILURE
    sys.exit(status)


sys.exit(status)




