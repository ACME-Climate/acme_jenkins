import sys
import os
import argparse

thisDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(thisDir + '/../modules/')
from Util import *

class ProcessFlowSetup: 
    def __init__(self, conda_setup, env_name, version):

        workdir = conda_setup.workdir
        env_dir = os.path.join(workdir, 'miniconda', 'envs', env_name)
        if os.path.isdir(env_dir):
            print("Environment {e} is already created.".format(e=env_name))
            self.workdir = conda_setup.workdir
            self.conda_path = conda_setup.conda_path
            self.env = env_name
        else:
            self.workdir = conda_setup.workdir
            self.conda_path = conda_setup.conda_path
            self.create_env(env_name, version)

    def __check_version(self, version):
    
        if version == 'nightly':
            version_str = 'acme/label/nightly'
        elif version == 'latest':
            version_str = 'acme'
        
        conda_path = self.conda_path
        env = self.env
        # print out whole version of processflow -- just for logging purpose
        cmds_list = []
        cmd = "conda list processflow | grep '^processflow'"
        cmds_list.append(cmd)
        ret_code = run_in_conda_env(conda_path, env, cmds_list) 
        if ret_code != SUCCESS:
            return(ret_code)

        cmds_list = []
        cmd = "conda list processflow | grep '^processflow' | awk -F\\\" \\\" '{ print \$4 }'"
        cmds_list.append(cmd)
        
        (ret_code, output) = run_in_conda_env_capture_output(conda_path, env, cmds_list) 
        if ret_code != SUCCESS:
            return(ret_code)    

        if version_str == output[0].rstrip():
            print("Version matched: {v}".format(v=version))
            ret_code = SUCCESS
        else:
            print("version: {v}, output: {o}, they do not match!!!".format(v=version_str,
                                                                       o=output[0]))
            ret_code = FAILURE
        return(ret_code)

    def create_env(self, env_name, version):
        """
        version can be 'nightly' or 'latest'
        """
        conda_path = self.conda_path
        conda_cmd = os.path.join(conda_path, 'conda')

        
        channels = "-c acme -c conda-forge -c uvcdat"
        cmd = "{conda} create --name {env} {c} processflow".format(conda=conda_cmd,
                                                                   env=env_name,
                                                                   c=channels)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return(ret_code)

        self.env = env_name
        # update to version -- 'nightly' or 'latest'
        cmds_list = []
        cmd = 'conda config --set always_yes yes'
        cmds_list.append(cmd)

        # update to nightly
        if version == 'nightly':
            cmd = 'conda update -c acme/label/nightly -c acme -c conda-forge -c uvcdat processflow'
        else:
            cnd = 'conda update -c acme -c conda-forge -c uvcdat processflow'
        cmds_list.append(cmd)
        ret_code = run_in_conda_env(conda_path, env_name, cmds_list)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return(ret_code)
     
        # check that we can activate processflow env
        cmd = 'conda list processflow'
        cmds_list = []
        cmds_list.append(cmd)
        ret_code = run_in_conda_env(conda_path, env_name, cmds_list)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return(ret_code)

        # check version of processflow
        ret_code = self.__check_version(version)
        return(ret_code)
