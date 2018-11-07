import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from os import listdir, getcwd, mkdir
from os.path import isfile, join, isdir
from sklearn import preprocessing

def collect_run_data(data_path):
    """Collect all data sets from runs folder"""
    run_data = {}
    months_simmed = 1200
    print("collecting data...")

    # retrieve run dataset for each year of the simulations
    for run in listdir(data_path):
        data = xr.open_dataset(data_path + run + '/ocean_mean_month.nc',decode_times=False)
        data_by_month = list(data.groupby("time"))
        # remove first 10 years of the simulation
        for month in range(120, months_simmed):
            run_data[run + "_" + str(month)] = data_by_month[month][1]

    return run_data

def shape_training_data(run_data, state_values):
    """Create state tensors to hold output of the MOM6 model
       state tensor = (lat + long) x len(state_vars)"""

    # get data sample for measurements
    data = run_data[list(run_data.keys())[1]]

    # get number of columns per grid point
    num_state_vars = len(state_values)

    # Dimensions of the data
    layers = len(data.zl)
    latitude = data.yh.size
    longitude = data.xh.size
    grid_points = latitude * longitude
    data_info = (layers, latitude, longitude)

    # Create arrays which will become the state tensor
    state_tensors = dict.fromkeys(run_data.keys())
    for run in run_data.keys():
        state_tensors[run] = np.zeros((grid_points, num_state_vars * layers))

    return state_tensors, data_info



def create_training_samples(data_path, state_values):
    """time average run data and place into state tensors
       outputs dictionary of state tensors for training"""

    # collect data from run
    run_data = collect_run_data(data_path)

    # get state tensors for each run to hold training data
    state_tensors, data_info = shape_training_data(run_data, state_values)
    layers = data_info[0]
    grid_points = data_info[1] * data_info[2]


    # Calculate zonal streamfunction
    for run in run_data.keys():
        data = run_data[run]
        run_data[run]["stream"] = data.vh.cumsum('xh')

    print("processing...")
    for run, state_tensor in state_tensors.items():
        # Loop over all state variables to create state tensor
        KH = run.split("_")[2]
        data = run_data[run]
        ncol = 0
        for var in state_values:
            for layer in range(0, layers):
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
        vis = name.split("_")[2]
        unaveraged[vis].append(sample)

    print("averaging...")
    for kh, sl in unaveraged.items():
        avg_samples[kh] = [pd.concat((sl[x:x+num_years*12])).groupby(level=0).mean()
                           for x in range(years_simmed*12) if x % (num_years * 12) == 0]

    return avg_samples


def normalize_data(state_tensors):
    """Create normal distribution of data in each time averaged sample"""
    print("normalizing...")
    for run, sample_list in state_tensors.items():
        for state_tensor in sample_list:
            min_max_scaler = preprocessing.MinMaxScaler()
            np_scaled = min_max_scaler.fit_transform(state_tensor)
            state_tensor = pd.DataFrame(np_scaled)
    return state_tensors


def write_datasets(train_data):
    basepath = getcwd() +  "/data/"
    mkdir(basepath)
    path = basepath
    print("writing to files...")
    for  kh, training_samples in train_data.items():
        for i, sample in enumerate(training_samples):
            path += kh + "_" + str(i) + ".csv"
            sample.to_csv(path, index=False)
            path = basepath


def get_training_data(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    train_targets = []
    train_data = []
    test_targets = []
    test_data = []
    counter = 1
    for f in onlyfiles:
        KH = f.split("_")[0]
        dataset = pd.read_csv(path + f)
        if counter != 8:
            train_targets.append(int(KH))
            train_data.append(np.array(dataset, ndmin=2))
            counter += 1
        else:
            test_targets.append(int(KH))
            test_data.append(np.array(dataset, ndmin=2))
            counter = 1

    # put into numpy arrays
    train_data = np.array(train_data, ndmin=3)
    test_data = np.array(test_data, ndmin=3)
    train_targets = np.array(train_targets)
    test_targets = np.array(test_targets)

    # normalize targets
    min_max_scaler = preprocessing.MinMaxScaler()
    train_scaled = min_max_scaler.fit_transform(train_targets.reshape(-1, 1))
    test_scaled = min_max_scaler.fit_transform(test_targets.reshape(-1, 1))
    train_targets = train_scaled
    test_targets = test_scaled

    # randomly permute training data
    p = np.random.permutation(len(train_data))
    train_data = train_data[p]
    train_targets = train_targets[p]

    return train_data, train_targets, test_data, test_targets


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

        training_samples = create_training_samples(data_path, state_values)
        averaged_state_tensors = average_by_year(time_window, years_simmed, training_samples)
        normalized_state_tensors = normalize_data(averaged_state_tensors)
        write_datasets(normalized_state_tensors)

        print("--- %s minutes ---" % ((time.time() - start_time)/60))



