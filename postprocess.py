import csv
from collections import defaultdict
import pandas as pd
from typing import Iterable
from common import *
import matplotlib.pyplot as plt
from PIL import Image

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
    def __init__(
        self, 
        student_results_path: str | Path,
        teaching_guide_path: str | Path
    ):
        self.degree_df = (
            pd.read_excel(teaching_guide_path, "Grau")
            .set_index('GrauCodi')
        )
        teacher_df = pd.read_excel(teaching_guide_path, "Professor")
        self.student_df = self.get_student_df(student_results_path)
        self.teacher_df = self.get_teacher_df(self.student_df).merge(teacher_df, how='left')
        self.degrees = [TOTAL] + list(self.student_df[STUDENT_DEGREE].unique())
        self.degree_count = pd.DataFrame(self.student_df[STUDENT_DEGREE].value_counts()).reset_index()
        self.line_length = 10

    def get_top_teachers_per_degree(
            self, 
            degrees: Iterable[str] | str | None = None, 
            top: int = 16
        ) -> pd.DataFrame:
        if degrees is None:
            degrees = self.degrees
        if isinstance(degrees, str):
            degrees = [degrees]
        if not isinstance(degrees, Iterable):
            raise Exception("degrees is not iterable")
        if any(d not in self.degrees for d in degrees):
            return pd.DataFrame()
        return (
            self.teacher_df[[PROFESSOR_NAME] + degrees]
            .sort_values(by=degrees, ascending=False)
            .head(top)
            .reset_index(drop=True)
        )
    
    def render_students_results(self):
        print("\n--- Students list votes ---\n")
        teacher_columns = self.get_teacher_columns(self.student_df)
        for i, series in self.student_df.iterrows():
            student_name = series[STUDENT_NAME]
            student_degree = series[STUDENT_DEGREE]
            teachers = series[teacher_columns]
            print(f"{i}) [{student_degree}] {student_name}")
            print("-" * self.line_length)
            [print(t) for t in teachers[teachers > 0].index]
            print()
        
        print(f"Total students who voted: {len(self.student_df)}")
        for _, series in self.degree_count.iterrows():
            print(f"- Students from {series[STUDENT_DEGREE]}: {series["count"]}")

        student_name_counts = self.student_df[STUDENT_NAME].value_counts()
        non_unique_students = student_name_counts[student_name_counts > 1].index
        are_students_unique = len(non_unique_students) == 0

        print(f"\nAre students unique? {are_students_unique}")
        if not are_students_unique:
            print("Not unique students:")
            for student in non_unique_students:
                student_mask = self.student_df[STUDENT_NAME] == student
                professor_columns = self.get_teacher_columns(self.student_df)
                repeated_votes = self.student_df[student_mask].copy()
                teacher_counts = repeated_votes[professor_columns].sum()
                teacher_counts = teacher_counts[teacher_counts > 0]
                is_exactly_repeated = (teacher_counts == len(repeated_votes)).all()
                print(f"- Student: {student}. Is exactly repeated? {is_exactly_repeated}")
                # print(teacher_counts)

    def render_teachers_results(
        self, 
        sortby: Literal['count', 'valley', 'surname'],
        series: bool = False,
        images: bool = False,
        series_output: bool = False,
        top: int = 16
    ):
        print("\n--- Teacher vote counts ---\n")
        num_degrees = len(self.degrees)
        for idx, degree in enumerate(self.degrees):
            _top = top + 2 if degree == TOTAL else top
            results_df = (
                self.teacher_df[self.teacher_df[degree] > 0]
                .sort_values(by=degree, ascending=False)
                .head(_top)
            )
            if sortby == 'count':
                pass
            if sortby == 'valley':
                results_df.pipe(
                    func=self.do_valley_reorder, 
                    inplace=True
                )
            if sortby == 'surname':
                results_df.sort_values(
                    by='ProfessorCognom1', 
                    ascending=True, 
                    inplace=True
                )
            results_df = (
                results_df
                .reset_index(drop=True)
                [[PROFESSOR_NAME, degree]]
            )
            if series: 
                print(results_df)
                print() if idx < num_degrees - 1 else None
            output_path = (DATA_DIR / degree)
            if images:
                try:
                    degree_name = self.degree_df.loc[degree]['GrauNom']
                    title = f"Orla del {degree_name}"
                except KeyError:
                    title = "Orla Conjunta dels Graus en Enginyeries TIC"
                self.generate_image_plot(results_df, title, output_path.with_suffix('.png'), ncols=_top)
            if series_output:
                results_df.to_csv(output_path.with_suffix('.csv'), index=False)

    def render_student_suggestions(self):
        any_suggestion = (
            self.student_df[STUDENT_SUGGESTION]
            .apply(lambda s: len(s))
            .any()
        )
        if not any_suggestion:
            return
        print("\n--- Students suggestions ---")
        for i, series in self.student_df.iterrows():
            student_suggestion = series[STUDENT_SUGGESTION]
            if len(student_suggestion) == 0:
                continue
            student_name = series[STUDENT_NAME]
            student_degree = series[STUDENT_DEGREE]
            print(f"{i}) [{student_degree}] {student_name.rstrip(" ")}: {student_suggestion}")

    def render_complementary_degree(self):
        print("\n--- Complementary degree ---")
        print(
            self.student_df[
                (self.student_df[STUDENT_COMPLEMENTARY_DEGREE].str.len() > 0)
                & (self.student_df[STUDENT_COMPLEMENTARY_DEGREE] != self.student_df[STUDENT_DEGREE]) 
            ][[STUDENT_NAME, STUDENT_DEGREE, STUDENT_COMPLEMENTARY_DEGREE]])

    def render_results(self):
        print("\n------ Results Analysis ------")
        self.render_students_results()
        # self.render_teachers_results(mode='surname', images=True, top=16) # 
        self.render_teachers_results(sortby='count', series=True, series_output=True, top=len(self.teacher_df))
        # self.render_student_suggestions()
        self.render_complementary_degree()
        print()

    @staticmethod
    def generate_image_plot(
            df: pd.DataFrame, 
            title: str = "", 
            output_path: str | Path | None = None,
            nrows: int = 1,
            ncols: int = 16
        ):
        fig, axes = plt.subplots(nrows, ncols, figsize=(20, 3))
        if len(df) == 1:
            axes = [axes]
        for ax_idx, (df_idx, row) in enumerate(df.iterrows()):
            ax = axes[ax_idx]
            teacher_name = str(row[PROFESSOR_NAME])
            image_path = IMAGES_DIR / generate_image_name(teacher_name)
            if image_path.exists():
                image = Image.open(image_path)
                ax.imshow(image)
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Not found",
                    ha="center",
                    va="center",
                    color="red",
                    transform=ax.transAxes,
                )
            ax.set_xlabel('\n'.join(teacher_name.split(' ')), fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
        for j in range(len(df), 16):
            axes[j].axis("off")
        plt.suptitle(title, fontsize=18, y=0.8)
        plt.tight_layout(rect=[0, 0, 1, 1])
        if output_path is not None:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
        plt.show()

    @staticmethod
    def get_teacher_columns(student_df: pd.DataFrame) -> pd.Index:
        return student_df.select_dtypes(int).columns

    @staticmethod
    def do_valley_reorder(
        df: pd.DataFrame, 
        inplace: bool = False
    ) -> pd.DataFrame | None:
        n = len(df)
        start_index = (n - 1) if (n - 1) % 2 == 0 else (n - 2)
        even_indexs = list(range(start_index, -1, -2))
        odd_indexs = list(range(1, n, 2))
        order = even_indexs + odd_indexs
        if inplace:
            df.loc[:, :] = df.iloc[order].values
            df.index = df.index[order]
            return None
        else:
            return df.iloc[order]

    @staticmethod
    def get_teacher_df(students_df: pd.DataFrame) -> pd.DataFrame:
        degrees = students_df[STUDENT_DEGREE].unique()
        teachers = []
        for professor in AnalyzerDataFrame.get_teacher_columns(students_df):
            professor_dict = {}
            professor_dict[PROFESSOR_NAME] = professor
            professor_dict[TOTAL] = students_df[professor].sum().astype(int)
            for degree in degrees:
                filtered_results_df = students_df[students_df[STUDENT_DEGREE] == degree]
                filtered_comlementary_results_df = students_df[students_df[STUDENT_COMPLEMENTARY_DEGREE] == degree]
                professor_dict[degree] = filtered_results_df[professor].sum().astype(int)
                professor_dict[degree] += filtered_comlementary_results_df[professor].sum().astype(int) / 10
            teachers.append(professor_dict)
        teahcer_df = pd.DataFrame(teachers)
        teahcer_df[PROFESSOR_IMAGE] = (
            teahcer_df[PROFESSOR_NAME].apply(generate_image_name)
        )
        return teahcer_df

    @staticmethod
    def get_student_df(filepath: str | Path) -> pd.DataFrame: 
        df = (
            pd.read_csv(filepath)
            if str(filepath).endswith('csv')
            else pd.read_json(filepath)
        )
        return (
            df
            .fillna({c: "" if c in STUDENT_FIXED_KEYS else 0 for c in df.columns})
            .astype({c: str if c in STUDENT_FIXED_KEYS else int for c in df.columns})
        )

if __name__ == "__main__":
    AnalyzerDataFrame(RESULTS_PATH, DATABASE_PATH).render_results()