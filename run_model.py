from os import path
import shutil
import glob
import sys
import subprocess
from model import Model, create_model_configurations


def run_prep(model_name):
    # Remove directory from previous run
    remove_dir = subprocess.Popen("rm -rf " + MOM6DIR + "/ocean_only/" + model_name,
                                  shell=True)
    remove_dir.wait()

    # copy start directory into a new directory
    create_dir = subprocess.Popen("cp -r " + MOM6DIR + "/ocean_only/double_gyre_start" +
                                  " " + MOM6DIR + "/ocean_only/" + model_name,
                                  shell=True)
    create_dir.wait()

    # Setup restart for run
    create_restart = subprocess.Popen("mkdir -p " + MOM6DIR + "/ocean_only/"
                                      + model_name + "/RESTART",
                                      shell=True)
    create_restart.wait()

    # Create data dir in MPO dir
    create_dir = subprocess.Popen("mkdir -p ./" + model_name, shell=True)
    create_dir.wait()


def write_override_configs(model):
    """Writes configurations for model before run"""

    # Open MOM_override
    override = open(MOM6DIR + "/ocean_only/" + model.name + "/MOM_override", mode="w+")
    for k, v in model.configs.items():
        override.write("#override " + k + "=" + v + "\n")
    override.close()


# helper for moving files
def move_file(f, model_name):
    f = path.basename(f)
    shutil.move(MOM6DIR + "/ocean_only/" + model_name + "/" + f,
                "./" + model_name + "/" + f)

def collect_data_from_run(model_name):
    """Collects all data from a run"""
    run_dir_glob = MOM6DIR + "/ocean_only/" + model_name + "/*"
    for f in glob.glob(run_dir_glob):
        # MOM_parameter_doc.
        if f.endswith(".short") or f.endswith(".all") or f.endswith(".layout"):
            move_file(f, model_name)
        # logs of run
        elif f.startswith("logfile"):
            move_file(f, model_name)
        elif f.startswith("available_diags"):
            move_file(f, model_name)
        elif f == "ocean.stats":
            move_file(f, model_name)
        # Diagnostic table
        elif f == "diag_table":
            move_file(f, model_name)
        # all netCDF data
        elif f.endswith(".nc"):
            move_file(f, model_name)


def run_MOM6_model(model_name):
    """Runs the MOM6 model (ocean-only), captures output and places all
       output files in current directory in dir named after model_name"""
    run_model = subprocess.Popen("mpirun -n 4 ../../build/intel/ocean_only/repro/MOM6",
                                 cwd=MOM6DIR + "/ocean_only/" + model_name,
                                 stdout=subprocess.PIPE,
                                 shell=True)
    run_model.wait()

    # Read model output into data dir
    model_output = run_model.stdout.read()
    f = open(model_name + "/output.txt", "wb+")
    f.write(model_output)

    # get all parameter and .nc files
    collect_data_from_run(model_name)



if __name__ == "__main__":

    # variables to set for the run
    MOM6DIR = "../MOM6-examples"

    #list of models
    model_list = create_model_configurations()

    for m in model_list:
        run_prep(m.name)
        write_override_configs(m)
        run_MOM6_model(m.name)
