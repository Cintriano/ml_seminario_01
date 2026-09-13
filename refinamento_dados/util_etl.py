from tkinter.constants import ROUND
from supabase import create_client, Client
from datetime import timedelta
from pandas import DataFrame
from functools import wraps
from pathlib import Path
import pandas as pd
import time
import json

def leitura_inicial_dados(caminho_str: str, colunas_manter=False, dic_de_tipagem=False, print_flag=False):
    try:
        caminho_arq: str = Path(caminho_str)
        data_frame = pd.read_csv(caminho_arq, sep=";", dtype=str, encoding="latin1")
        data_frame = data_frame[colunas_manter] if colunas_manter is not  False else data_frame
        data_frame = data_frame.astype(dic_de_tipagem) if dic_de_tipagem is not  False else data_frame
        print(data_frame) if print_flag else None
        return data_frame
    except Exception as erro:
        raise erro

def calcula_tempo(func):
    @wraps(func)
    def warpper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fim = time.perf_counter()
        tempo_final = round(fim - inicio, 2)
        if tempo_final <= 60:
            print(f"Tempo de execucao: {tempo_final}s")
        else:
            tempo_final = round(tempo_final / 60, 2)
            print(f"Tempo de execucao: {tempo_final}m")
        return resultado
    return warpper

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

def upsert_dataframe_to_supabase(df: pd.DataFrame, table_name: str, supabase_url: str, supabase_key: str) -> None:
    """
    Envia qualquer DataFrame do Pandas para uma tabela do Supabase utilizando a operação de Upsert.
    :param supabase_url: A URL do seu projeto Supabase.
    :param supabase_key: A chave de API (service_role ou anon) do Supabase.
    """
    # 1. Inicializa o cliente do Supabase com toda a segurança
    supabase: Client = create_client(supabase_url, supabase_key)

    # 2. O segredo da universalidade: convertemos para JSON via Pandas.
    # Isso resolve automaticamente dois grandes problemas:
    # - Transforma colunas de data/hora no formato ISO correto que o PostgreSQL aceita.
    # - Transforma valores nulos (NaN ou NaT) em 'null' nativos do JSON, evitando erros de tipagem.
    dados_json = df.to_json(orient="records", date_format="iso")
    registros = json.loads(dados_json)

    # 3. Executa a operação de upsert em lote
    try:
        resposta = supabase.table(table_name).upsert(registros).execute()
        print(f"Sucesso! {len(registros)} registros foram processados na tabela '{table_name}'.")
        return resposta
    except Exception as e:
        print(f"Erro detectado no envio: {e}")
        raise e

def main():
    # ARQ-03 NT-GER NOTA GERAL
    caminho: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq3.txt"
    dataf_nota_geral = leitura_inicial_dados(caminho, ["NT_GER"], {"NT_GER": "float"})
    # ARQ-29 QE-I23 HORAS DE ESTUDO
    caminho: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq29.txt"
    dataf_horas_estudo = leitura_inicial_dados(caminho, ["QE_I23"], {"QE_I23": "str"})
    # ARQ-14 QE-I08 RENDA FAMILIAR
    caminho: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq14.txt"
    dataf_renda_familiar = leitura_inicial_dados(caminho, ["QE_I08"], {"QE_I08": "str"})
    # ARQ-4 QE-I53 INTERCAMBIO E ESTAGIO
    caminho: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq4.txt"
    dataf_intercambio_estagio = leitura_inicial_dados(caminho, ["QE_I53"], {"QE_I53": "str"})
    # ARQ-23 QE-I17 TIPO ENSINO MEDIO
    caminho: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq23.txt"
    dataf_tipo_ensino_medio = leitura_inicial_dados(caminho, ["QE_I17"], {"QE_I17": "str"})
    # ARQ-26 CO_GRUPO GRUPO
    caminho: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq1.txt"
    dataf_grupo = leitura_inicial_dados(caminho, ["CO_GRUPO"], {"CO_GRUPO": "str"})
    mapeamento_valores = {"4004":"ciencia da computacao", "4006":"sistemas de informacao"}
    dataf_grupo = dataf_grupo.replace({"CO_GRUPO": mapeamento_valores})
    # JUNÇÃO DOS DATA FRAMES
    dataf_completo = juncao([dataf_nota_geral, dataf_horas_estudo, dataf_renda_familiar, dataf_intercambio_estagio, dataf_tipo_ensino_medio, dataf_grupo])
    dataf_refinado = dataf_completo[(dataf_completo["CO_GRUPO"] == "ciencia da computacao") | (dataf_completo["CO_GRUPO"] == "sistemas de informacao")]
    print(dataf_refinado)


if __name__=="__main__":
    main()
    pass