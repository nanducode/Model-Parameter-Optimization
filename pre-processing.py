import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def collect_run_data(data_path):
    """Collect all data sets from runs folder"""
    run_data = {}
    months_simmed = 1200
    print("collecting data...")

    # retrieve run dataset for each year of the simulations
    for run in os.listdir(data_path):
        data = xr.open_dataset(data_path + run + '/ocean_mean_month.nc',decode_times=False)
        data_by_month = list(data.groupby("time"))
        for month in range(months_simmed):
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

    for run, state_tensor in state_tensors.items():
        print("processing " + run)
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


    for kh, sl in unaveraged.items():
        print("Averaging samples for " + kh)
        avg_samples[kh] = [pd.concat((sl[x:x+num_years*12])).groupby(level=0).mean()
                           for x in range(years_simmed*12) if x % (num_years * 12) == 0]

    return avg_samples


def normalize_data(state_tensors):
    """Create normal distribution of data in each time averaged sample"""
    for run, sample_list in state_tensors.items():
        print("normalizing " + run)
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
    print("writing to files...")
    for  kh, training_samples in train_data.items():
        for i, sample in enumerate(training_samples):
            path += kh + "_" + str(i) + ".csv"
            sample.to_csv(path, index=False, header=False)
            path = basepath


if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 4:
        print("Usage: python3 pre-processing.py data_dir_path years_simmed time_window")
        print("Example: python3 pre-processing.py /../low-res-with-tracer 100 5")
    else:

        try:
            # columns of each grid point
            state_values = ["dye001", "dye002", "dye003", "stream", "KE"]

            data_path = os.getcwd() + sys.argv[1] + "/"
            if not os.path.isdir(data_path):
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




