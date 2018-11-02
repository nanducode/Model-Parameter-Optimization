import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def collect_run_data(data_path):
    """Collect all data sets from runs folder"""
    run_data = {}
    months_simmed = 120

    # retrieve run dataset for each year of the simulations
    for run in os.listdir(data_path):
        data = xr.open_dataset(data_path + run + '/ocean_mean_month.nc',decode_times=False)
        data_by_month = list(data.groupby("time"))
        for month in range(months_simmed):
            run_data[run + "_" + str(month)] = data_by_month[month][1]

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



def create_training_samples(data_path):
    """time average run data and place into state tensors
       outputs dictionary of state tensors for training"""

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
                # [t0:tf,:,:,:].mean('time')
                state_tensor[:,ncol] = np.array(data[var][layer,:,:]).reshape(grid_points)
                ncol += 1

        state_tensors[run] = pd.DataFrame(state_tensor)

    return state_tensors


def average_by_year(num_years, years_simmed, training_samples):
    """Takes in training samples to be averaged by num years of simulation
       Returns a dictionary of KH : [samples_averaged_by_year]"""
    KH = set([x.split("_")[2] for x in training_samples.keys()])
    unaveraged = dict.fromkeys(KH, [])
    avg_samples = dict.fromkeys(KH, [])
    for name, sample in training_samples.items():
        for vis in KH:
            if vis in name:
                unaveraged[vis].append(sample)

    for kh, sl in unaveraged.items():
        avg_samples[kh] = [pd.concat((sl[x:x+num_years*12])).groupby(level=0).mean()
                           for x in range(years_simmed*12) if x % (num_years * 12) == 0]

    return avg_samples


def normalize_data(state_tensors):
    """Create normal distribution of data in each time averaged sample"""
    for run, sample_list in state_tensors.items():
        for state_tensor in sample_list:
            mean = state_tensor.mean(axis=0)
            state_tensor -= mean
            std = state_tensor.std(axis=0)
            state_tensor /= std
    return state_tensors


def write_datasets(train_data):
    basepath = os.getcwd() +  "/data/"
    os.mkdir(basepath)
    path = basepath
    for  kh, training_samples in train_data.items():
        for i, sample in enumerate(training_samples):
            path +=  kh + "_" + str(i) + ".csv"
            sample.to_csv(path, index=False, header=False)
            path = basepath


path = "/Users/spartee/Dropbox/Professional/Cray/399-Thesis/low-res-with_tracer/"
training_samples = create_training_samples(path)
averaged_state_tensors = average_by_year(5, 100, training_samples)
normalized_state_tensors = normalize_data(averaged_state_tensors)
write_datasets(normalized_state_tensors)




