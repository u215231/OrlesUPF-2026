from typing import Literal
from pathlib import Path
import unicodedata

MODE: Literal[".json", ".csv"] = ".json"

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "professors.xlsx"
TEACHERS_PATH = DATABASE_PATH.with_suffix(".csv")
TEST_PATH = DATA_DIR / "test_.csv"
RESULTS_PATH = (DATA_DIR / "resultats").with_suffix(MODE)

STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR =  STATIC_DIR / "images"

PROFESSOR_NAME = "ProfessorNom"
PROFESSOR_IMAGE = "ImageName"

STUDENT_NAME = "EstudiantNom"
STUDENT_SUGGESTION = "EstudiantSuggeriment"
STUDENT_DEGREE = "EstudiantGrau"
STUDENT_COMPLEMENTARY_DEGREE = "EstudiantGrauComplementari"
STUDENT_FIXED_KEYS = [
    STUDENT_NAME, 
    STUDENT_SUGGESTION, 
    STUDENT_DEGREE,
    STUDENT_COMPLEMENTARY_DEGREE
]
TOTAL = "TOTAL"

def generate_image_name(name: str) -> str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('utf-8')
    name = name.lower().replace(' ', '_').replace('\'', '_') + '.jpg'    
    return name