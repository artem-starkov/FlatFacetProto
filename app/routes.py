from app import app
from flask import render_template, redirect, flash, jsonify, send_from_directory, request
from app.utils import nn_utils


@app.route("/")
def home():
    return render_template("index.html", title="Home page")


@app.route('/validate_g5', methods=['GET', 'POST'])
def validate_g5():
    if request.method == 'GET':
        return render_template('validate_g10.html', title='Валидация g5', g=5)
    else:
        case = int(request.form.get('case'))
        nn_type = int(request.form.get('model'))
        validation_data = nn_utils.validate(case, nn_type, 5)
        print(validation_data)
        return render_template('validate_g10.html', title='Валидация g5', g=5, info=validation_data)


@app.route('/manual_input', methods=['GET', 'POST'])
def manual_input():
    if request.method == 'GET':
        return render_template('manual_input.html', title='Ручной ввод')
    else:
        nn_type = int(request.form.get('model'))
        left_from = int(request.form.get('left_from'))    # 1
        left_to = int(request.form.get('left_to'))        # 4
        right_from = int(request.form.get('right_from'))  # 9 65
        right_to = int(request.form.get('right_to'))      # 18 74
        r = float(request.form.get('r'))                  # 259.96702
        fi = float(request.form.get('fi'))                # 1.539734
        validation_data = nn_utils.validate_on_manual_input(nn_type, left_from, left_to, right_from, right_to, r, fi, 5)
        return render_template('manual_input.html', title='Пользовательский ввод', info=validation_data)
