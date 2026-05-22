import pandas as pd
from itertools import combinations
from common import *

if __name__ == "__main__":
    # degree_df = pd.read_excel(DATABASE_PATH, "Grau")
    degree_subject_df = pd.read_excel(DATABASE_PATH, "GrauAssignatura")
    # subject_df = pd.read_excel(DATABASE_PATH, "Assignatura")
    subject_teacher_df = pd.read_excel(DATABASE_PATH, "AssignaturaProfessor")
    teacher_df = pd.read_excel(DATABASE_PATH, "Professor")

    degree_subject_teacher_df = pd.merge(
        degree_subject_df,
        subject_teacher_df,
        how='right'
    )

    subject_teacher_count_df = (
        subject_teacher_df
        .groupby(PROFESSOR_NAME, as_index=False)
        .size()
        .rename(columns={"size": "ProfessorQuantitatAssignatures"})
    )

    subject_teacher_df["Coordinador"] = subject_teacher_df["AssignaturaNom"].str.startswith("Coordinador")
    subject_teacher_df["Tutor"] = subject_teacher_df["AssignaturaNom"].str.startswith("Tutor")

    subject_teacher_coordinator_df = (
        subject_teacher_df
        .groupby(PROFESSOR_NAME, as_index=False)["Coordinador"]
        .any()
        .astype({"Coordinador": int})
    )
    
    subject_teacher_tutor_df = (
        subject_teacher_df
        .groupby(PROFESSOR_NAME, as_index=False)["Tutor"]
        .any()
        .astype({"Tutor": int})
    )

    subject_teacher_ponderation_df = (
        subject_teacher_df
        .groupby(PROFESSOR_NAME, as_index=False)["AssignaturaProfessorPes"]
        .sum()
    )

    degree_teacher_count_df = (
        degree_subject_teacher_df[["GrauCodi", PROFESSOR_NAME]]
        .drop_duplicates()
        .groupby(PROFESSOR_NAME, as_index=False)
        .size()
        .rename(columns={"size": "ProfessorQuantitatGraus"})
    )

    degrees = list(degree_subject_teacher_df["GrauCodi"].unique())
    for degree in degrees:
        degree_subject_teacher_df[degree] = (
            degree_subject_teacher_df["GrauCodi"] == degree
        ).astype(int)

    professor_degrees_df = pd.DataFrame(teacher_df[[PROFESSOR_NAME, "Dona"]])

    degrees_not_na = [d for d in degrees if isinstance(d, str)]
    num_degress_not_na = len(degrees_not_na)

    for i in range(1, num_degress_not_na + 1):
        for degree_combination_tuple in combinations(degrees_not_na, i):
            degree_combination_list = sorted(degree_combination_tuple)
            degree_combination_str = "_".join(degree_combination_list).lower()
            
            isin_degree_combination = (
                degree_subject_teacher_df['GrauCodi']
                .isin(degree_combination_list)
            )

            counts = (
                degree_subject_teacher_df[isin_degree_combination]
                .drop_duplicates(subset=[PROFESSOR_NAME, 'AssignaturaNom'])
                .groupby('ProfessorNom')['AssignaturaProfessorPes']
                .sum()
                .reset_index()
            )
            
            counts.columns = [PROFESSOR_NAME, degree_combination_str]
            professor_degrees_df = (
                professor_degrees_df
                .merge(counts, on=PROFESSOR_NAME, how='left')
                .fillna(0)
            )
            
            professor_degrees_df[degree_combination_str] = (
                professor_degrees_df[degree_combination_str].astype(int)
            )

    professor_merged_df = (
        degree_teacher_count_df
        .merge(subject_teacher_count_df)
        .merge(subject_teacher_ponderation_df)
        .merge(professor_degrees_df)
        .merge(subject_teacher_coordinator_df)
        .merge(subject_teacher_tutor_df)
    )

    professor_merged_df.to_csv(TEACHERS_PATH, index=False)