import csv
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(__file__)
RESULTS_PATH = os.path.join(BASE_DIR, "data/resultats.csv")

class Analyzer:
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

if __name__ == "__main__":
    Analyzer().analyze(RESULTS_PATH)