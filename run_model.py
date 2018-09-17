
import sys
import subprocess

# TODO: get running
#       capture output
#       flexible filepaths
#       come up with dir naming system
#       compile and run multicore
#       iterate over multiple runs
#       encapsulate as functions.

# copy start directory into a new directory
create_dir = subprocess.Popen("cp -r ../MOM6-examples/ocean_only/double_gyre_start ../MOM6-examples/ocean_only/double_gyre",
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
compile_MOM.wait()


# Setup restart for run
create_restart = subprocess.Popen("mkdir -p ../MOM6-examples/ocean_only/double_gyre/RESTART",
                                  shell=True)
create_restart.wait()


# Run the model
run_model = subprocess.Popen("mpirun ../../build/intel/ocean_only/repro/MOM6",
                             shell=True,
                             cwd="../MOM6-examples/ocean_only/double_gyre")
run_model.wait()


