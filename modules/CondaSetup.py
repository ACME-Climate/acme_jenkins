import os
import sys

from Util import *

class CondaSetup:
    def __init__(self, workdir):
        print("xxx CondaSetup __init__")
        if os.path.isdir(workdir):
            print("{w} directory exists".format(w=workdir))
            self.workdir = workdir
            conda_path = os.path.join(workdir, 'miniconda', 'bin')
            if os.path.isdir(conda_path):
                self.conda_path = conda_path
                print("conda is already installed, conda_path: {c}".format(c=conda_path))
                return
        
        print("xxx going to install conda")
        self.conda_path = None
        self.install_miniconda(workdir)


    def install_miniconda(self, workdir):

        print("xxx install_miniconda xxx")
        # create workdir if it does not exist         
        if os.path.isdir(workdir) == True:
            print('INFO: ' + workdir + ' already exists')
            if self.conda_path != None and os.path.isdir(self.conda_path) == True:
                return(SUCCESS, self.conda_path)
        else:
            print("mkdir {d}".format(d=workdir))
            os.mkdir(workdir)

        self.workdir = workdir

        url = "https://repo.continuum.io/miniconda/"
        
        conda_script = os.path.join(workdir, 'miniconda.sh')
        
        if sys.platform == 'darwin':
            source_script = url + 'Miniconda3-latest-MacOSX-x86_64.sh'
            cmd = "curl {src} -o {dest}".format(src=source_script, dest=conda_script)
        else:            
            source_script = url + 'Miniconda3-latest-Linux-x86_64.sh'
            cmd = "wget {src} -O {dest}".format(src=source_script, dest=conda_script)

        ret_code = run_cmd(cmd, True, False, False)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))

        conda_dir = os.path.join(workdir, 'miniconda')
        cmd = "bash {script} -b -p {dir}".format(script=conda_script, dir=conda_dir)
        # run the command, set verbose=False 
        ret_code = run_cmd(cmd, True, False, False)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))

        self.conda_path = os.path.join(conda_dir, 'bin')
        conda_path = self.conda_path

        conda_cmd = os.path.join(conda_path, 'conda')
        cmd = "{c} config --set always_yes yes --set changeps1 no".format(c=conda_cmd)
    
        ret_code = run_cmd(cmd)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))

        cmd = "{c} install gcc future".format(c=conda_cmd)
        ret_code = run_cmd(cmd, True, False, True)
        if ret_code != SUCCESS:
            raise Exception("FAIL...{c}".format(c=cmd))

        if sys.platform == 'darwin':
            cmd = "{c} update -y -q conda".format(c=conda_cmd)
            ret_code = run_cmd(cmd, True, False, False)
            if ret_code != SUCCESS:
                raise Exception("FAIL...{c}".format(c=cmd))

        cmd = "{c} config --set conda_upload no".format(c=conda_cmd)
        ret_code = run_cmd(cmd)
        return(ret_code)


