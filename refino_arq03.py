from util_etl import leitura_inicial_dados, show_df
import uuid

def main_refino_arq3(caminho_arq_3: str, caminho_arq_1: str, print_flag: bool = False) -> None:
    dataf_inicial_arq1 = leitura_inicial_dados(caminho_arq_1, ["CO_CURSO", "CO_REGIAO_CURSO", "CO_GRUPO"])
    dataf_filtrado_arq1 = dataf_inicial_arq1.dropna(how="all")
    dataf_filtrado_arq1 = dataf_inicial_arq1[dataf_inicial_arq1["CO_REGIAO_CURSO"] == "1"]
    dataf_filtrado_arq1 = dataf_inicial_arq1[(dataf_inicial_arq1["CO_GRUPO"] == "4004") | (dataf_inicial_arq1["CO_GRUPO"] == "4006")]
    dataf_final_arq1 = dataf_filtrado_arq1["CO_CURSO"]

    dic_tipagem = {
        # Novas colunas adicionadas da imagem
        "NU_ITEM_OFG": "int",
        "NU_ITEM_OFG_Z": "int",
        "NU_ITEM_OFG_X": "int",
        "NU_ITEM_OFG_N": "int",
        "NU_ITEM_OCE": "int",
        "NU_ITEM_OCE_Z": "int",
        "NU_ITEM_OCE_X": "int",
        "NU_ITEM_OCE_N": "int",

        # Colunas de notas anteriores
        "NT_GER": "float",
        "NT_FG": "float",
        "NT_OBJ_FG": "float",
        "NT_DIS_FG": "float",
        "NT_FG_D1": "float",
        "NT_FG_D1_PT": "float",
        "NT_FG_D1_CT": "float",
        "NT_FG_D2": "float",
        "NT_FG_D2_PT": "float",
        "NT_FG_D2_CT": "float",
        "NT_CE": "float",
        "NT_OBJ_CE": "float",
        "NT_DIS_CE": "float",
        "NT_CE_D1": "float",
        "NT_CE_D2": "float",
        "NT_CE_D3": "float"
    }

    dataf_inicial_arq3 = leitura_inicial_dados(caminho_arq_3, dic_de_tipagem=dic_tipagem)
    dataf_filtrado_arq3 = dataf_inicial_arq3.dropna(how="all")

    dataf_filtrado_arq3 = dataf_filtrado_arq3[
        dataf_filtrado_arq3["CO_CURSO"].isin(dataf_final_arq1)
    ].copy()
    ids_unicos = [str(uuid.uuid4()) for _ in range(len(dataf_filtrado_arq3))]
    dataf_filtrado_arq3.insert(0, "id", ids_unicos)

    pasta_destino = "./dados/filtrados/microdados2021_arq3.txt"
    dataf_filtrado_arq3.to_csv(pasta_destino, index=False, sep=";")

    show_df(dataf_filtrado_arq3) if print_flag else None

if __name__ == "__main__":
    caminho_arq_3: str = "./dados/fonte_dados/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq3.txt"
    caminho_arq_1: str = "./dados/fonte_dados/microdados_Enade_2021_LGPD/2.DADOS/microdados2021_arq1.txt"
    main_refino_arq3(caminho_arq_3, caminho_arq_1)