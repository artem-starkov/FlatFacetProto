from app import app, db
from app.enums import NNType, PredictionType, DataSource
from app.utils.nn_utils import get_model
from app.utils.prototype_data_receiver import PrototypeFileReceiver, PrototypeDeviceReceiver
from app.utils.prototype_exceptions import *
from app.models import Run
import math


def get_receiver(run_id):
    if app.config['DATA_SOURCE'] == DataSource.File:
        return PrototypeFileReceiver(run_id)
    else:
        return PrototypeDeviceReceiver(run_id)


def stream_validate(coord_case, angle_case, g, run_id):
    nn_type = NNType.NN1
    dist_model = get_model(nn_type, PredictionType.Distance, g=g)
    angle_model = get_model(nn_type, PredictionType.Azimuth, g=g)
    receiver = get_receiver(run_id)
    receiver.initialize()
    data = receiver.get_data()
    zero_flag = False
    while Run.is_active(run_id):
        try:
            frame = next(data)
            if sum(frame) <= 2:
                app.logger.info('Zeros')
                if zero_flag:
                    continue
                flag = False
                if Run.is_active(run_id):
                    flag = True
                if coord_case == 1:
                    yield {'R': '0.00000', 'φ': '0.00000', 'flag': flag}
                else:
                    yield {'X': '0.00000', 'Y': '0.00000', 'flag': flag}
            else:
                zero_flag = True
                r_pred = round(dist_model.predict([frame])[0][0], 5)
                fi_pred = round(angle_model.predict([frame])[0][0], 5)
                app.logger.info(f'r: {r_pred} | fi: {fi_pred}')
                flag = False
                if Run.is_active(run_id):
                    Run.update(run_id, r_pred, fi_pred)
                    flag = True
                if coord_case == 1:
                    if angle_case == 1:
                        yield {'R': r_pred, 'φ': fi_pred, 'flag': flag}
                    else:
                        yield {'R': r_pred, 'φ': f'{round(fi_pred * 57.3, 5)}°', 'flag': flag}
                else:
                    if fi_pred < math.pi:
                        r_pred *= -1
                    else:
                        fi_pred = math.pi - fi_pred
                    yield {'X': round(r_pred * math.cos(fi_pred), 5), 'Y': round(abs(r_pred) * math.sin(fi_pred), 5), 'flag': flag}
        except StopIteration:
            Run.finish(run_id)
            break
        except InputException as e:
            print('Something went wrong with bytes_ check:', e.bytes_)
        except BrightsException as e:
            print('Something went wrong with brights, look: ', e.omm_num, e.brights)
        except Exception as e:
            print('Unknown exception: ', str(e))



""" 
    left_from=318, left_to=400, right_from=338, right_to=420
    318 82 338 338 82 318 original
    1476 / 2 = 738
    309 100 329 329 100 309 addiction ver.1
    318 left[9:-9] 338 338 right[9:-9] 318 addiction ver.2 
"""
