from os import path
import shutil
import glob
import sys
import subprocess
from model import Model, create_model_configurations


def run_prep(model_name):

    # copy start directory into a new directory
    create_dir = subprocess.Popen("cp -r double_gyre_base/" +
                                  " ./" + model_name,
                                  shell=True)
    create_dir.wait()

    # Setup restart for run
    create_restart = subprocess.Popen("mkdir -p ./" + model_name + "/RESTART",
                                      shell=True)
    create_restart.wait()


def write_override_parameters(model):
    """Writes parameters for model before run"""

    # Open MOM_override
    override = open("./" + model.run_name + "/MOM_override", mode="w+")
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


def run_MOM6_model(model_name):
    """Runs the MOM6 model (ocean-only), captures output and places all
       output files in current directory in dir named after model_name"""
    print("Running " + model_name + "...")
    run_model = subprocess.Popen("srun ../Ocean/MOM6-examples/build/gnu/ocean_only/repro/MOM6",
                                 stdout=subprocess.PIPE,
                                 shell=True)
    run_model.wait()

    # Read model output into data dir
    model_output = run_model.stdout.read()
    f = open(model_name + "/output.txt", "wb+")
    f.write(model_output)



def setup_multiple_configurations(model_list, num_alters):
    """sets up multiple iterations of the MOM6 model.
       Each model is run for a number of times specified by num_alters"""

    param_to_alter = "KH"

    print("Setting up model configurations for multiple runs...")
    for m in model_list:
        for i in range(num_alters):

            # decrease paramter value by model.step
            m.alter_parameter(param_to_alter)
            new_param_val = m.get_parameter(param_to_alter)
            m.set_run_name(str(new_param_val))
            run_prep(m.run_name)
            write_override_parameters(m)
            run_names.append(m.run_name)


def run_all_configurations(model_names):
    for configured_model_name in model_names:
        run_MOM6_model(configured_model_name)


if __name__ == "__main__":

    #list of base models
    model_list = create_model_configurations()

    # list of configured models
    run_names = []

    # run multiple configurations of the models in model_list
    num_alters = 34
    setup_multiple_configurations(model_list, num_alters)

    run_all_configurations(run_names)
