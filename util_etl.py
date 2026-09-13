from pandas import DataFrame
from pathlib import Path
import pandas as pd

def leitura_inicial_dados(caminho_str: str, colunas_manter=False, dic_de_tipagem=False, print_flag=False):
    try:
        caminho_arq: str = Path(caminho_str)
        data_frame = pd.read_csv(caminho_arq, dtype=str, sep=";", encoding="latin1")
        data_frame = data_frame[colunas_manter] if colunas_manter is not  False else data_frame
        data_frame = data_frame.astype(dic_de_tipagem) if dic_de_tipagem is not  False else data_frame
        print(data_frame) if print_flag else None
        return data_frame
    except Exception as erro:
        raise erro

def show_df(dataf: pd.DataFrame):
    dataf.describe()

    print(f"{dataf.head()}\n"
          f"{20 * "-"}\n"
          f"{dataf.info()}\n"
          f"{20 * "-"}\n"
          f"{dataf.describe()}")

def juncao(dataf_1: DataFrame, dataf_2: DataFrame, coluna_juncao: str, print_flag=False) -> DataFrame:
    try:
        dataf_merged = dataf_1.merge(dataf_2, on=coluna_juncao, how="inner")
        print(dataf_merged) if print_flag else None
        return dataf_merged
    except Exception as erro:
        raise erro


if __name__=="__main__":
    pass