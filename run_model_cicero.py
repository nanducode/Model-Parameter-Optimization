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
    create_dir = subprocess.Popen("cp -r double_gyre_base/" +
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


def write_override_parameters(model):
    """Writes parameters for model before run"""

    # Open MOM_override
    override = open(MOM6DIR + "/ocean_only/" + model.run_name + "/MOM_override", mode="w+")
    for k, v in model.parameters.items():
        if k in model.altered_params:
            altered = model.altered_params[k]
            override.write("#override " + k + "=" + str(altered) + "\n")
        else:
            override.write("#override " + k + "=" + str(v) + "\n")
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
        file_name = path.basename(f)
        # MOM_parameter_doc.
        if file_name.endswith(".short") or file_name.endswith(".all") or file_name.endswith(".layout"):
            move_file(file_name, model_name)
        # logs of run
        elif file_name.startswith("logfile"):
            move_file(file_name, model_name)
        elif file_name.startswith("available_diags"):
            move_file(file_name, model_name)
        elif file_name == "ocean.stats":
            move_file(file_name, model_name)
        # Diagnostic table
        elif file_name == "diag_table":
            move_file(file_name, model_name)
        elif file_name == "MOM_override":
            move_file(file_name, model_name)
        # all netCDF data
        elif file_name.endswith(".nc"):
            move_file(file_name, model_name)
        elif file_name == "input.nml":
            move_file(file_name, model_name)


def run_MOM6_model(model_name, num_proc):
    """Runs the MOM6 model (ocean-only), captures output and places all
       output files in current directory in dir named after model_name"""
    run_model = subprocess.Popen("salloc -N " + str(num_proc) + " -n " + str(num_proc)
                                 + " ../../../../run_training" +
                                 " ../../build/gnu/ocean_only/repro/MOM6",
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



def run_multiple_configurations(model_list, num_alters, num_proc):
    """Runs multiple iterations of the MOM6 model.
       Each iteration a parameter is altered by percent alteration
       percent_alteration is increase each time by step
       Each model is run for a number of times specified by num_alters"""

    param_to_alter = "KH"

    for m in model_list:
        for i in range(num_alters):

            # decrease paramter value by model.step
            m.alter_parameter(param_to_alter)
            new_param_val = m.get_parameter(param_to_alter)
            m.set_run_name(str(new_param_val))
            run_prep(m.run_name)

            write_override_parameters(m)
            run_MOM6_model(m.run_name, num_proc)



if __name__ == "__main__":

    # variables to set for the run
    MOM6DIR = "../Ocean/MOM6-examples"

    #list of models
    model_list = create_model_configurations()

    # number of processors to run on
    num_proc = 32

    # run multiple configurations of the models in model_list
    num_alters = 33
    run_multiple_configurations(model_list, num_alters, num_proc)
