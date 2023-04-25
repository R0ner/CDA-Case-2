import os

import pandas as pd


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
    return df

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.mkdir('data')
    df = get_data()
    df.to_pickle("data/data_df.pkl")