from flask import Flask, render_template, request
import csv
import os
import unicodedata

BASE_DIR = os.path.dirname(__file__)

TEACHERS_PATH = os.path.join(BASE_DIR, "data/professors.csv")
RESULTS_PATH = os.path.join(BASE_DIR, "data/resultats.csv")
IMAGES_DIR =  os.path.join(BASE_DIR, "static/imatges")
TEMPLATE_NAME = "index.html"
DEFAULT_IMAGE = "default.jpg"
RETURN_MESSAGE = \
    "<h1>Gràcies per la teva votació!</h1>"\
    "<p>El teu vot s'ha registrat correctament.</p>"

app = Flask(__name__)

def generate_image_name(name: str) -> str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore').decode('utf-8')
    name = name.lower().replace(' ', '_').replace('\'', '_') + '.jpg'    
    return name

def read_teachers(
    path: str = TEACHERS_PATH,
    key: str = "ProfessorNom",
    image: str = "Imatge"
) -> list[dict]:
    teachers = []
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row[key]
            row[image] = generate_image_name(name)\
                if name\
                else DEFAULT_IMAGE 
            teachers.append(row)
        teachers = sorted(teachers, key=lambda t: t[key])
        for teacher in teachers:
            image_name = teacher[image]
            image_path = os.path.join(IMAGES_DIR, image_name)
            if not os.path.exists(image_path):
                teacher[image] = DEFAULT_IMAGE
    return teachers

@app.route('/')
def index():
    teachers = read_teachers()
    keys = list(teachers[0].keys())
    return render_template(TEMPLATE_NAME, professors=teachers, keys=keys)

@app.route('/votar', methods=['POST'])
def vote(
    teacher_key_name: str = "ProfessorNom",
    student_key_name: str = "EstudiantNom",
    student_key_degree: str = "EstudiantGrau",
    student_key_degree2: str = "EstudiantGrauComplementari",
    student_key_suggestions: str = "EstudiantSuggeriment"
) -> str:
    teachers = read_teachers()
    teacher_names = [p[teacher_key_name] for p in teachers]
    student_name = request.form.get('nom_estudiant', '')
    student_degree = request.form.get('grau', '')
    student_degree2 = request.form.get('grau2', '')
    student_suggestions = request.form.get('suggeriments', '').replace('\n', ' ')

    votes = []
    for name in teacher_names:
        vote = request.form.get(name, '0') 
        votes.append(vote)
    
    file_exists = os.path.isfile(RESULTS_PATH)
    with open(RESULTS_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            header = [
                student_key_name, 
                student_key_degree, 
                student_key_degree2,
                student_key_suggestions,
            ] + teacher_names
            writer.writerow(header)
        student_row = [student_name, student_degree, student_degree2, student_suggestions] + votes
        writer.writerow(student_row)
    
    return RETURN_MESSAGE

if __name__ == '__main__':
    app.run(debug=True)