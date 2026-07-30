import os
import csv
import json
from common import *
import flask

INDEX_TEMPLATE = "index.html"
RETURN_TEMPLATE = "return.html"
DEFAULT_IMAGE = "default.jpg"
RETURN_MESSAGE = \
    "<h1>Gràcies per la teva votació!</h1>"\
    "<p>El teu vot s'ha registrat correctament.</p>"
BAD_RETURN = \
    "<h1>MODE variable not set: .json or .csv</h1>"\
    "<p>Contact with the programmer of this web: +34 605 17 19 65</p>"

app = flask.Flask(__name__)

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return value

def read_teachers(
    path: str = TEACHERS_PATH,
    key: str = PROFESSOR_NAME,
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
    return flask.render_template(
        template_name_or_list=INDEX_TEMPLATE, 
        professors=teachers, 
        keys=keys
    )

if MODE == ".json":
    @app.route('/votar', methods=['POST'])
    def vote() -> str:   
        votes = []
        if RESULTS_PATH.exists():
            with open(RESULTS_PATH, mode='r', encoding='utf-8') as f:
                try:
                    votes = json.load(f)
                except json.JSONDecodeError:
                    pass
        votes.append(dict(flask.request.form))
        with open(RESULTS_PATH, mode='w', encoding='utf-8') as f:
            json.dump(votes, f, ensure_ascii=False, indent=4)
        return flask.render_template('return.html')

elif MODE == ".csv":
    @app.route('/votar', methods=['POST'])
    def vote(
        teacher_key_name: str = PROFESSOR_NAME,
        student_key_name: str = STUDENT_NAME,
        student_key_degree: str = "EstudiantGrau",
        student_key_degree2: str = "EstudiantGrauComplementari",
        student_key_suggestions: str = "EstudiantSuggeriment"
    ) -> str:
        teachers = read_teachers()
        teacher_names = [p[teacher_key_name] for p in teachers]
        student_name = flask.request.form.get('nom_estudiant', '')
        student_degree = flask.request.form.get('grau', '')
        student_degree2 = flask.request.form.get('grau2', '')
        student_suggestions = flask.request.form\
            .get('suggeriments', '')\
            .replace('\n', ' ')
        
        votes = []

        for name in teacher_names:
            vote = flask.request.form.get(name, '0') 
            votes.append(vote)
        
        file_exists = os.path.isfile(RESULTS_PATH)
        with open(RESULTS_PATH, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                header = [
                    student_key_name, 
                    student_key_degree, 
                    student_key_degree2,
                    student_key_suggestions,
                ] + teacher_names
                writer.writerow(header)
            student_row = [
                student_name, 
                student_degree, 
                student_degree2, 
                student_suggestions
            ] + votes
            writer.writerow(student_row)
        
        return flask.render_template('return.html')

else:
    @app.route('/votar', methods=['POST'])
    def vote() -> str:
        return BAD_RETURN 

if __name__ == '__main__':
    app.run(debug=True)