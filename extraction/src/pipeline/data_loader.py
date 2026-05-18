import pandas as pd
from pathlib import Path
import os
from typing import Optional

def find_csv_dataset():
    project_path = Path().resolve()
    data_path = fr'{project_path}\src\data\in'
    extension = '.csv'
    all_files = os.listdir(data_path)
    csv_files = list(filter(lambda x: x.endswith(extension), all_files))

    return csv_files, [f'{data_path}\{csv}' for csv in csv_files]

def load_data(path):
    try:
        df = pd.read_csv(path, sep=',',low_memory=True)
    except:
        df = pd.concat(pd.read_csv(path, sep=",",
                                   chunksize=100000))
    return df

def save_data(df, name):
    project_path = Path().resolve()
    data_path = fr'{project_path}\src\data\out'
    df.to_csv(fr'{data_path}\{name}_results.csv', index=False)


