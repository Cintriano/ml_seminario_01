
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from util_etl import leitura_inicial_dados
from sklearn.decomposition import PCA
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def preparar_dados_pca(df: pd.DataFrame) -> pd.DataFrame:
    df_plot = df.copy()

    df_plot['NT_GER_PREVISTA'] = pd.to_numeric(df_plot['NT_GER_PREVISTA'], errors='coerce')

    # 1. Isola as 11 colunas de proporção
    colunas_qe = [col for col in df_plot.columns if col.startswith('QE_I11_')]
    df_pca = df_plot[colunas_qe].fillna(0)  # Proteção contra nulos matemáticos

    # 2. Inicializa e aplica o modelo PCA focado em 1 única dimensão (PC1)
    pca = PCA(n_components=1)
    df_plot['INDICE_PCA_I11'] = pca.fit_transform(df_pca)[:, 0]

    # Extrai o percentual de explicação desse componente para embasamento do TCC
    variancia = pca.explained_variance_ratio_[0] * 100
    print(f"[INFO] O índice PCA resume {variancia:.2f}% de toda a variância das colunas A-K.")

    df_plot = df_plot.dropna(subset=['INDICE_PCA_I11', 'NT_GER_PREVISTA'])
    return df_plot


def plotar_grafico_dispersao(df_plot: pd.DataFrame, nome_arquivo='./plotagens/regressao_pca_i11.png'):
    fig, ax = plt.subplots(figsize=(10, 6.5))

    # Dispersão: Cada ponto é um curso posicionado no seu novo eixo sintético
    sns.scatterplot(
        data=df_plot,
        x='INDICE_PCA_I11',
        y='NT_GER_PREVISTA',
        color='#2a9d8f',  # Um verde azulado elegante para contrastar
        alpha=0.75,
        s=65,
        edgecolor='w',
        linewidth=0.5,
        ax=ax
    )

    # A linha tracejada de tendência calculando a correlação linear do PCA
    sns.regplot(
        data=df_plot,
        x='INDICE_PCA_I11',
        y='NT_GER_PREVISTA',
        scatter=False,
        color='#2b2d42',
        line_kws={'linewidth': 2.5, 'linestyle': '--'},
        ax=ax
    )

    # Rótulos rigorosos e limpos
    ax.set_xlabel('Índice Sintético de Perfil do Curso (1º Componente do PCA)', fontsize=11, fontweight='bold',
                  labelpad=12)
    ax.set_ylabel('Nota Geral Prevista pela IA (NT_GER_PREVISTA)', fontsize=11, fontweight='bold', labelpad=12)

    # Legenda polida
    handles = [Line2D([0], [0], color='#2b2d42', linewidth=2.5, linestyle='--')]
    labels = ['Tendência de Desempenho']
    ax.legend(handles=handles, labels=labels, loc='upper left', frameon=True)

    sns.despine()
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=150, bbox_inches='tight')
    print(f"[INFO] Gráfico do PCA salvo com maestria, senhor: {nome_arquivo}")
    plt.show()




def plotar_painel_regressao(df: pd.DataFrame, nome_arquivo='painel_regressao_i11.png'):
    df_plot = df.copy()

    df_plot['NT_GER_PREVISTA'] = pd.to_numeric(df_plot['NT_GER_PREVISTA'], errors='coerce')
    colunas_qe = [col for col in df_plot.columns if col.startswith('QE_I11_')]

    for col in colunas_qe:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')

    df_plot = df_plot.dropna(subset=['NT_GER_PREVISTA'] + colunas_qe)
    colunas_qe = sorted(colunas_qe)  # Garante que os gráficos sigam a ordem A, B, C... K

    # Configurando uma grade 3x4 (3 linhas, 4 colunas = 12 espaços)
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 12), sharey=True, sharex=True)
    axes = axes.flatten()  # Transforma a matriz em uma lista linear para facilitar o loop

    # Iterando pelas 11 colunas e desenhando um gráfico em cada "quadradinho" da grade
    for i, col in enumerate(colunas_qe):
        ax = axes[i]
        letra = col.replace('QE_I11_', '')  # Extrai apenas a letra da opção

        # O gráfico de regressão para a opção específica
        sns.regplot(
            data=df_plot,
            x=col,
            y='NT_GER_PREVISTA',
            ax=ax,
            scatter_kws={'alpha': 0.4, 'color': '#023e8a', 's': 25, 'edgecolor': 'w', 'linewidths': 0.5},
            line_kws={'color': '#e76f51', 'linewidth': 2.5, 'linestyle': '--'}
        )

        ax.set_title(f'Opção {letra}', fontsize=12, fontweight='bold', color='#2b2d42')

        # Rótulos limpos: Mostra o Y apenas na 1ª coluna e o X na última linha
        ax.set_ylabel('Nota Prevista' if i % 4 == 0 else '', fontsize=10)
        ax.set_xlabel('Proporção de Alunos' if i >= 7 else '', fontsize=10)
        ax.set_xlim(-0.05, 1.05)  # Mantém o eixo X de 0 a 100% (0 a 1)

    # Como temos 11 gráficos e 12 espaços, o último espaço fica vazio. Precisamos deletá-lo.
    fig.delaxes(axes[11])

    # Polimento visual final da figura
    fig.suptitle('Impacto Isolado de Cada Categoria (QE_I11) no Desempenho Previsto',
                 fontsize=16, fontweight='bold', y=1.02)
    sns.despine()
    plt.tight_layout()

    plt.savefig(nome_arquivo, dpi=200, bbox_inches='tight')
    print(f"[INFO] Painel de regressão com 11 gráficos gerado com sucesso: {nome_arquivo}")
    plt.show()


def exibir_tabela_metricas_regressao(df: pd.DataFrame) -> pd.DataFrame:
    df_calc = df.copy()


    df_calc['NT_GER_PREVISTA'] = pd.to_numeric(df_calc['NT_GER_PREVISTA'], errors='coerce')
    colunas_qe = [col for col in df_calc.columns if col.startswith('QE_I11_')]

    for col in colunas_qe:
        df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce')

    df_calc = df_calc.dropna(subset=['NT_GER_PREVISTA'] + colunas_qe)
    colunas_qe = sorted(colunas_qe)

    resultados = []

    # O eixo Y (Variável Dependente) é o mesmo para todos os minigráficos
    y_real = df_calc['NT_GER_PREVISTA'].values.reshape(-1, 1)

    for col in colunas_qe:
        # O eixo X (Variável Independente) muda a cada iteração do loop
        x_coluna = df_calc[col].values.reshape(-1, 1)

        # Treina a regressão linear simples idêntica à matemática do sns.regplot
        modelo_lr = LinearRegression()
        modelo_lr.fit(x_coluna, y_real)

        # Gera as predições dessa linha de tendência específica
        y_predito_linha = modelo_lr.predict(x_coluna)

        # Calcula as métricas de erro e ajuste
        r2 = r2_score(y_real, y_predito_linha)
        mae = mean_absolute_error(y_real, y_predito_linha)
        rmse = np.sqrt(mean_squared_error(y_real, y_predito_linha))

        letra = col.replace('QE_I11_', '')
        resultados.append({
            'Opção': letra,
            'R²': round(r2, 4),
            'MAE': round(mae, 4),
            'RMSE': round(rmse, 4)
        })

    df_metricas = pd.DataFrame(resultados)

    # Formatação primorosa para exibição no terminal
    print("\n" + "=" * 50)
    print("   MÉTRICAS DA REGRESSÃO ISOLADA (QE_I11 A-K)")
    print("=" * 50)
    print(df_metricas.to_string(index=False, justify='center'))
    print("=" * 50 + "\n")

    return df_metricas


def main_plot_dispersao(caminho_arq: str, caminho_mdl:str):
    df_plot = leitura_inicial_dados(caminho_arq)
    df_dispersao = preparar_dados_pca(df_plot)
    plotar_grafico_dispersao(df_dispersao)

    df_metricas = exibir_tabela_metricas_regressao(df_plot)
    df_metricas.to_csv("./dados/dados_modelo/tabela_metricas.csv", index=False)
    plotar_painel_regressao(df_plot)

if __name__ == "__main__":
    caminho_arq_dados_prontos = "./dados/dados_modelo/dados_pos_modelo.csv"
    caminho_modelo = "./dados/dados_modelo/rf_regressor.joblib"
    main_plot_dispersao(caminho_arq_dados_prontos, caminho_modelo)