import os
import joblib


def guardar(modelo, encoder, models_dir):
    """
    serializa el modelo y el encoder en la carpeta indicada.
    crea la carpeta si todavía no existe.
    """

    # exist_ok=True no lanza error si la carpeta ya estaba creada
    os.makedirs(models_dir, exist_ok=True)

    model_path   = os.path.join(models_dir, 'catboost_regressor.joblib')
    encoder_path = os.path.join(models_dir, 'onehot_encoder.joblib')

    # joblib es más rápido que pickle para objetos que tienen arrays numpy grandes,
    # que es exactamente el caso de cualquier modelo de sklearn o catboost
    joblib.dump(modelo,  model_path)
    joblib.dump(encoder, encoder_path)

    print(f'  modelo guardado en  : {model_path}')
    print(f'  encoder guardado en : {encoder_path}')

    return model_path, encoder_path
