from tensorflow import keras
from app import app
from app.utils.dataset_generator import Generator
from app.enums import NNType, PredictionType
import os
import math
import numpy as np
#from sklearn.metrics import r2_score, mean_squared_error
#from sklearn.utils.validation import check_consistent_length, check_array
import time
import csv


def get_model(model_type, prediction_type, g):
    if model_type == NNType.NN1:
        if prediction_type == PredictionType.Distance:
            model_path = os.path.join(app.root_path, 'artifacts', f'NN1-dist-g{g}')
        else:
            model_path = os.path.join(app.root_path, 'artifacts', f'NN1-angle-g{g}')
    elif model_type == NNType.NN2:
        if prediction_type == PredictionType.Distance:
            model_path = os.path.join(app.root_path, 'artifacts', f'NN2-dist-g{g}')
        else:
            model_path = os.path.join(app.root_path, 'artifacts', f'NN2-angle-g{g}')
    else:
        if prediction_type == PredictionType.Distance:
            model_path = os.path.join(app.root_path, 'artifacts', f'NN3-dist-g{g}')
        else:
            model_path = os.path.join(app.root_path, 'artifacts', f'NN3-angle-g{g}')
    model = keras.models.load_model(model_path)
    return model


def validate_real_and_predicted(r_true, fi_true, r_pred, fi_pred):
    if fi_true > 4:
        fi_true /= 57.3
    return {
        'Distance': {'1-MAPE': 100 - abs((r_true - r_pred)/r_true) * 100, 'RMSE': abs(r_pred - r_true)},
        'Angle': {'1-MAPE': 100 - abs((fi_true - fi_pred)/fi_true) * 100, 'RMSE': abs(fi_pred - fi_true)}}


def validate(test_case, nn_type, g):
    m = 1476
    t = time.time()
    generator = Generator(g=g)
    dataset = generator.get_dataset_for_validating(m=m, test_case=test_case)
    if nn_type != NNType.NN1:
        dataset = Generator.get_blue_zone_dataset(dataset, m)
    if nn_type == NNType.NN3:
        dataset = Generator.transform_to_small_dataset(dataset, m)
        m = 164
    x, y_r, y_fi = [], [], []
    for precedent in dataset:
        x.append(precedent[:m])
        y_r.append(precedent[m])
        y_fi.append(precedent[m + 1])
    gen_time = time.time() - t
    t = time.time()
    dist_model = get_model(nn_type, PredictionType.Distance, g=g)
    dist_time = time.time() - t
    t = time.time()
    angle_model = get_model(nn_type, PredictionType.Azimuth, g=g)
    angle_time = time.time() - t
    t = time.time()
    y_r_pred = dist_model.predict(x)
    dist_pred_time = time.time() - t
    t = time.time()
    y_fi_pred = angle_model.predict(x)
    counter = 0
    for i in range(len(y_fi)):
        if abs(y_fi[i] - y_fi_pred[i]) < math.asin(g / y_r[i]):
            counter += 1
    angle_pred_time = time.time() - t
    save_to_file(y_r, y_r_pred, y_fi, y_fi_pred, g)
    return {
        'Distance': {'R2': r2_score(y_r, y_r_pred), '1-MAPE': (1 - mean_absolute_percentage_error(y_r, y_r_pred)) * 100,
                     'RMSE': mean_squared_error(y_r, y_r_pred, squared=False)},
        'Angle': {'R2': r2_score(y_fi, y_fi_pred),
                  '1-MAPE': (1 - mean_absolute_percentage_error(y_fi, y_fi_pred)) * 100,
                  'RMSE': mean_squared_error(y_fi, y_fi_pred, squared=False), 'Hit rate': counter / len(y_fi)},
        'angle_pred_time': angle_pred_time, 'angle_time': angle_time, 'dist_time': dist_time, 'gen_time': gen_time,
        'dist_pred_time': dist_pred_time}


def validate_on_manual_input(nn_type, left_from, left_to, right_from, right_to, r_true, fi_true, g):
    if fi_true > 4:
        fi_true /= 57.3
    m = 164
    precedent = [0] * m
    for i in range(left_from - 1, left_to):
        precedent[i] = 1
    for i in range(int(m / 2) + right_from - 1, int(m / 2) + right_to):
        precedent[i] = 1
    if nn_type != NNType.NN3:
        precedent = [0] * 318 + precedent[:82] + [0] * 338 + [0] * 338 + precedent[82:] + [0] * 318
    print(len(precedent))
    t = time.time()
    dist_model = get_model(nn_type, PredictionType.Distance, g=g)
    dist_time1 = time.time() - t
    t = time.time()
    angle_model = get_model(nn_type, PredictionType.Azimuth, g=g)
    angle_time1 = time.time() - t
    t = time.time()
    r_pred = dist_model.predict([precedent])
    dist_time2 = time.time() - t
    t = time.time()
    fi_pred = angle_model.predict([precedent])
    angle_time2 = time.time() - t
    return {
        'Distance': {'R2': r2_score([r_true], r_pred), '1-MAPE': (1 - mean_absolute_percentage_error([r_true], r_pred)) * 100,
                     'RMSE': mean_squared_error([r_true], r_pred, squared=False), 'Value': r_pred},
        'Angle': {'R2': r2_score([fi_true], fi_pred),
                  '1-MAPE': (1 - mean_absolute_percentage_error([fi_true], fi_pred)) * 100,
                  'RMSE': mean_squared_error([fi_true], fi_pred, squared=False), 'Value': fi_pred},
        'dist_time': dist_time1, 'angle_time': angle_time1, 'dist_pred_time': dist_time2, 'angle_pred_time': angle_time2}


def mean_absolute_percentage_error(y_true, y_pred, sample_weight=None, multioutput='uniform_average'):
    y_type, y_true, y_pred, multioutput = check_reg_targets(
        y_true, y_pred, multioutput)
    check_consistent_length(y_true, y_pred, sample_weight)
    epsilon = np.finfo(np.float64).eps
    mape = np.abs(y_pred - y_true) / np.maximum(np.abs(y_true), epsilon)
    output_errors = np.average(mape,
                               weights=sample_weight, axis=0)
    if isinstance(multioutput, str):
        if multioutput == 'raw_values':
            return output_errors
        elif multioutput == 'uniform_average':
            # pass None as weights to np.average: uniform mean
            multioutput = None
    return np.average(output_errors, weights=multioutput)


def check_reg_targets(y_true, y_pred, multioutput, dtype="numeric"):
    check_consistent_length(y_true, y_pred)
    y_true = check_array(y_true, ensure_2d=False, dtype=dtype)
    y_pred = check_array(y_pred, ensure_2d=False, dtype=dtype)

    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))

    if y_pred.ndim == 1:
        y_pred = y_pred.reshape((-1, 1))

    if y_true.shape[1] != y_pred.shape[1]:
        raise ValueError("y_true and y_pred have different number of output "
                         "({0}!={1})".format(y_true.shape[1], y_pred.shape[1]))

    n_outputs = y_true.shape[1]
    allowed_multioutput_str = ('raw_values', 'uniform_average',
                               'variance_weighted')
    if isinstance(multioutput, str):
        if multioutput not in allowed_multioutput_str:
            raise ValueError("Allowed 'multioutput' string values are {}. "
                             "You provided multioutput={!r}".format(
                allowed_multioutput_str,
                multioutput))
    elif multioutput is not None:
        multioutput = check_array(multioutput, ensure_2d=False)
        if n_outputs == 1:
            raise ValueError("Custom weights are useful only in "
                             "multi-output cases.")
        elif n_outputs != len(multioutput):
            raise ValueError(("There must be equally many custom weights "
                              "(%d) as outputs (%d).") %
                             (len(multioutput), n_outputs))
    y_type = 'continuous' if n_outputs == 1 else 'continuous-multioutput'

    return y_type, y_true, y_pred, multioutput


def save_to_file(r_true, r_pred, fi_true, fi_pred, g):
    filename = os.path.join(app.root_path, 'static', 'reports', 'data.csv')
    with open(filename, 'w', newline='') as output:
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['R true', 'R pred', 'Fi true', 'Fi pred', 'Hit'])
        for i in range(len(fi_true)):
            hit = 1 if abs(fi_true[i] - fi_pred[i]) < math.asin(g / r_true[i]) else 0
            writer.writerow([r_true[i], r_pred[i][0], fi_true[i], fi_pred[i][0], hit])
