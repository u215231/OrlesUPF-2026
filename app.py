from flask import Flask, render_template, request
import csv
import os

TEACHERS_FILE = 'professors.csv'
TEMPLATE_FILE = 'index.html'
RESULTS_FILE = 'resultats.csv'
RETURN_MESSAGE = \
    "<h1>Gràcies per la teva votació!</h1>"\
    "<p>El teu vot s'ha registrat correctament.</p>"

IMAGES_DIR = 'static/imatges'
DEFAULT_IMAGE = 'default.jpg'

app = Flask(__name__)

def read_teachers():
    teachers = []
    with open(TEACHERS_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['NomCognoms']
            if not name:
                row['Imatge'] = DEFAULT_IMAGE
            else:
                file_name = name.lower().replace(' ', '_') + '.jpg'
                file_path = os.path.join(IMAGES_DIR, file_name)
                if os.path.exists(file_path):
                    row['Imatge'] = file_name
                else:
                    row['Imatge'] = DEFAULT_IMAGE
            teachers.append(row)
    return teachers

@app.route('/')
def index():
    professors = read_teachers()
    return render_template(TEMPLATE_FILE, professors=professors)

@app.route('/votar', methods=['POST'])
def vote():
    teachers = read_teachers()
    teacher_names = [p['NomCognoms'] for p in teachers]
    
    votes = []
    for name in teacher_names:
        vote = request.form.get(name, '0') 
        votes.append(vote)
        
    results_file = RESULTS_FILE
    file_exists = os.path.isfile(results_file)
    
    with open(results_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(teacher_names)
        writer.writerow(votes)
        
    return RETURN_MESSAGE

if __name__ == '__main__':
    app.run(debug=True)