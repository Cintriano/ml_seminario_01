from util_etl import leitura_inicial_dados, show_df
import uuid

def main_refino_arq17(caminho_arq_17: str, caminho_arq_1: str, print_flag: bool = False) -> None:
    dataf_inicial_arq1 = leitura_inicial_dados(caminho_arq_1, ["CO_CURSO", "CO_REGIAO_CURSO", "CO_GRUPO"])
    dataf_filtrado_arq1 = dataf_inicial_arq1.dropna(how="all")
    dataf_filtrado_arq1 = dataf_inicial_arq1[dataf_inicial_arq1["CO_REGIAO_CURSO"] == "1"]
    dataf_filtrado_arq1 = dataf_inicial_arq1[(dataf_inicial_arq1["CO_GRUPO"] == "4004") | (dataf_inicial_arq1["CO_GRUPO"] == "4006")]
    dataf_final_arq1 = dataf_filtrado_arq1["CO_CURSO"]

    dataf_inicial_arq17 = leitura_inicial_dados(caminho_arq_17, dic_de_tipagem={"NU_ANO": "int"})
    dataf_filtrado_arq17 = dataf_inicial_arq17.dropna(how="all")

    dataf_filtrado_arq17 = dataf_filtrado_arq17[
        dataf_filtrado_arq17['CO_CURSO'].isin(dataf_final_arq1)
    ].copy()
    ids_unicos = [str(uuid.uuid4()) for _ in range(len(dataf_filtrado_arq17))]
    dataf_filtrado_arq17.insert(0, "id", ids_unicos)

    pasta_destino = "./dados/filtrados/microdados2021_arq17.txt"
    dataf_filtrado_arq17.to_csv(pasta_destino, index=False, sep=";")
    show_df(dataf_filtrado_arq17) if print_flag else None


if __name__ == "__main__":
    caminho_arq_17: str = "./dados/fonte_dados/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq17.txt"
    caminho_arq_1: str = "./dados/fonte_dados/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq1.txt"
    main_refino_arq17(caminho_arq_17, caminho_arq_1)