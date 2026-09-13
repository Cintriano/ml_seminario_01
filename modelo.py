from sklearn.linear_model import LinearRegression
from util_etl import leitura_inicial_dados, show_df
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from pandas import DataFrame
import pandas as pd
import numpy as np
import warnings
import joblib
import os

# Silencia os avisos internos do Supabase
warnings.filterwarnings("ignore", category=DeprecationWarning, module="supabase")

def preparar_dados_regressao(df_arq3: DataFrame, df_arq17: DataFrame, print_flag=False) -> DataFrame:
    """
    Trata as bases de dados realizando o mapeamento de variáveis ordinais,
    limpeza de ruídos (ausências/zeros) e agregando-as por média a nível de curso (CO_CURSO).
    """
    # 1. ========== Arquivo 3 (Notas de Desempenho) ==========
    df_arq3_limpo = df_arq3[['CO_CURSO', 'NT_GER']].copy()
    df_arq3_limpo['NT_GER'] = pd.to_numeric(df_arq3_limpo['NT_GER'], errors='coerce') # Tipagem
    # Filtro: Removemos valores nulos e notas zero
    df_arq3_limpo = df_arq3_limpo[(df_arq3_limpo['NT_GER'].notna()) & (df_arq3_limpo['NT_GER'] > 0)]
    # Calculo da média da nota por curso
    df_arq3_agg = df_arq3_limpo.groupby('CO_CURSO').agg(
        NT_GER=('NT_GER', 'mean'),
        QT_ALUNOS=('NT_GER', 'count')  # Esta é a nova âncora de peso!
    ).reset_index()

    # 2. ========== Arquivo 17 ==========
    df_arq17_limpo = df_arq17[['CO_CURSO', 'QE_I11']].dropna().copy()
    # Padronização de strings para evitar duplicação de categorias
    df_arq17_limpo['QE_I11'] = df_arq17_limpo['QE_I11'].astype(str).str.strip().str.upper()
    # Codificação da variável para números binários
    df_arq17_dummies = pd.get_dummies(df_arq17_limpo, columns=['QE_I11'], dtype=int)
    df_arq17_agg = df_arq17_dummies.groupby('CO_CURSO').mean().reset_index()

    # 5. InnerJoin dos Dataframes
    df_consolidado = df_arq3_agg.merge(df_arq17_agg, on='CO_CURSO', how='inner')
    show_df(df_consolidado) if print_flag else None
    return df_consolidado


def treinar_e_salvar_modelo(df_consolidado: DataFrame, fatia_treino: float = 0.2,
                            caminho_modelo: str = 'rf_regressor2.joblib', teste_par: bool=False, teste_mdl: bool=False):
    """
    Prepara os dados, treina o Random Forest e salva (serializa) a IA no disco.
    """
    x = df_consolidado.drop(columns=['CO_CURSO', 'NT_GER', 'QT_ALUNOS'])
    y = df_consolidado['NT_GER']
    pesos = df_consolidado['QT_ALUNOS']

    X_train, X_test, y_train, y_test, pesos_train, pesos_test = train_test_split(
        x, y, pesos, test_size=fatia_treino, random_state=42
    )

    teste_de_parametros(X_train, y_train, X_test, y_test, pesos_train) if teste_par else None

    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=1,
        random_state=42
    )
    rf_model.fit(X_train, y_train, sample_weight=pesos_train)

    comparar_algoritmos(X_train, y_train, X_test, y_test, pesos_train)

    avaliar_modelo(rf_model, X_test, y_test) if teste_mdl else None

    # Cria a pasta caso ela não exista e salva o modelo
    os.makedirs(os.path.dirname(caminho_modelo), exist_ok=True)
    joblib.dump(rf_model, caminho_modelo)
    print(f"[INFO] Inteligência Artificial treinada e salva em: {caminho_modelo}")
    return rf_model


def aplicar_modelo(df_consolidado: DataFrame, caminho_modelo: str = 'modelos/rf_regressor.joblib', print_flag=False):
    """
    Carrega o modelo do disco e aplica aos dados para gerar a nova coluna de predições.
    """
    # Carrega a IA da memória do disco
    rf_model = joblib.load(caminho_modelo)

    x = df_consolidado.drop(columns=['CO_CURSO', 'NT_GER', 'QT_ALUNOS'])

    df_pos_treino = df_consolidado.copy()
    df_pos_treino['NT_GER_PREVISTA'] = rf_model.predict(x)

    show_df(df_pos_treino) if print_flag else None
    return rf_model, df_pos_treino


def teste_de_parametros(X_train, y_train, X_test, y_test, pesos_train):
    print("Iniciando teste...")
    # 1. O Menu de Ajustes (Hiperparâmetros para testar)
    parametros_grid = {
        'n_estimators': [50, 100, 200],  # Quantidade de árvores na floresta
        'max_depth': [None, 5, 10, 15],  # Profundidade (ajuda a evitar o overfitting)
        'min_samples_split': [2, 5, 10],  # Mínimo de cursos para criar uma nova regra
        'min_samples_leaf': [1, 2, 4]  # Mínimo de cursos no resultado final da regra
    }

    # 2. Configurando o provador automático (GridSearch)
    grid_search = GridSearchCV(
        estimator=RandomForestRegressor(random_state=42),
        param_grid=parametros_grid,
        scoring='neg_root_mean_squared_error',
        cv=5,
        n_jobs=-1
    )

    grid_search.fit(X_train, y_train, sample_weight=pesos_train)
    melhor_rf = grid_search.best_estimator_

    print("\n[INFO] === RESULTADO ===")
    print(f"Melhores parâmetros encontrados: {grid_search.best_params_}")

    return melhor_rf


def avaliar_modelo(modelo, X_test, y_test):
    """
    Recebe o modelo treinado e os dados de teste, realiza as predições
    internamente e exibe as métricas e a importância das variáveis.
    """
    # 1. A IA faz a prova usando os dados que ela nunca viu (X_test)
    y_previsto = modelo.predict(X_test)

    # 2. Comparamos as respostas da IA (y_previsto) com o gabarito real (y_test)
    r2 = r2_score(y_test, y_previsto)
    mae = mean_absolute_error(y_test, y_previsto)
    rmse = np.sqrt(mean_squared_error(y_test, y_previsto))

    print("\n" + "="*45)
    print("   RESULTADOS DA AVALIAÇÃO DO MODELO")
    print("="*45)
    print(f"R² (Poder explicativo): {r2:.4f}")
    print(f"MAE (Erro absoluto médio): {mae:.4f}")
    print(f"RMSE (Erro médio penalizado): {rmse:.4f}")

    # 3. Extrai o peso das variáveis automaticamente
    if hasattr(modelo, 'feature_importances_'):
        importancias = pd.Series(modelo.feature_importances_, index=X_test.columns)
        top_variaveis = importancias.sort_values(ascending=False)

        print("\n=== PESO REAL DAS VARIÁVEIS NO DESEMPENHO ===")
        print(top_variaveis.to_string())
    print("="*45 + "\n")


def comparar_algoritmos(X_train, y_train, X_test, y_test, pesos_train):
    """
    Treina o Random Forest e a Regressão Linear simultaneamente,
    compara as métricas de erro e declara o vencedor.
    """
    print("\n" + "=" * 30)
    print("   RANDOM FOREST vs LINEAR")
    print("=" * 30)

    # 1. Oponente 1: O seu Random Forest tunado
    rf_model = RandomForestRegressor(
        n_estimators=200, max_depth=5, min_samples_split=10, min_samples_leaf=1, random_state=42
    )
    rf_model.fit(X_train, y_train, sample_weight=pesos_train)
    rf_preds = rf_model.predict(X_test)

    rf_r2 = r2_score(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))

    # 2. Oponente 2: Regressão Linear Clássica
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train, sample_weight=pesos_train)
    lr_preds = lr_model.predict(X_test)

    lr_r2 = r2_score(y_test, lr_preds)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_preds))

    # 3. Exibindo o Placar
    print(f"[Random Forest]    R²: {rf_r2:.4f}  |  RMSE: {rf_rmse:.4f}")
    print(f"[Regressão Linear] R²: {lr_r2:.4f}  |  RMSE: {lr_rmse:.4f}")


def main_modelo(caminho_arq_3, caminho_arq_17, flag_exe_treino=False):
    print("Iniciando modelo...")
    df_arq3 = leitura_inicial_dados(caminho_arq_3)
    df_arq17 = leitura_inicial_dados(caminho_arq_17)

    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_do_modelo = os.path.join(diretorio_atual, 'dados/dados_modelo/rf_regressor.joblib')

    print("Preparando e agregando a base...")
    df_preparado = preparar_dados_regressao(df_arq3, df_arq17)
    df_preparado.to_csv("./dados/dados_modelo/dados_transformados.csv", index=False, sep=";")

    treinar_e_salvar_modelo(df_preparado, 0.2, caminho_do_modelo) if flag_exe_treino else None

    print("Aplicando os dados no modelo...\n")
    modelo_treinado, df_pos_treino = aplicar_modelo(df_preparado, caminho_modelo=caminho_do_modelo)
    df_pos_treino.to_csv("./dados/dados_modelo/dados_pos_modelo.csv", index=False, sep=";")


    print("\nPipeline finalizado com sucesso!")


if __name__ == "__main__":
    caminho_arq_17: str = "./dados/filtrados/microdados2021_arq17.txt"
    caminho_arq_3: str = "./dados/filtrados/microdados2021_arq3.txt"

    main_modelo(caminho_arq_3, caminho_arq_17, True)