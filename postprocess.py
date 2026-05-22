import csv
from collections import defaultdict
import pandas as pd
from typing import Iterable
from common import *

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
            print(f" - Students from {degree}: {count}")
            
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

class AnalyzerDataFrame:
    def __init__(self, filepath: str | Path):
        self.students_df = self.get_students(filepath)
        self.professor_df = self.get_professors(self.students_df)
        self.degrees = [TOTAL] + list(self.students_df[STUDENT_DEGREE].unique())
        self.degree_count = pd.DataFrame(self.students_df[STUDENT_DEGREE].value_counts()).reset_index()
        self.line_length = 10

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
    
    def render_students_results(self):
        students_df = self.students_df

        print("\n--- Students list votes ---\n")
        for i, series in students_df.iterrows():
            student_name = series[STUDENT_NAME]
            student_degree = series[STUDENT_DEGREE]
            professors = series[series.apply(lambda x: isinstance(x, bool))]
            print(f"{i}) [{student_degree}] {student_name}")
            print("-" * self.line_length)
            [print(t) for t in professors[professors > 0].index]
            
            print()
        
        print(f"Total students who voted: {len(students_df)}")
        for _, series in self.degree_count.iterrows():
            print(f"- Students from {series[STUDENT_DEGREE]}: {series["count"]}")

    def render_teachers_results(self):
        print("\n--- Teacher vote counts ---\n")
        for i, degree in enumerate(self.degrees):
            print(self.top_results(degrees=degree))
            print() if i < len(self.degrees) - 1 else None

    def render_student_suggestions(self):
        if not self.students_df[STUDENT_SUGGESTION].apply(lambda s: len(s)).any():
            return
        print("\n--- Students suggestions ---")
        for i, series in self.students_df.iterrows():
            student_suggestion = series[STUDENT_SUGGESTION]
            if len(student_suggestion) == 0:
                continue
            student_name = series[STUDENT_NAME]
            student_degree = series[STUDENT_DEGREE]
            print(f"{i}) [{student_degree}] {student_name.rstrip(" ")}: {student_suggestion}")

    def render_results(self):
        print("\n------ Results Analysis ------")
        self.render_students_results()
        self.render_teachers_results()
        self.render_student_suggestions()
        print()

    @staticmethod
    def get_professors(students_df: pd.DataFrame) -> pd.DataFrame:
        degrees = students_df[STUDENT_DEGREE].unique()
        professors = []
        for professor in students_df.select_dtypes(bool):
            professor_dict = {}
            professor_dict[PROFESSOR_NAME] = professor
            professor_dict[TOTAL] = students_df[professor].sum().astype(int)
            for degree in degrees:
                filtered_results_df = students_df[students_df[STUDENT_DEGREE] == degree]
                professor_dict[degree] = filtered_results_df[professor].sum().astype(int)
            professors.append(professor_dict)
        return pd.DataFrame(professors)

    @staticmethod
    def get_students(filepath: str | Path) -> pd.DataFrame: 
        df = (
            pd.read_csv(filepath)
            if str(filepath).endswith('csv')
            else pd.read_json(filepath)
        )
        return (
            df
            .fillna({c: 0 for c in df.columns if c not in STUDENT_FIXED_KEYS})
            .astype({c: str if c in STUDENT_FIXED_KEYS else bool for c in df.columns})
        )

if __name__ == "__main__":
    AnalyzerDataFrame(RESULTS_PATH).render_results()