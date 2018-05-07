import sys
import shutil
import time
import re

from Const import *
from Util import *

sys.stdout.flush()

class ACMEDIAGSSetup:
    def __init__(self, conda_setup, env_name):

        workdir = conda_setup.workdir
        env_dir = os.path.join(workdir, 'miniconda', 'envs', env_name)
        print("xxx DEBUG DEBUG...env_dir: {e}".format(e=env_dir))
        if os.path.isdir(env_dir):
            self.env = env_name
            print("Environment {e} is already created.".format(e=env_name))
            self.workdir = conda_setup.workdir
            self.conda_path = conda_setup.conda_path
            return

        self.workdir = conda_setup.workdir
        self.conda_path = conda_setup.conda_path

    def get_env_name(self):
        return self.env

    def create_env_from_yaml_file(self, env_name, env_file_url):

        # get the env yml file
        yml_file_name = "{e}.yml".format(e=env_name)
        env_file = os.path.join(self.workdir, yml_file_name)
        cmd = "wget {url} -O {env_file}".format(url=env_file_url,
                                                env_file=env_file)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return ret_code

        # remove any cached conda packages
        conda_cmd = os.path.join(self.conda_path, 'conda')
        cmd = "{conda} clean --all".format(conda=conda_cmd)

        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return(ret_code)
        
        # create the environment
        cmd = "{conda} env create -n {env} -f {env_file}".format(conda=conda_cmd,
                                                                 env=env_name,
                                                                 env_file=env_file)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return ret_code

        self.env = env_name

        # conda list for debugging purpose
        cmds_list = ["conda list"]
        ret_code = run_in_conda_env(self.conda_path, env_name, cmds_list)
        if ret_code != SUCCESS:
            print("FAIL...{c}".format(c=cmd))
            return ret_code

    def get_tests(self, build_tests):
        # get test code from 'master' -
        # may need some parameter to determine with
        # version of test to get
        # build_tests - set it to True if we should build the test
        #    i.e. run 'python setup.py install'
        #
        url = "https://github.com/E3SM-Project/acme_diags.git"
        repo_dir = os.path.join(self.workdir, 'acme_diags')

        # check if repo_dir exists already
        if os.path.isdir(repo_dir):
            shutil.rmtree(repo_dir)

        cmd = "git clone {url} {repo_dir}".format(url=url,
                                                  repo_dir=repo_dir)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            return ret_code

        # install test code
        if build_tests == True:
            cmds_list = []
            cmds_list.append("cd {repo_dir}".format(repo_dir=repo_dir))
            cmds_list.append("python setup.py install")
        
            ret_code = run_in_conda_env(self.conda_path, self.env, cmds_list)

        return(ret_code)

    def __prep_sbatch_file(self, results_base_dir, results_dir_prefix, time_stamp, cmd):
        
        sbatch_file_prefix = os.path.join(results_base_dir, 
                                          "{prefix}_{t}".format(prefix=results_dir_prefix,
                                                                t=time_stamp))
        sbatch_file = "{f}.sh".format(f=sbatch_file_prefix)
        sbatch_out = "{f}.out".format(f=sbatch_file_prefix)
        sbatch_err = "{f}.err".format(f=sbatch_file_prefix)
        num_workers = 16

        f = open(sbatch_file, "w")
        f.write("#!/bin/bash\n")
        f.write("#SBATCH -N 1\n")
        f.write("#SBATCH -n {w}\n".format(w=num_workers))
        f.write("#SBATCH -t 0-06:00\n")
        f.write("#SBATCH -o {out_file}\n".format(out_file=sbatch_out))
        f.write("#SBATCH -e {err_file}\n".format(err_file=sbatch_err))
        f.write("{c}\n".format(c=cmd))
        f.close()
        print("Output file: {f}".format(f=sbatch_out))
        print("Error file : {f}".format(f=sbatch_err))
        return(sbatch_file)

    def __wait_till_slurm_job_completes(self, job_id):
        
        cmd = "scontrol show job {id} | grep JobState".format(id=job_id)
        return_code = SUCCESS
        time.sleep(30)
        n_no_output = 0

        while True and n_no_output <= 10:
            ret_code, out = run_in_conda_env_capture_output(self.conda_path, 
                                                            self.env, [cmd])
            if out:
                match_obj = re.match(r'\s+JobState=(\S+)\s+Reason', out[0])
                if match_obj:
                    job_state = match_obj.group(1)
                    if job_state == 'COMPLETED':
                        print("job {id} completed!".format(id=job_id))
                        break
                    elif job_state == 'FAILED':
                        print("job {id} FAILED!".format(id=job_id))
                        break
                    else:
                        print("job {id} is in {state} state".format(id=job_id,
                                                                    state=job_state))
                    time.sleep(120)
                else:
                    print("Cannot get slurm job state for job id: {id}".format(id=job_id))
                    ret_code = FAILURE
                    break
            else:
                print("No output...sleep for 10 seconds...")
                n_no_output += 1
                time.sleep(10)

        return ret_code


    def __submit_cmd_to_slurm_and_wait(self, results_base_dir, results_dir_prefix, time_str, cmd):

        sbatch_file = self.__prep_sbatch_file(results_base_dir, 
                                              results_dir_prefix,
                                              time_str,
                                              cmd)
        print("DEBUG...sbatch_file: {f}".format(f=sbatch_file))
        print("results_base_dir: {d}".format(d=results_base_dir))
        print("results_dir_prefix: {p}".format(p=results_dir_prefix))
        cmds_list = ["sbatch {f}".format(f=sbatch_file)]
        ret_code, sbatch_output = run_in_conda_env_capture_output(self.conda_path, self.env, cmds_list)
        # Submitted batch job 6389
        match_obj = re.match(r'Submitted\s+batch\s+\job\s+(\d+)', sbatch_output[0])
        if match_obj:
            job_id = match_obj.group(1)
            print("slurm job id: {id}".format(id=job_id))
        else:
            print("FAIL in submitting acme_diags to slurm")
            return FAILURE

        # wait till job completes
        ret_code = self.__wait_till_slurm_job_completes(job_id)
        return ret_code

    def run_system_tests(self, backend=None):

        results_base_dir = "/var/www/acme/acme-diags/e3sm_diags_jenkins"
        if backend:
            results_dir_prefix = "{env}_system_{backend}".format(env=self.env,
                                                                 backend=backend)
        else:
            results_dir_prefix = "{env}_system".format(env=self.env)

        current_time = time.localtime(time.time())
        time_str = time.strftime("%Y.%m.%d-%H:%M:%S", current_time)

        test_dir = os.path.join(self.workdir, 'acme_diags', 'tests', 'system')
        results_dir = os.path.join(test_dir, 'all_sets')

        cmd1 = "cd {d}".format(d=test_dir)
        if backend:
            cmd2 = "e3sm_diags -d all_sets.cfg --backend vcs"
        else:
            cmd2 = "e3sm_diags -d all_sets.cfg"

        cmd = "{c1};\n{c2}".format(c1=cmd1, c2=cmd2)

        ret_code = self.__submit_cmd_to_slurm_and_wait(results_base_dir, 
                                                       results_dir_prefix, 
                                                       time_str, cmd)
        run_cmd("ls {d}".format(d=test_dir), True, False, True)
        run_cmd("ls {d}".format(d=results_dir), True, False, True)
        return ret_code
        
    def run_sets_tests(self, obs_or_model, backend, git_branch):
        """
        obs_or_model: 'model_vs_obs' or 'model_vs_model'
        backend: 'vcs' or 'mpl'
        """
        results_base_dir = "/var/www/acme/acme-diags/e3sm_diags_jenkins"
        results_dir_prefix = "{env}_{backend}_{o_m}".format(env=self.env,
                                                            backend=backend,
                                                            o_m=obs_or_model)
        current_time = time.localtime(time.time())
        time_str = time.strftime("%Y.%m.%d-%H:%M:%S", current_time)

        results_dir = "{base_dir}/{prefix}_{time_stamp}".format(base_dir=results_base_dir,
                                                                prefix=results_dir_prefix,
                                                                time_stamp=time_str)
        test_script = "all_sets_nightly_{o_m}.py".format(o_m=obs_or_model)
        #base_url = "https://raw.githubusercontent.com/ACME-Climate/acme_diags"
        base_url = "https://raw.githubusercontent.com/E3SM-Project/acme_diags"
        workdir = self.workdir
        test_script_url = "{base_url}/{branch}/tests/{test_script}".format(base_url=base_url,
                                                                     branch=git_branch,
                                                                     test_script=test_script)
        test_script_path = "{workdir}/{test_script}".format(workdir=workdir,
                                                            test_script=test_script)
        if os.path.exists(test_script_path):
            os.remove(test_script_path)
        cmd = "wget {url} -O {dest_file}".format(url=test_script_url,
                                                 dest_file=test_script_path)
        ret_code = run_cmd(cmd, True, False, True, workdir)
        if ret_code != SUCCESS:
            return ret_code        
        
        num_workers = 16
        cmd = "e3sm_diags -p {t} --backend {b} --results_dir {d} --num_workers {w}".format(t=test_script_path,
                                                                                           b=backend,
                                                                                           w=num_workers,
                                                                                           d=results_dir)
        
        ret_code = self.__submit_cmd_to_slurm_and_wait(results_base_dir, 
                                                       results_dir_prefix, 
                                                       time_str, cmd)
        print("Result directory: ", results_dir)
        run_cmd("ls {d}".format(d=results_dir), True, False, True)

        return ret_code
    
