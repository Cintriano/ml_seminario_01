# DIÁRIO DE DECISÕES

## 13/09

Baixamos os dados públicos de alunos estudantes cotistas e bolsistas (Prouni/PIBIC/apoio moradia). O arquivo `microdados2021_arq29.csv` continha 489868 linhas e 3 colunas, sendo elas "NU_ANO", "CO_CURSO", "QE_I23".

## 13/09

Iniciamos a análise exploratória dos dados do Enade 2021. Identificamos os arquivos relacionados às notas de desempenho e às informações do Questionário do Estudante.

O arquivo de desempenho (`arq03`) contém a variável `NT_GER`, utilizada como referência para a nota geral dos estudantes. O arquivo `arq17` contém a variável `QE_I11`, utilizada para representar informações sobre o perfil dos alunos.

## 13/09 

Realizamos o refinamento dos dados para preparar a base para os modelos de aprendizado de máquina.

No arquivo de desempenho, selecionamos as colunas `CO_CURSO` e `NT_GER`, removemos valores nulos e notas iguais a zero e calculamos a média da nota geral por curso.

No arquivo de perfil dos estudantes, selecionamos `CO_CURSO` e `QE_I11`, removemos valores ausentes, padronizamos as categorias e transformamos as respostas em variáveis numéricas.

Em seguida, realizamos a junção dos dois arquivos utilizando `CO_CURSO` como chave. A base resultante contém a média de desempenho e as proporções das categorias de perfil dos estudantes por curso.

## 13/09

Preparamos a base consolidada para o treinamento do modelo de regressão.

A variável `NT_GER` foi definida como alvo, enquanto as proporções das categorias de `QE_I11` foram utilizadas como variáveis explicativas. A quantidade de alunos por curso foi mantida para ser utilizada como peso durante o treinamento.

Dividimos os dados em conjuntos de treinamento e teste, utilizando `test_size=0.2` e `random_state=42`.

## 13/09

Treinamos um modelo Random Forest Regressor para estimar a nota geral média dos cursos a partir das informações de perfil dos estudantes.

O modelo foi configurado com 200 árvores, profundidade máxima de 5 e mínimo de 10 amostras para dividir um nó. Também foi utilizado o número de alunos por curso como peso no treinamento.

## 13/09

Comparamos o Random Forest com um modelo de Regressão Linear para verificar qual abordagem apresenta melhor desempenho.

Utilizamos as métricas R² e RMSE para comparar os modelos. Os resultados dessa comparação serão registrados após a execução dos experimentos.

## 13/09

Realizamos a análise dos resultados do modelo por meio de gráficos de dispersão e regressão.

Também aplicamos PCA às variáveis de perfil dos estudantes para criar um índice sintético e investigar sua relação com a nota geral prevista pelo modelo.

## 13/09

Geramos os arquivos de resultados e visualizações para auxiliar na interpretação do modelo, incluindo a tabela de métricas, os gráficos de barras e os gráficos de dispersão.

Próximo passo: analisar os resultados obtidos e verificar se os dados permitem responder à pergunta inicial sobre a eficácia das bolsas e auxílios estudantis.