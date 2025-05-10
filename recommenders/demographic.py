import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_demographic_recommendations(target_user,
                                    datos_personales,
                                    grupos_preferencias,
                                    items_clasificacion,
                                    items_names,
                                    top_n=10):
    """
    Genera recomendaciones basadas en características demográficas del usuario.
    Devuelve una lista de dicts con:
      - id_item
      - name_item
      - demo_score       (similitud demográfica)
      - group            (nombre de grupo demográfico)
      - explanation      (texto explicativo)
    """
    # 1) Prepara matriz ítem×preferencia
    items_group = (
        items_clasificacion
        .groupby(['id_item','id_preferencia'], as_index=False)
        .mean()
    )
    matriz_items = items_group.pivot(
        index='id_item', columns='id_preferencia', values='score'
    )
    columnas_deseadas = list(range(1, 116))
    matriz_items = (
        matriz_items
        .reindex(columns=columnas_deseadas, fill_value=0)
        .fillna(0)
    )

    # 2) Asigna usuario a grupo y extrae vector de preferencias del grupo
    def asignar_vector_y_grupo(uid):
        user_row = datos_personales[datos_personales['id']==uid]
        if user_row.empty:
            return None, None
        u = user_row.iloc[0]
        edad, hijos, genero = u['age'], u['children'], u['gender']
        # reglas
        if edad <= 25 and hijos == 0:
            grp = "Menores de 25 sin hijos"
        elif edad >= 60:
            grp = "Jubilados (>60)"
        elif edad <= 40 and hijos == 1:
            grp = "menores de 40 con hijos"
        elif 25 <= edad <= 40 and hijos == 0:
            grp = "25/40 sin hijos"
        elif 40 <= edad <= 60 and genero == 'F':
            grp = "mujeres entre 40 y 60"
        elif 40 <= edad <= 60 and genero == 'M':
            grp = "hombres entre 40 y 60"
        else:
            return None, None
        # extrae vector del grupo
        if grp not in grupos_preferencias.columns:
            return None, None
        vec = grupos_preferencias.T.loc[grp].values
        print(grupos_preferencias.columns)
        return vec, grp

    vector, group = asignar_vector_y_grupo(target_user)
    print(group, vector)
    if vector is None:
        return []  # no asignado a ningún grupo

    # 3) Calcula similitud coseno ítems vs. vector del grupo
    sims = cosine_similarity(
        matriz_items.values,
        vector.reshape(1, -1)
    ).flatten()
    scores = pd.Series(sims, index=matriz_items.index)

    # 4) Selecciona top_n
    top = scores.nlargest(top_n)

    # 5) Construye lista de recomendaciones con detalles
    recs = []
    for item_id, score in top.items():
        name = items_names.loc[
            items_names['id_item']==item_id, 'name_item'
        ].iat[0]
        recs.append({
            "id_item":    int(item_id),
            "name_item":  name,
            "demo_score": float(round(score, 4)),
            "group":      group,
            "explanation": (
                f"Usuario asignado al grupo “{group}”. "
                f"El índice demográfico de este ítem es {round(score, 4)}."
            )
        })

    return recs
