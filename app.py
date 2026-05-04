from flask import Flask, render_template, request
import csv
import os
import unicodedata

BASE_DIR = os.path.dirname(__file__)

TEACHERS_PATH = os.path.join(BASE_DIR, "professors.csv")
RESULTS_PATH = os.path.join(BASE_DIR, "resultats.csv")
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
    name = name.lower().replace(' ', '_') + '.jpg'    
    return name

def read_teachers(path: str = TEACHERS_PATH) -> list[dict]:
    teachers = []
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['NomCognoms']
            row['Imatge'] = generate_image_name(name)\
                if name\
                else DEFAULT_IMAGE 
            teachers.append(row)
        teachers = sorted(teachers, key=lambda t: t["NomCognoms"])
        for teacher in teachers:
            image_name = teacher['Imatge']
            image_path = os.path.join(IMAGES_DIR, image_name)
            if not os.path.exists(image_path):
                teacher["Imatge"] = DEFAULT_IMAGE
    return teachers

@app.route('/')
def index():
    teachers = read_teachers()
    return render_template(TEMPLATE_NAME, professors=teachers)

@app.route('/votar', methods=['POST'])
def vote():
    teachers = read_teachers()
    teacher_names = [p['NomCognoms'] for p in teachers]
    student_name = request.form.get('nom_estudiant', '')
    student_degree = request.form.get('grau', '')
    votes = []
    for name in teacher_names:
        vote = request.form.get(name, '0') 
        votes.append(vote)
    results_file = RESULTS_PATH
    file_exists = os.path.isfile(results_file)
    with open(results_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            header = ['Nom Estudiant', 'Grau'] + teacher_names
            writer.writerow(header)
        student_row = [student_name, student_degree] + votes
        writer.writerow(student_row)
    return RETURN_MESSAGE

if __name__ == '__main__':
    app.run(debug=True)