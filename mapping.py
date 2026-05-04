
from itertools import combinations
import pandas as pd

df_base = pd.read_csv('data/test_.csv')

graus = sorted(['GEI', 'GEMCD', 'GEXT', 'GESA'])
professors = df_base['ProfessorNom'].unique()

professors_counts_df = pd.DataFrame({'ProfessorNom': professors})

for i in range(1, len(graus) + 1):
    for combination_tuple in combinations(graus, i):
        combination_list = sorted(list(combination_tuple))
        combination_str = "_".join(combination_list).lower()
        mask = df_base['GrauCodi'].isin(combination_list)
        df_filtrat = df_base[mask]
        counts = df_filtrat.groupby('ProfessorNom')['AssignaturaNom'].nunique().reset_index()
        counts.columns = ['ProfessorNom', combination_str]
        professors_counts_df = professors_counts_df.merge(counts, on='ProfessorNom', how='left').fillna(0)
        professors_counts_df[combination_str] = professors_counts_df[combination_str].astype(int)

professors_counts_df.to_csv('professors_combinacions.csv', index=False)