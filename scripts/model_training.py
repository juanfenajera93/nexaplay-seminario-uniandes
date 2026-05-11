from catboost import CatBoostRegressor

# mismo random_state que en el notebook para que los resultados sean reproducibles
RANDOM_STATE = 50


def entrenar(X_train, y_train):
    """
    entrena catboost con los hiperparámetros por defecto del notebook.
    devuelve el modelo listo para predecir o guardar.
    """

    # los defaults de catboost ya funcionan bien para este dataset;
    # el tuning de hiperparámetros es un paso siguiente que aquí no aplica
    # verbose=0 silencia los logs de iteración que aparecen durante el fit
    modelo = CatBoostRegressor(
        random_state=RANDOM_STATE,
        verbose=0
    )

    modelo.fit(X_train, y_train)

    return modelo
