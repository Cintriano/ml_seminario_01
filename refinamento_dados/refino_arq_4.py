from refinamento_dados.util_etl import leitura_inicial_dados, juncao, calcula_tempo, show_df
import pandas as pd
import time
import uuid

def main_refino_arq4(caminho_arq_4: str, caminho_arq_1: str, print_flag: bool = False) -> None:
    dataf_inicial_arq1 = leitura_inicial_dados(caminho_arq_1, ["CO_CURSO", "CO_REGIAO_CURSO", "CO_GRUPO"])
    dataf_filtrado_arq1 = dataf_inicial_arq1.dropna(how="all")
    dataf_filtrado_arq1 = dataf_inicial_arq1[dataf_inicial_arq1["CO_REGIAO_CURSO"] == "1"]
    dataf_filtrado_arq1 = dataf_inicial_arq1[(dataf_inicial_arq1["CO_GRUPO"] == "4004") | (dataf_inicial_arq1["CO_GRUPO"] == "4006")]
    dataf_final_arq1 = dataf_filtrado_arq1["CO_CURSO"]

    dataf_inicial_arq4 = leitura_inicial_dados(caminho_arq_4, dic_de_tipagem={"NU_ANO": "int"})
    dataf_filtrado_arq4 = dataf_inicial_arq4.dropna(how="all")

    dataf_filtrado_arq4 = dataf_filtrado_arq4[
        dataf_filtrado_arq4["CO_CURSO"].isin(dataf_final_arq1)
    ].copy()
    ids_unicos = [str(uuid.uuid4()) for _ in range(len(dataf_filtrado_arq4))]
    dataf_filtrado_arq4.insert(0, "id", ids_unicos)

    pasta_destino = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/Modelo_teste/associacao/arq4_refinado.csv"
    dataf_filtrado_arq4.to_csv(pasta_destino, index=False)
    show_df(dataf_filtrado_arq4) if print_flag else None
    return dataf_filtrado_arq4

if __name__ == "__main__":
    caminho_arq_4: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq4.txt"
    caminho_arq_1: str = "G:/Meu Drive/01_Faculdade/03_Projeto tecnologico/Biblioteca de dados Enade/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq1.txt"
    main_refino_arq4(caminho_arq_4, caminho_arq_1)