import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from util_etl import leitura_inicial_dados

def preparar_dados_colunas(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Isola as colunas geradas pelo get_dummies
    colunas_qe = [col for col in df.columns if col.startswith('QE_I11_')]

    # 2. O Unpivot (Melt): Transforma as colunas em linhas
    df_melt = df.melt(
        id_vars=['CO_CURSO', 'NT_GER', 'NT_GER_PREVISTA', 'QT_ALUNOS'],
        value_vars=colunas_qe,
        var_name='Categoria',
        value_name='Proporcao'
    )

    # Limpa o nome da categoria para deixar apenas a letra (Ex: 'QE_I11_A' -> 'A')
    df_melt['Categoria'] = df_melt['Categoria'].str.replace('QE_I11_', '')

    df_melt['QT_ALUNOS'] = pd.to_numeric(df_melt['QT_ALUNOS'], errors='coerce')
    df_melt['Proporcao'] = pd.to_numeric(df_melt['Proporcao'], errors='coerce')
    df_melt['NT_GER_PREVISTA'] = pd.to_numeric(df_melt['NT_GER_PREVISTA'], errors='coerce')
    df_melt['NT_GER'] = pd.to_numeric(df_melt['NT_GER'], errors='coerce')

    # 3. Calcula o número absoluto de alunos naquela categoria específica
    df_melt['Alunos_Estimados'] = df_melt['QT_ALUNOS'] * df_melt['Proporcao']

    # Removemos linhas zeradas para não causar divisão por zero no cálculo de pesos
    df_melt = df_melt[df_melt['Alunos_Estimados'] > 0]

    # 4. Agrupa as categorias calculando a média ponderada exata
    df_agrupado = df_melt.groupby('Categoria').apply(
        lambda x: pd.Series({
            'Nota_Prevista_Ponderada': np.average(x['NT_GER_PREVISTA'], weights=x['Alunos_Estimados']),
            'Nota_Real_Ponderada': np.average(x['NT_GER'], weights=x['Alunos_Estimados']),
            'Total_Alunos': x['Alunos_Estimados'].sum()
        })
    ).reset_index()

    return df_agrupado


def plotar_grafico_colunas(df_plot: pd.DataFrame, nome_arquivo='./plotagens/grafico_barras.png'):
    fig, ax = plt.subplots(figsize=(10, 6.5))

    # Gráfico de barras usando a nota prevista ponderada
    sns.barplot(
        data=df_plot,
        x='Categoria',
        y='Nota_Prevista_Ponderada',
        hue='Categoria',
        legend=False,
        palette='mako',
        edgecolor='#2b2d42',
        linewidth=1.2,
        ax=ax
    )

    # Rótulos com formatação polida
    ax.set_xlabel('Opção do Questionário (QE_I11)', fontsize=11, fontweight='bold', labelpad=12)
    ax.set_ylabel('Nota Geral Média Prevista (Ponderada)', fontsize=11, fontweight='bold', labelpad=12)

    # Ajuste de limite do eixo Y para destacar as diferenças (opcional, ajustável)
    ax.set_ylim(df_plot['Nota_Prevista_Ponderada'].min() * 0.85,
                df_plot['Nota_Prevista_Ponderada'].max() * 1.05)

    # Adiciona os valores exatos em cima de cada barra
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.1f}",
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color='#2b2d42', xytext=(0, 5),
                    textcoords='offset points')

    sns.despine()
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=150, bbox_inches='tight')
    print(f"[INFO] Gráfico de colunas salvo em: {nome_arquivo}")
    plt.show()

def main_plot_colunas(caminho_arq: str):
    df_plot = leitura_inicial_dados(caminho_arq)
    df_colunas = preparar_dados_colunas(df_plot)
    plotar_grafico_colunas(df_colunas)

if __name__ == "__main__":
    caminho_arq_dados_prontos = "./dados/dados_modelo/dados_pos_modelo.csv"
    main_plot_colunas(caminho_arq_dados_prontos)