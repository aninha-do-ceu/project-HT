import pandas as pd
import numpy as np
from pathlib import Path
import os
from typing import Optional
from sklearn.model_selection import train_test_split

def find_csv_dataset(train: Optional[bool] = False):
    project_path = Path().resolve()
    if train == True:
        data_path = fr'{project_path}\src\data\train\in'
    else:
        data_path = fr'{project_path}\src\data\inference\in'
    extension = '.csv'
    all_files = os.listdir(data_path)
    csv_files = list(filter(lambda x: x.endswith(extension), all_files))

    return csv_files, [f'{data_path}\{csv}' for csv in csv_files]

def load_data(path):
    df = pd.read_csv(path, sep='~')
    # df['embedding'] = df['embedding'].apply(lambda x: string_to_array(x))
    return df

def string_to_array(s):
    s = s.strip()[1:-1]
    float_list = [float(x) for x in s.split()]
    return np.array(float_list, dtype=float)

def split_data_for_train(X, y, test_size, random_state: Optional[int] = 1234):
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=test_size,
                                                        random_state=random_state,
                                                        stratify=y
                                                        )
    return X_train, X_test, y_train, y_test

def save_df(df, df_name, train, embedding_model:Optional[str]=None):
    project_path = Path().resolve()
    if train == True:
        data_path = fr'{project_path}\src\data\train\out'
    else:
        data_path = fr'{project_path}\src\data\inference\out'

    if embedding_model is not None:
        data_path = fr'{data_path}\{embedding_model}'

    df.to_csv(f'{data_path}\df_{df_name}.csv', index=False, sep='~')

def check_or_create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return None
