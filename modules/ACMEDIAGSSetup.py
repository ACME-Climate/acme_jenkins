from Const import *
from Util import *

class ACMEDIAGSSetup:
    def __init__(self, conda_setup, env_name, env_file_url):

        workdir = conda_setup.workdir
        env_dir = os.path.join(workdir, 'miniconda', 'envs', env_name)
        if os.path.isdir(env_dir):
            print("Environment {e} is already created.".format(e=env_name))
            self.workdir = conda_setup.workdir
            self.conda_path = conda_setup.conda_path
            self.env = env_name
            return

        self.workdir = conda_setup.workdir
        self.conda_path = conda_setup.conda_path
        self.create_env(env_name, env_file_url)


    def create_env(self, env_name, env_file_url):

        # get the env yml file
        env_file = os.path.join(self.workdir, 'acme_diags_env.yml')
        cmd = "wget {url} -O {env_file}".format(url=env_file_url,
                                                env_file=env_file)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))

        # remove any cached conda packages
        conda_cmd = os.path.join(self.conda_path, 'conda')
        cmd = "{conda} clean --all".format(conda=conda_cmd)

        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))
        
        # create the environment
        cmd = "{conda} env create -n {env} -f {env_file}".format(conda=conda_cmd,
                                                                 env=env_name,
                                                                 env_file=env_file)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))
        self.env = env_name

        # conda list for debugging purpose
        cmds_list = ["conda list"]
        ret_code = run_in_conda_env(self.conda_path, env_name, cmds_list)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))

    def install_tests(self):
        # get test code from 'master' -
        # may need some parameter to determine with
        # version of test to get
        url = "https://github.com/ACME-Climate/acme_diags.git"
        repo_dir = os.path.join(self.workdir, 'acme_diags')
        cmd = "git clone {url} {repo_dir}".format(url=url,
                                                  repo_dir=repo_dir)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            return ret_code

        # install test code
        cmds_list = []
        cmds_list.append("cd {repo_dir}".format(repo_dir=repo_dir))
        cmds_list.append("python setup.py install")
        
        ret_code = run_in_conda_env(self.conda_path, self.env, cmds_list)
        return(ret_code)

    def run_tests(self):
        test_dir = os.path.join(self.workdir, 'acme_diags', 'tests')
        cmds_list = []
        cmds_list.append("cd {d}".format(d=test_dir))
        cmds_list.append("acme_diags_driver.py -d all_sets.cfg")
        ret_code = run_in_conda_env(self.conda_path, self.env, cmds_list)

        return(ret_code)

        
