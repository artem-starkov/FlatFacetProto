from app import app

if __name__ == '__main__':
    app.run(debug=True)
# import wandb
#
#
# def get_model(run, models_info, index):
#     model_artifact = run.use_artifact(f"{models_info[index]['wandb_rep']}:{models_info[index]['version']}")
#     model_dir = model_artifact.download()
#     # model_path = os.path.join(model_dir, models_info[index]['wandb_rep'])
#     # model = keras.models.load_model(model_dir)
#     # return model
#     return 0
#
# models_info2 = [{'title': 'bumbling-sweep-3', 'wandb_rep': 'model-bumbling-sweep-3', 'version': 'v19', 'pred_type': 'Distance'},
#                {'title': 'solar-sweep-11', 'wandb_rep': 'model-solar-sweep-11', 'version': 'v46', 'pred_type': 'Angle'},
#                {'title': 'glorious-sweep-7', 'wandb_rep': 'Proto_distance_trained_models', 'version': 'v50', 'pred_type': 'Distance'},
#                {'title': 'volcanic-sweep-1', 'wandb_rep': 'Proto_angle_trained_models', 'version': 'v60', 'pred_type': 'Angle'},
#                {'title': 'fallen-sweep-14', 'wandb_rep': 'Proto_distance_trained_models', 'version': 'v43', 'pred_type': 'Distance'},
#                {'title': 'hopeful-sweep-1', 'wandb_rep': 'Proto_angle_trained_models', 'version': 'v33', 'pred_type': 'Angle'}]
#
#
# models_info = [{'wandb_rep': 'Proto_distance_trained_models', 'version': 'v103', 'pred_type': 'Distance'},
#                {'wandb_rep': 'Proto_angle_trained_models', 'version': 'v100', 'pred_type': 'Angle'},
#                {'wandb_rep': 'Proto_distance_trained_models', 'version': 'v115', 'pred_type': 'Distance'},
#                {'wandb_rep': 'Proto_angle_trained_models', 'version': 'v105', 'pred_type': 'Angle'},
#                {'wandb_rep': 'Proto_distance_trained_models', 'version': 'v113', 'pred_type': 'Distance'},
#                {'wandb_rep': 'Proto_angle_trained_models', 'version': 'v113', 'pred_type': 'Angle'}]
#
# with wandb.init(project="PhysProto", job_type="experiments") as run:
#   #dist_model1 = get_model(run, models_info, 0)
#   dist_model2 = get_model(run, models_info, 2)
#   dist_model3 = get_model(run, models_info, 4)
#   #dist_model4 = get_model(run, models_info, 6)
#
#   #angle_model1 = get_model(run, models_info, 1)
#   angle_model2 = get_model(run, models_info, 3)
#   angle_model3 = get_model(run, models_info, 5)
# import wandb
# #wandb.login(key='677c0813a6a0dba6f2349a8b015e27298e30cbab')
# run = wandb.init()
# artifact = run.use_artifact('cim/PhysProto/Proto_angle_trained_models:v100', type='model')
# artifact_dir = artifact.download()
# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# from tensorflow import keras
# model = keras.models.load_model('artifacts/NN1-dist-g10')
# print(type(model))