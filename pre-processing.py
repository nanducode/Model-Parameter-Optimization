import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

def collect_run_data(data_path):
    """Collect all data sets from runs folder"""
    run_data = {}

    # retrieve monthly run dataset
    for run in os.listdir(data_path):
        run_data[run] = xr.open_dataset(data_path + run + '/ocean_mean_month.nc',decode_times=False)

    return run_data

def shape_training_data(run_data):
    """Create state tensors to hold output of the MOM6 model
       state tensor = (lat + long) x len(state_vars)"""

    # get data sample for measurements
    data = run_data[list(run_data.keys())[1]]

    # define state_tensor
    state_vars = ["dye001", "dye002", "dye003", "stream", "KE"]
    num_state_vars = len(state_vars)

    # Dimensions of the data
    layers = len(data.zl)
    latitude = data.yh.size
    longitude = data.xh.size
    grid_points = latitude * longitude
    data_info = (state_vars, layers, latitude, longitude)

    # Create arrays which will become the state tensor
    state_tensors = dict.fromkeys(run_data.keys())
    for run in run_data.keys():
        state_tensors[run] = np.zeros((grid_points, num_state_vars * layers))

    return state_tensors, data_info


def normalize_data(state_tensors):
    """Create normal distribution of data and put into pandas dataframe"""
    import pandas as pd
    for run, state_tensor in state_tensors.items():
        df = pd.DataFrame(state_tensor)
        mean = df.mean(axis=0)
        df -= mean
        std = df.std(axis=0)
        df /= std
        state_tensors[run] = df
    return state_tensors


def create_training_samples(data_path):
    """time average run data and place into state tensors
       outputs dictionary of normalized state tensors for training"""

    # collect data from run
    run_data = collect_run_data(data_path)

    # get state tensors for each run to hold training data
    state_tensors, data_info = shape_training_data(run_data)
    state_vars = data_info[0]
    layers = data_info[1]
    grid_points = data_info[2] * data_info[3]

    # Define indices for time averaging
    t0 = 12
    tf = -1

    # Calculate zonal streamfunction
    for run in run_data.keys():
        data = run_data[run]
        run_data[run]["stream"] = data.vh.cumsum('xh')

    for run, state_tensor in state_tensors.items():
    # Loop over all state variables to create state tensor
        data = run_data[run]
        ncol = 0
        for var in state_vars:
            for layer in range(0, layers):
                # Average the data in time (note that )
                state_tensor[:,ncol] = np.array(data[var][t0:tf,:,:,:].mean('time')[layer,:,:]).reshape(grid_points)
                ncol += 1

    nomalized_state_tensors = normalize_data(state_tensors)
    return state_tensors


path = "/Users/spartee/Dropbox/Professional/Cray/399-Thesis/low-res-3yr/"
print(list(create_training_samples(path).values())[1])

