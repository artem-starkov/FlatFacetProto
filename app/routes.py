from app import app
from flask import render_template, flash, send_from_directory, request
from app.utils import nn_utils
import os


@app.route("/")
def home():
    return render_template("index.html", title="Home page")


@app.route('/validate_g5', methods=['GET', 'POST'])
def validate_g5():
    if request.method == 'GET':
        return render_template('validate_g10.html', title='Валидация G5', g=5)
    else:
        case = int(request.form.get('case'))
        nn_type = int(request.form.get('model'))
        validation_data = nn_utils.validate(case, nn_type, 5)
        print(validation_data)
        return render_template('validate_g10.html', title='Валидация G5', g=5, info=validation_data)


@app.route('/validate_g10', methods=['GET', 'POST'])
def validate_g10():
    if request.method == 'GET':
        return render_template('validate_g10.html', title='Валидация G10', g=10)
    else:
        case = int(request.form.get('case'))
        nn_type = int(request.form.get('model'))
        validation_data = nn_utils.validate(case, nn_type, 10)
        print(validation_data)
        return render_template('validate_g10.html', title='Валидация G10', g=10, info=validation_data)


@app.route('/manual_input', methods=['GET', 'POST'])
def manual_input():
    if request.method == 'GET':
        return render_template('manual_input.html', title='Ручной ввод')
    else:
        if not request.form.get('fi_rad') and not request.form.get('fi'):
            flash('Угол не указан', 'fi')
            return render_template('manual_input.html', title='Ручной ввод')
        g = int(request.form.get('g'))
        nn_type = int(request.form.get('model'))
        left_from = int(request.form.get('left_from'))    # 8
        left_to = int(request.form.get('left_to'))        # 15
        right_from = int(request.form.get('right_from'))  # 23 59
        right_to = int(request.form.get('right_to'))      # 30 52
        r = float(request.form.get('r'))                  # 259.96702
        if 'fi_rad' in request.form:
            fi = float(request.form.get('fi_rad'))
        else:
            fi = float(request.form.get('fi'))
        validation_data = nn_utils.validate_on_manual_input(nn_type, left_from, left_to, right_from, right_to, r, fi, g)
        return render_template('manual_input.html', title='Пользовательский ввод', info=validation_data)


@app.route('/download_data')
def download_data():
    return send_from_directory(directory=os.path.join(app.root_path, 'static', 'reports'),
                               path='data.csv', as_attachment=True)
