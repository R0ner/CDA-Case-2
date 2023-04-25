import os

import numpy as np
import pandas as pd
from scipy import signal


def get_data():
    dir = "data/dataset"
    
    measurements = ["BVP", "EDA", "HR", "TEMP"]
    fields = measurements + ["response", "round", "phase", "participant"]

    # df = pd.DataFrame(columns = cols)
    lengths = dict()
    for m in measurements:
        lengths[m] = list()
    
    data = {field: [] for field in fields}
    index = []
    for root, dirs, files in os.walk(dir):
        if len(dirs) == 0:
            # Split D1_3 into its subsets
            path = root.replace('\\', '/')
            path = path.replace("D1_3/", "")
            path_comp = path.split("/")
            # Assign experiment variables
            cohord, person, round_, phase = path_comp[2:]
            data['participant'].append((cohord, person))
            data['round'].append(round_)
            data['phase'].append(phase)

            # Load responses
            filepath = f"{root}/response.csv"
            responses_df = pd.read_csv(filepath, index_col = 0)
            data['response'].append(responses_df)
            for m in measurements:
                filepath = f"{root}/{m}.csv"
                m_df = pd.read_csv(filepath, index_col = 0) 
                # Convert to datetime
                m_df["time"] = pd.to_datetime(m_df["time"])
                # Make a column for seconds elapsed
                start_time = min(m_df["time"])
                m_df["time_seconds"] = m_df["time"].apply(lambda x: (x - start_time).total_seconds())
                data[m].append(m_df)
    # Convert to pandas dataframe
    df = pd.DataFrame.from_dict(data)

    freqs = {"BVP": 64, "TEMP": 4, "EDA": 4, "HR": 1}

    lengths = []
    m_df_sync = {m: list() for m in measurements}
    for row in range(df.shape[0]):
        time = np.arange(0, 300, 1 / 64)
        for m in measurements:
            m_df = df.loc[row, m]
            series = m_df[m].to_numpy()
            if freqs[m] != 64:
                target_len = int(64 / freqs[m] * len(series))
                series = signal.resample(series, target_len)

            series = series[:time.size]  # Cut off tailing data
            
            if len(series) != time.size:
                diff = time.size - len(series)
                series = np.concatenate((series, np.repeat(series.mean, diff)))
            m_df_sync[m].append(series)
    for m, synched in m_df_sync.items():
        df[f'{m}_synched'] = synched
    return df

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.mkdir('data')
    df = get_data()
    df.to_pickle("data/data_df.pkl")