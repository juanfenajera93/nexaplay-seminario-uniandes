import os
import pandas as pd
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

from scripts.model_preprocessing import preprocesar
from scripts.model_training      import entrenar
from scripts.model_saving        import guardar

# rutas absolutas relativas a este archivo,
# sin importar desde qué carpeta se ejecute el script
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, 'data',   'games_clean.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')


def main():

    # ── carga ──────────────────────────────────────────────────────────────────
    print('cargando datos...')
    df = pd.read_csv(DATA_PATH)
    print(f'  {df.shape[0]:,} filas x {df.shape[1]} columnas')

    # ── preprocesamiento ───────────────────────────────────────────────────────
    print('\npreprocesando...')
    X_train, X_test, y_train, y_test, encoder = preprocesar(df)
    print(f'  train: {X_train.shape[0]:,} filas  |  test: {X_test.shape[0]:,} filas')

    # ── entrenamiento ──────────────────────────────────────────────────────────
    print('\nentrenando modelo...')
    modelo = entrenar(X_train, y_train)
    print('  listo')

    # ── evaluación ────────────────────────────────────────────────────────────
    # métricas sobre test, no sobre train:
    # si se evaluara en train, cualquier modelo parecería perfecto
    pred = modelo.predict(X_test)

    rmse = root_mean_squared_error(y_test, pred)
    mae  = mean_absolute_error(y_test,     pred)
    r2   = r2_score(y_test,                pred)

    print('\nresultados en test:')
    print(f'  rmse : {rmse:.4f}  (error promedio en millones de unidades)')
    print(f'  mae  : {mae:.4f}')
    print(f'  r2   : {r2:.4f}  (varianza explicada por el modelo)')

    # ── guardar ────────────────────────────────────────────────────────────────
    print('\nguardando archivos...')
    guardar(modelo, encoder, MODELS_DIR)

    print('\nlisto. los .joblib están en models/')


# __name__ == '__main__' hace que main() solo corra cuando se ejecuta
# este archivo directamente; no corre si otro archivo lo importa
if __name__ == '__main__':
    main()
