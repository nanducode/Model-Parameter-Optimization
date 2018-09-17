import os
import shutil
import glob
import sys
import subprocess
import base64

# TODO: flexible filepaths
#       come up with dir naming system
#       compile and run multicore
#       iterate over multiple runs
#       encapsulate as functions.
#       Adjust parameters before runs in MOM_OVERRIDE

run_name = "double_gyre_1"

# Remove directory from previous run
remove_dir = subprocess.Popen("rm -rf ../MOM6-examples/ocean_only/double_gyre_1",
                              shell=True)
remove_dir.wait()

# copy start directory into a new directory
create_dir = subprocess.Popen("cp -r ../MOM6-examples/ocean_only/double_gyre_start ../MOM6-examples/ocean_only/" + run_name,
                              shell=True)
create_dir.wait()


# Compile Flexible Model System
create_fms_build_dir = subprocess.Popen("mkdir -p ../MOM6-examples/build/intel/shared/repro",
                                        shell=True)
create_fms_build_dir.wait()
setup_fms = subprocess.Popen("(rm -f path_names; ../../../../src/mkmf/bin/list_paths -l ../../../../src/FMS; \
../../../../src/mkmf/bin/mkmf -t ../../../../src/mkmf/templates/sam-linux-gnu.mk \
-p libfms.a -c '-Duse_netCDF -DSPMD' path_names)",
                             cwd="../MOM6-examples/build/intel/shared/repro/",
                             shell=True)
setup_fms.wait()
compile_fms = subprocess.Popen("(source ../../env; make NETCDF=3 REPRO=1 libfms.a -j)",
               cwd="../MOM6-examples/build/intel/shared/repro/",
                               shell=True)
compile_fms.wait()


# Compile MOM6 model
create_MOM_dir = subprocess.Popen("mkdir -p ../MOM6-examples/build/intel/ocean_only/repro/",
                                  shell=True)
create_MOM_dir.wait()
setup_MOM = subprocess.Popen("(rm -f path_names; ../../../../src/mkmf/bin/list_paths -l \
../ ../../../../src/MOM6/{config_src/dynamic,config_src/solo_driver,src/{*,*/*}}/ ; \
../../../../src/mkmf/bin/mkmf -t ../../../../src/mkmf/templates/sam-linux-gnu.mk -o \
'-I../../shared/repro' -p MOM6 -l '-L../../shared/repro -lfms' -c '-Duse_netCDF -DSPMD' path_names)",
               cwd="../MOM6-examples/build/intel/ocean_only/repro/",
                             shell=True)
setup_MOM.wait()
compile_MOM = subprocess.Popen("(source ../../env; make NETCDF=3 REPRO=1 MOM6 -j)",
                               cwd="../MOM6-examples/build/intel/ocean_only/repro/",
                               shell=True)



# Setup restart for run
create_restart = subprocess.Popen("mkdir -p ../MOM6-examples/ocean_only/" + run_name + "/RESTART",
                                  shell=True)
create_restart.wait()


# Run the model
run_model = subprocess.Popen("mpirun ../../build/intel/ocean_only/repro/MOM6",
                             cwd="../MOM6-examples/ocean_only/" + run_name,
                             stdout=subprocess.PIPE,
                             shell=True)
run_model.wait()

# Create data dir in MPO
create_dir = subprocess.Popen("mkdir -p ./" + run_name, shell=True)
create_dir.wait()

# Read model output into data dir
model_output = run_model.stdout.read()
f = open(run_name + "/output.txt", "wb+")
f.write(model_output)

# helper for moving files
def move_file(f):
    f = os.path.basename(f)
    shutil.move("../MOM6-examples/ocean_only/" + run_name + "/" + f,
                "./" + run_name + "/" + f)


# collect and move all data for run
run_dir_glob = "../MOM6-examples/ocean_only/" + run_name + "/*"
for f in glob.glob(run_dir_glob):
    # MOM_parameter_doc.
    if f.endswith(".short") or f.endswith(".short") or f.endswith(".layout"):
        move_file(f)
    # logs of run
    elif f.startswith("logfile"):
        move_file(f)
    elif f.startswith("available_diags"):
        move_file(f)
    elif f == "ocean.stats":
        move_file(f)
    # Diagnostic table
    elif f == "diag_table":
        move_file(f)
    # all netCDF data
    elif f.endswith(".nc"):
        move_file(f)

