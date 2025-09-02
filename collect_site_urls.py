import pandas as pd
import os
import multiprocessing
import numpy as np
import configparser
from functools import partial


def get_file(name, folder, path, worker):
    return_string = f"{path}/raw/{folder}_{worker}/{name}.csv"
    return return_string

def check_404(file):
    with open(file, "r", encoding="utf-8") as text_file:
            if ("Valaki valahol elrontott valamit." in text_file.read()):
                return True
    return False

def row_function(row, path):
    address = get_file(row["file"], row["folder"], path, row["source"])
    return check_404(address)

def process_chunk(df_chunk, path):
    df_chunk['problem'] = df_chunk.apply(row_function, axis=1, path=path)
    return df_chunk

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    SITE_NAME = config['collect_site_urls']['SITE_NAME']
    INPUT_PATH = config['collect_site_urls']['INPUT_PATH']
    NUM_WORKERS = config.getint('collect_site_urls', 'NUM_WORKERS')
    df_list = []
    all_urls = pd.DataFrame()
    file_list = os.listdir("output/")
    for file in file_list:
        if len(file) > len("results.csv") and file[0:7] == "results":
            df = pd.read_csv(INPUT_PATH + file, delimiter=";",
                            names=["file", "folder", "url"])
            df["source"] = file[7:8]
            df_list.append(df)
    all_urls = pd.concat(df_list, ignore_index=True)
    df = all_urls[all_urls["url"].str.contains(SITE_NAME, na=False)]
    df_split = np.array_split(df, NUM_WORKERS)
    with multiprocessing.Pool(NUM_WORKERS) as pool:
        result_chunks = pool.map(partial(process_chunk, path=INPUT_PATH), df_split)
    df_result = pd.concat(result_chunks)
    df_result.to_csv("Articles.csv", index=False)
