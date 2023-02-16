from app import app, db
from flask import render_template, request, Response, stream_with_context, redirect
from app.utils import prototype
from app.models import Run
from app.utils.nn_utils import validate_real_and_predicted


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv


@app.route('/stream_prediction', methods=['GET', 'POST'])
def stream_prediction():
    if request.method == 'GET':
        return render_template('prototype/stream_validate.html', title='Симуляция горизонтального движения',
                               coord_case=1, angle_case=1)
    else:
        coord_case = int(request.form.get('coord_case'))
        angle_case = int(request.form.get('angle_case'))
        run = Run(status=1, r=0, fi=0, angle_case=angle_case, coord_case=coord_case)
        db.session.add(run)
        db.session.commit()
        return Response(stream_with_context(stream_template('prototype/stream_validate.html',
                                                            show_results=True, coord_case=coord_case,
                                                            angle_case=angle_case, run_id=run.id,
                                                            rows=prototype.stream_validate(coord_case, angle_case, g=10,
                                                                                           run_id=run.id))))


@app.route('/stop_run/<run_id>')
def stop_run(run_id):
    run = Run.query.get(run_id)
    run.stop()
    return redirect(f'/measurements/{run_id}')


@app.route('/measurements/<run_id>', methods=['GET', 'POST'])
def measurements(run_id):
    run = Run.query.get(run_id)
    if request.method == 'GET':
        return render_template('prototype/measurements.html', r_pred=round(run.r, 5), fi_pred=round(run.fi * 57.3, 5))
    else:
        fi_true = float(request.form.get('fi'))
        r_true = float(request.form.get('r'))
        info = validate_real_and_predicted(r_true, fi_true, run.r, run.fi)
        return render_template('prototype/measurements.html', r_pred=round(run.r, 5), fi_pred=round(run.fi * 57.3, 5),
                               info=info, r_true=r_true, fi_true=fi_true)
# /css nn_utils prototype prototype_data_receiver enums prot+routes config