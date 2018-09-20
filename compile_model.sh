
#!/bin/sh


# Compile Flexible Model System
mkdir -p ../MOM6-examples/build/intel/shared/repro

(cd ../MOM6-examples/build/intel/shared/repro/; rm -f path_names; ../../../../src/mkmf/bin/list_paths -l ../../../../src/FMS; \
../../../../src/mkmf/bin/mkmf -t ../../../../src/mkmf/templates/sam-linux-gnu.mk \
-p libfms.a -c '-Duse_libMPI -Duse_netCDF -DSPMD' path_names)

(cd ../MOM6-examples/build/intel/shared/repro/; make NETCDF=3 REPRO=1 libfms.a)

# Compile MOM6 model
mkdir -p ../MOM6-examples/build/intel/ocean_only/repro/

(cd ../MOM6-examples/build/intel/ocean_only/repro/; rm -f path_names; \
 ../../../../src/mkmf/bin/list_paths -l ./ ../../../../src/MOM6/{config_src/dynamic,config_src/solo_driver,src/{*,*/*}}/ ; \
 ../../../../src/mkmf/bin/mkmf -t ../../../../src/mkmf/templates/sam-linux-gnu.mk -o '-I../../shared/repro' -p MOM6 -l '-L../../shared/repro -lfms' -c '-Duse_libMPI -Duse_netCDF -DSPMD' path_names)

(cd ../MOM6-examples/build/intel/ocean_only/repro/; make NETCDF=3 REPRO=1 MOM6)


