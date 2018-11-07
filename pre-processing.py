import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from os import listdir, getcwd, mkdir
from os.path import isfile, join, isdir
from sklearn import preprocessing

def collect_run_data(data_path, run):
    """collect the xr dataset for a single run"""
    run_data = {}
    months_simmed = 1200

    run_data = []
    data = xr.open_dataset(data_path + run + '/ocean_mean_month.nc',decode_times=False)
    data_by_month = list(data.groupby("time"))
    for month in range(months_simmed): # edit this to a smaller range for a smaller time window
        run_data.append(data_by_month[month][1])
    return run_data

def shape_training_data(run_data, state_values):
    """Create state tensors to hold output of the MOM6 model
       state tensor = (lat + long) x len(state_vars)"""

    # get data sample for measurements
    data = run_data[0]

    # get number of columns per grid point
    num_state_vars = len(state_values)

    # Dimensions of the data
    layers = len(data.zl)
    latitude = data.yh.size
    longitude = data.xh.size
    grid_points = latitude * longitude
    data_info = (layers, latitude, longitude)

    # Create arrays which will become the state tensor
    state_tensors = []
    for i in range(len(run_data)):
        state_tensors.append(np.zeros((grid_points, num_state_vars * layers)))

    return state_tensors, data_info


def create_training_samples(run_data, state_values):
    """time average run data and place into state tensors
       outputs dictionary of state tensors for training"""

    # get state tensors for each run to hold training data
    state_tensor_list, data_info = shape_training_data(run_data, state_values)
    layers = data_info[0]
    grid_points = data_info[1] * data_info[2]


    # Calculate zonal streamfunction
    for i in range(len(run_data)):
        data = run_data[i]
        run_data[i]["stream"] = data.vh.cumsum('xh')

    for i, data in enumerate(run_data):
        # Loop over all state variables to create state tensor
        state_tensor = state_tensor_list[i]
        ncol = 0
        for var in state_values:
            for layer in range(0, layers):
                state_tensor[:,ncol] = np.array(data[var][layer,:,:]).reshape(grid_points)
                ncol += 1
        state_tensor_list[i] = pd.DataFrame(state_tensor)

    return state_tensor_list



def average_by_year(num_years, years_simmed, state_tensors):
    """Takes in list of state_tensors to be averaged by num years of simulation"""
    averaged_state_tensors = [pd.concat((state_tensors[x:x+num_years*12])).groupby(level=0).mean()
                           for x in range(years_simmed*12) if x % (num_years * 12) == 0]

    return averaged_state_tensors



def normalize_data(state_tensors):
    """Create normal distribution of data in each time averaged sample"""
    normalized_state_tensors = []
    for state_tensor in state_tensors:
        min_max_scaler = preprocessing.MinMaxScaler()
        np_scaled = min_max_scaler.fit_transform(state_tensor)
        normalized_state_tensors.append(pd.DataFrame(np_scaled))
    return normalized_state_tensors


def write_datasets(state_tensors, run):
    kh = run.split("_")[2]
    basepath = getcwd() +  "/data/"
    path = basepath
    for i, tensor in enumerate(state_tensors):
        path += kh + "_" + str(i) + ".csv"
        tensor.to_csv(path, index=False)
        path = basepath


def preprocess_data(path, years_simmed, time_window, state_values):
    for run in listdir(path):
        print("Processing " + run + "...")
        run_data = collect_run_data(path, run)
        filled_state_tensors = create_training_samples(run_data, state_values)
        averaged_state_tensors = average_by_year(time_window, years_simmed, filled_state_tensors)
        normalized_state_tensors = normalize_data(averaged_state_tensors)
        write_datasets(normalized_state_tensors, run)



if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 4:
        print("Usage: python3 preProcessing.py data_dir_path years_simmed time_window")
        print("Example: python3 preProcessing.py ../low-res-with-tracer 100 5")
    else:

        try:
            # columns of each grid point
            state_values = ["dye001", "dye002", "dye003", "stream", "KE"]

            data_path = getcwd() + "/" + sys.argv[1] + "/"
            if not isdir(data_path):
                raise Exception("Data directory not found")

        except Exception as e:
            print(e)

        years_simmed = int(sys.argv[2])
        time_window = int(sys.argv[3])

        # clock pre-processing time
        start_time = time.time()

        mkdir(getcwd() + "/data")

        preprocess_data(data_path, years_simmed, time_window, state_values)

        print("--- %s minutes ---" % ((time.time() - start_time)/60))






