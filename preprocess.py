import pandas as pd
import os
from itertools import combinations

BASE_DIR = os.path.dirname(__file__)
DATABASE_PATH = os.path.join(BASE_DIR, "data/professors.xlsx")
TEACHERS_PATH = os.path.join(BASE_DIR, "data/professors.csv")
TEST_PATH = os.path.join(BASE_DIR, "data/test_.csv")

if __name__ == "__main__":
    grau_df = pd.read_excel(DATABASE_PATH, "Grau")
    grau_assignatura_df = pd.read_excel(DATABASE_PATH, "GrauAssignatura")
    assignatura_df = pd.read_excel(DATABASE_PATH, "Assignatura")
    assignatura_professor_df = pd.read_excel(DATABASE_PATH, "AssignaturaProfessor")
    professor_df = pd.read_excel(DATABASE_PATH, "Professor")

    grau_assignatura_professor_df = pd.merge(
        grau_assignatura_df,
        assignatura_professor_df,
    )

    professor_subject_count_df = (
        assignatura_professor_df
        .groupby("ProfessorNom", as_index=False)
        .size()
        .rename(columns={"size": "ProfessorQuantitatAssignatures"})
    )

    professor_subject_ponderation_df = (
        assignatura_professor_df
        .groupby("ProfessorNom", as_index=False)["AssignaturaProfessorPes"]\
        .sum()
    )

    professor_degree_count_df = (
        grau_assignatura_professor_df[["GrauCodi", "ProfessorNom"]]
        .drop_duplicates()
        .groupby("ProfessorNom", as_index=False)
        .size()
        .rename(columns={"size": "ProfessorQuantitatGraus"})
    )

    graus = list(grau_assignatura_professor_df["GrauCodi"].unique())
    for grau in graus:
        grau_assignatura_professor_df[grau] = (
            grau_assignatura_professor_df["GrauCodi"] == grau
        ).astype(int)
    
    # combinations_list = []
    # for i in range(1, len(graus) + 1):
    #     for combination_tuple in combinations(graus, i):
    #         combination_str = "_".join(combination_tuple)
    #         combinations_list.append(combination_str)
    #         grau_assignatura_professor_df[combination_str] = 0
    #         for grau in combination_tuple:
    #             grau_assignatura_professor_df[combination_str] |= (
    #                 grau_assignatura_professor_df["GrauCodi"] == grau
    #             ).astype(int)        

    professor_degrees_df = pd.DataFrame(professor_df["ProfessorNom"])

    # for i in range(1, len(graus) + 1):
    #     for combination_tuple in combinations(graus, i):
    #         combination_list = sorted(list(combination_tuple))
    #         combination_str = "_".join(combination_list).lower()
    #         mask = grau_assignatura_professor_df['GrauCodi'].isin(combination_list)
    #         filtered_df = grau_assignatura_professor_df[mask]
    #         counts = (
    #             filtered_df
    #             .groupby('ProfessorNom')['AssignaturaNom']
    #             .nunique()
    #             .reset_index()
    #         )
    #         counts.columns = ['ProfessorNom', combination_str]
    #         professor_degrees_df = (
    #             professor_degrees_df
    #             .merge(counts, on='ProfessorNom', how='left')
    #             .fillna(0)
    #         )
    #         professor_degrees_df[combination_str] = professor_degrees_df[combination_str].astype(int)

    for i in range(1, len(graus) + 1):
        for combination_tuple in combinations(graus, i):
            combination_list = sorted(list(combination_tuple))
            combination_str = "_".join(combination_list).lower()
            
            mask = grau_assignatura_professor_df['GrauCodi'].isin(combination_list)
            filtered_df = grau_assignatura_professor_df[mask]
            
            unique_assignments = filtered_df.drop_duplicates(subset=['ProfessorNom', 'AssignaturaNom'])
            
            counts = (
                unique_assignments
                .groupby('ProfessorNom')['AssignaturaProfessorPes']
                .sum()
                .reset_index()
            )
            
            counts.columns = ['ProfessorNom', combination_str]
            professor_degrees_df = (
                professor_degrees_df
                .merge(counts, on='ProfessorNom', how='left')
                .fillna(0)
            )
            
            professor_degrees_df[combination_str] = professor_degrees_df[combination_str].astype(int)

    # professor_degrees_df = (
    #     grau_assignatura_professor_df
    #     .groupby("ProfessorNom", as_index=False)[combinations_list]
    #     .sum()
    # )

    professor_merged_df = (
        professor_degree_count_df
        .merge(professor_subject_count_df)
        .merge(professor_subject_ponderation_df)
        .merge(professor_degrees_df)
    )

    professor_merged_df.to_csv(TEACHERS_PATH, index=False)
    grau_assignatura_professor_df.to_csv(TEST_PATH, index=False)