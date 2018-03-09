import sys
import os
import argparse

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../modules/')
import CondaSetup
import ProcessFlowSetup

from Const import *
from Util import *

parser = argparse.ArgumentParser(description="run_processflow",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-w", "--workdir",
                    help="working directory -- where conda env was installed")
parser.add_argument("-v", "--version",
                    help="version -- 'nightly' or 'latest'")
parser.add_argument("-c", "--conf_type",
                    help="config_type")

args = parser.parse_args()
workdir = args.workdir
version = args.version

# TEMPORARY
##conf_file = "/p/user_pub/e3sm/jenkins/acme_processflow/testdir/processflow_nightly/test_12/run.cfg"

def prepare_conf_file(workdir, conf_type):
    
    conf_file_name = "run.cfg.{c}".format(c=conf_type)
    template_file = os.path.join(thisDir, "..", "test_configs", "processflow", conf_file_name)
    dest_file = os.path.join(workdir, conf_file_name)

    src_f = open(template_file, "r")
    temp_f = open(dest_file, "w+")
    for a_line in src_f:
        if a_line.startswith("project_path"):
            temp_f.write("project_path = {p}".format(p=workdir))
        else:
            temp_f.write(a_line)
    src_f.close()
    temp_f.close()

    return dest_file

# TEMPORARY

    
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

# prepare a config file

conf_file = prepare_conf_file(workdir, args.conf_type)

status = processflow_setup.run_processflow(conf_file)




sys.exit(status)











