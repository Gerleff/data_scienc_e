import pandas as pd

DATA_FILE_PATH='data_set_Vic.dta'

if __name__ == '__main__':
    # data = pd.read_stata(DATA_FILE_PATH, convert_categoricals=False)
    # data.to_csv('data_set_Vic.csv', index=False)
    data = pd.read_csv('data_set_Vic.csv', index_col=False)
    df = pd.DataFrame.from_records(data)
    print(df[['um1', 'um2', 'uj10', 'u_age']])
