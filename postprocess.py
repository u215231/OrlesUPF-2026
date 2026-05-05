import csv
import os
from collections import defaultdict
import pandas as pd
from typing import Iterable

BASE_DIR = os.path.dirname(__file__)
RESULTS_PATH = os.path.join(BASE_DIR, "data/resultats.csv")

class AnalyzerDict:
    def analyze_results(self, filepath: str):
        self.total_students = 0
        self.degree_counts = defaultdict(int)
        self.professors_votes = defaultdict(lambda: defaultdict(int))
        
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                headers = next(reader)
            except StopIteration:
                return
            professors_list = headers[2:]
            for row in reader:
                if not row:
                    continue
                self.total_students += 1
                degree = row[1]
                self.degree_counts[degree] += 1
                for index, professor in enumerate(professors_list):
                    vote_index = index + 2
                    if vote_index < len(row) and row[vote_index] == '1':
                        self.professors_votes[professor]['Total'] += 1
                        self.professors_votes[professor][degree] += 1

    def render_results(self, top=16):
        sorted_professors = sorted(
            self.professors_votes.items(), 
            key=lambda item: item[1]['Total'], 
            reverse=True
        )
        
        top_professors = sorted_professors[:top]

        print("=" * 70)
        print("VOTING SUMMARY")
        print("=" * 70)
        print(f"Total students who voted: {self.total_students}")
        
        for degree, count in self.degree_counts.items():
            print(f"Students from {degree}: {count}")
            
        print("\n" + "=" * 70)
        print("TOP 16 PROFESSORS")
        print("=" * 70)
        
        header_row = \
            f"{'Professor Name':<30} | {'Total':<5} | {'GEI':<4} | {'GESA':<4} | {'GEMCD':<5} | {'GEXT':<4}"
        print(header_row)
        print("-" * 70)

        for professor, votes in top_professors:
            prof_name = (professor[:27] + '...') if len(professor) > 30 else professor
            total = votes.get('Total', 0)
            gei = votes.get('GEI', 0)
            gesa = votes.get('GESA', 0)
            gemcd = votes.get('GEMCD', 0)
            gext = votes.get('GEXT', 0)
            
            row_str = f"{prof_name:<30} | {total:<5} | {gei:<4} | {gesa:<4} | {gemcd:<5} | {gext:<4}"
            print(row_str)

    def analyze(self, path: str, top=16):
        self.analyze_results(path)
        self.render_results(top)

PROFESSOR_COLUMN = 4
PROFESSOR_NAME = "ProfessorNom"
STUDENT_NAME = "EstudiantNom"
SUGGESTION = "EstudiantSuggeriment"
DEGREE_KEY = "EstudiantGrau"
TOTAL = "Total"

class AnalyzerDataFrame:
    def __init__(self, filepath: str):
        students_df = pd.read_csv(filepath).fillna(0)
        degrees = students_df[DEGREE_KEY].unique()
        professors = []
        professors_list = students_df.columns[PROFESSOR_COLUMN:]
        for professor in professors_list:
            professor_dict = {}
            professor_dict[PROFESSOR_NAME] = professor
            professor_dict[TOTAL] = students_df[professor].sum().astype(int)
            for degree in degrees:
                filtered_results_df = students_df[students_df[DEGREE_KEY] == degree]
                professor_dict[degree] = filtered_results_df[professor].sum().astype(int)
            professors.append(professor_dict)
        self.students_df = students_df
        self.professor_df = pd.DataFrame(professors)
        self.degrees = [TOTAL] + list(degrees)
        degree_count = self.students_df[DEGREE_KEY].value_counts()
        self.degree_count = pd.DataFrame(degree_count).reset_index()

    def top_results(self, degrees: list[str] = None, top: int = 16) -> pd.DataFrame:
        if degrees is None:
            degrees = self.degrees
        if isinstance(degrees, str):
            degrees = [degrees]
        if not isinstance(degrees, Iterable):
            raise Exception("degrees is not iterable")
        professor_df = self.professor_df
        if any(d not in self.degrees for d in degrees):
            return pd.DataFrame()
        professor_df = professor_df.sort_values(degrees, ascending=False)
        professor_df = professor_df[[PROFESSOR_NAME] + degrees]
        professor_df = professor_df.head(top)
        professor_df = professor_df.reset_index(drop=True)
        return professor_df
    
    def render_teachers_results(self):
        print("Teacher vote counts:")
        for degree in self.degrees:
            print(analyzer.top_results(degrees=degree))
            print()
    
    def render_students_results(self):
        students_df = self.students_df

        print("Students list votes:")
        for i, (_, row) in enumerate(students_df.iterrows()):
            student_name = row[STUDENT_NAME]
            student_degree = row[DEGREE_KEY]
            professors = row[PROFESSOR_COLUMN:]
            print(f"{i}) [{student_degree}] {student_name}")
            print("-"*10)
            [print(t) for t in professors[professors > 0].index]
            print()
        
        print(f"Total students who voted: {len(students_df)}")
        for _, row in self.degree_count.iterrows():
            print(f"Students from {row[DEGREE_KEY]}: {row["count"]}")
        print()


    def render_student_suggestions(self):
        print("Students suggestions:")
        students_df = self.students_df
        for i, (_, row) in enumerate(students_df.iterrows()):
            student_name = row[STUDENT_NAME]
            student_degree = row[DEGREE_KEY]
            student_suggestion = row[SUGGESTION]
            print(f"{i}) [{student_degree}] {student_name.rstrip(" ")}: {student_suggestion}")

if __name__ == "__main__":
    analyzer = AnalyzerDataFrame(RESULTS_PATH)
    analyzer.render_students_results()
    analyzer.render_teachers_results()
    analyzer.render_student_suggestions()