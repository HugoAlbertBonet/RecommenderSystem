from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import pandas as pd
from recommenders.collaborative import compute_user_similarity
from recommenders.hybrid import hybrid_recommender
from recommenders.group import group_hybrid_recommender_with_aggregation
import dataloader
import random
from sklearn.metrics import mean_absolute_error

is_group = False

def update_data():
    (usuarios_historico, 
    items_names, preferencias, 
    padres, 
    items_clasificacion,
    datos_personales, 
    grupos_preferencias) = dataloader.load_data()

    # Crear la matriz usuario-ítem para el colaborativo
    user_item_matrix = usuarios_historico.pivot_table(index='id_user', columns='id_item', values='valoracion')
    all_items = items_names['id_item'].unique()
    user_item_matrix = user_item_matrix.reindex(columns=all_items)

    # Calcular la matriz de similitud entre usuarios
    sim_matrix = compute_user_similarity(user_item_matrix)
    global data_up_to_date
    data_up_to_date = True
    return (usuarios_historico,
            items_names, 
            preferencias, 
            padres, 
            items_clasificacion,
            datos_personales, 
            grupos_preferencias, 
            user_item_matrix, 
            all_items, 
            sim_matrix)

(usuarios_historico,
            items_names, 
            preferencias, 
            padres, 
            items_clasificacion,
            datos_personales, 
            grupos_preferencias, 
            user_item_matrix, 
            all_items, 
            sim_matrix) = update_data()


matriz_pref_raw = preferencias.pivot_table(
    index='id_user',
    columns='id_preferencia',
    values='score',
    fill_value=0
)

# 2) Asegurar columnas 1…115
columnas_deseadas = list(range(1, 116))
matriz_pref_raw = matriz_pref_raw.reindex(columns=columnas_deseadas, fill_value=0)

# 3) Transponer: filas=preferencias, columnas=usuarios
matriz_preferencias = matriz_pref_raw.T

# 4) Añadir la columna 'padre' (nombre de categoría)
padres_indexed = padres.set_index('id')['name']
matriz_preferencias['padre'] = matriz_preferencias.index.map(padres_indexed)

# 5) Función de filtrado top-20% por categoría
def filtrar_top_porcentaje(df, porcentaje=0.2):
    df_f = df.copy()
    usuarios = [c for c in df.columns if c != 'padre']
    for cat, grupo in df.groupby('padre'):
        for user in usuarios:
            cnt = (grupo[user] > 0).sum()
            top_n = max(1, int(cnt * porcentaje))
            tops   = grupo[user].nlargest(top_n).index
            no_tops = grupo.index.difference(tops)
            df_f.loc[no_tops, user] = 0
    return df_f

# 6) Calcular la matriz filtrada global
matriz_filtrada = filtrar_top_porcentaje(matriz_preferencias, porcentaje=0.2)
################################################################################

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/get_title")
def get_title():
    title = "My Valencia Travel Guide - From Backend!"
    return jsonify({"title": title})


##########################################
### REGISTRATION FORMS AND PREFERENCES ###
##########################################

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user_identifier = data.get("user_id")
    user_name = data.get("name")
    userAge = data.get("age")
    userGender = data.get("gender")
    userJob = data.get("job")
    userChildren = data.get("children")
    userChildrenOld = data.get("children_old")
    userChildrenYoung = data.get("children_young")
    #print(userAge)
    try: 
        userAge = int(userAge)
    except:
        return jsonify({"error": "Age must be a number"}), 400
    if userGender != "M" and userGender != "F":
        return jsonify({"error": "Gender must be M or F"}), 400
    try: 
        userJob = int(userJob)
    except:
        return jsonify({"error": "Job code must be a number"}), 400
    try: 
        userChildren = int(userChildren)
        if userChildren != 0 and userChildren != 1:
            return jsonify({"error": "Children must be 1 or 0"}), 400
    except:
        return jsonify({"error": "Children must be 1 or 0"}), 400
    if userChildren == 0:
        userChildrenOld = 0
        userChildrenYoung = 0
    try:
        userChildrenOld = int(userChildrenOld)
        userChildrenYoung = int(userChildrenYoung)
    except:
        return jsonify({"error": "Children ages must be numbers"}), 400

    answer = dataloader.check_exists(user_identifier)
    if answer == 0:
        return jsonify({"error": "User already exists"}), 400
    answer = dataloader.add_user_data(user_identifier, 
                                      user_name, 
                                      userAge, 
                                      userGender, 
                                      userJob, 
                                      userChildren, 
                                      userChildrenOld, 
                                      userChildrenYoung)
    if answer == 0:
        return jsonify({"error": "Error adding user data"}), 400
    
    global data_up_to_date
    data_up_to_date = False
    return jsonify({"message": "User registered successfully"})

@app.route("/preferences_to_rate", methods=["GET"])
def get_preferences_to_rate():
    try:
        # Assuming 'padres' DataFrame has columns 'id' and 'name' representing the preferences
        if 'id' not in padres.columns or 'name' not in padres.columns:
             return jsonify({"error": "Preferences data is missing 'id' or 'name' column"}), 500

        preferences_list = padres[['id', 'name']].to_dict('records')
        # Example format: [{"id": 1, "name": "Culture"}, {"id": 2, "name": "Gastronomy"}, ...]
        return jsonify({"preferences": preferences_list})
    except Exception as e:
        print(f"Error fetching preferences list: {e}")
        # Log the error properly in a real application
        return jsonify({"error": "Failed to retrieve preferences list"}), 500


@app.route("/submit_ratings", methods=["POST"])
def get_ratings():
    data = request.get_json()
    userId = data.get("userId")
    ratings = data.get("ratings")
    answer = dataloader.add_user_preferences(userId, ratings)
    if answer == 0:
        return jsonify({"error": "Error adding user preferences"}), 400
    global data_up_to_date
    data_up_to_date = False
    return jsonify({"message": "Ratings submitted successfully"})

@app.route("/get_individual_users", methods=["GET"])
def get_individual_users():
    try:
        users = dataloader.get_individual_users()
        if users is None:
            return jsonify({"error": "No users found"}), 404
        return jsonify({"users": users})
    except Exception as e:
        print(f"Error fetching individual users: {e}") 
        return jsonify({"error": "Failed to retrieve individual users"}), 500   
    
@app.route("/register_group", methods=["POST"])
def register_group():
    data = request.get_json()
    groupname = data.get("name")
    members = data.get("members")
    answer = dataloader.add_user_preferences(userId, ratings)
    if answer == 0:
        return jsonify({"error": "Error adding user preferences"}), 400
    global data_up_to_date
    data_up_to_date = False
    return jsonify({"message": "Ratings submitted successfully"})


##########################################
#######     RECOMMENDATIONS     ##########
##########################################

@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    global usuarios_historico
    global items_names
    global preferencias
    global padres
    global items_clasificacion
    global datos_personales
    global grupos_preferencias
    global user_item_matrix
    global all_items
    global sim_matrix
    global data_up_to_date

    # Actualizar datos si es necesario
    if not data_up_to_date:
        (
            usuarios_historico,
            items_names,
            preferencias,
            padres,
            items_clasificacion,
            datos_personales,
            grupos_preferencias,
            user_item_matrix,
            all_items,
            sim_matrix
        ) = update_data()

    try:
        data = request.get_json()
        user_id = int(data.get("userId"))
        num_recommendations = data.get("num_recommendations")
        selectedTypes = data.get("recommendation_types", [])

        print("Selected Types:", selectedTypes)

        if not isinstance(num_recommendations, int):
            num_recommendations = int(num_recommendations)

        # Construir pesos base según tipos seleccionados
        base_weights = {
            'collaborative': int("collaborative" in selectedTypes) / len(selectedTypes),
            'content':       int("content"       in selectedTypes) / len(selectedTypes),
            'demographic':   int("demographic"   in selectedTypes) / len(selectedTypes)
        }

        # Si solo hay un tipo, forzamos su peso
        set_weights = base_weights if len(selectedTypes) == 1 else None

        # Obtener recomendaciones híbridas
        raw_recommendations = hybrid_recommender(
            target_user      = user_id,
            user_item_matrix = user_item_matrix,
            sim_matrix       = sim_matrix,
            usuarios_historico = usuarios_historico,
            items_names        = items_names,
            preferencias       = preferencias,
            padres             = padres,
            items_clasificacion= items_clasificacion,
            datos_personales   = datos_personales,
            grupos_preferencias= grupos_preferencias,
            base_weights       = base_weights,
            top_n              = num_recommendations,
            set_weights        = set_weights
        )

        # Formatear salida
        recommendations = []
        for rec in raw_recommendations:
            item_id = rec['id_item']
            item_name = items_names.loc[
                items_names['id_item'] == item_id,
                'name_item'
            ].values[0]

            obj = {
    "id_item":      item_id,
    "name":         item_name,
    "hybrid_score": round(rec['hybrid_score'], 4)
            }

            # ── Content
            if 'sim_score' in rec:
                obj.update({
                    "sim_score":  round(rec['sim_score'],  4),
                    "hist_score": round(rec['hist_score'], 4),
                    "vis_score":  round(rec['vis_score'],  4)
                })

            # ── Collaborative
            if 'neighbor_count' in rec:
                obj.update({
                    "neighbor_count":       rec['neighbor_count'],
                    "neighbor_mean_rating": round(rec['neighbor_mean_rating'], 2)
                })

            # ── Demographic  ← NUEVO
            if 'group' in rec:          # también hay demo_score / explanation
                obj.update({
                    "demo_score": round(rec['demo_score'], 4),
                    "group":      rec['group'],
                    "explanation":rec['explanation']
                })


            recommendations.append(obj)

        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 400



##########################################
###### Evaluación usando mismas SR ######
##########################################


CORS(app)  # Esto SIEMPRE va después de definir app

@app.route("/evaluate", methods=["POST", "OPTIONS"])
@cross_origin()
def evaluate():
    if request.method == 'OPTIONS':
        return '', 200

    # ---------- cargar test set --------------------------------------------
    try:
        test_set = pd.read_csv(
            "data/puntuaciones_usuario_test.csv", sep=";", header=None,
            names=['id_user', 'id_item', 'valoracion']
        )
    except Exception:
        return jsonify({"error": "No se pudo cargar el test set."}), 500

    # ---------- refrescar datos si fuera necesario -------------------------
    global data_up_to_date, usuarios_historico, items_names, preferencias
    global padres, items_clasificacion, user_item_matrix, sim_matrix
    if not data_up_to_date:
        (usuarios_historico,  items_names,  preferencias, padres,
         items_clasificacion, user_item_matrix, all_items,
         sim_matrix) = update_data()

    # ---------- leer payload ------------------------------------------------
    try:
        d        = request.get_json()
        user_ids = [int(u) for u in d.get("userIds", [])]
        types    = d.get("recommendation_types", [])
        n        = int(d.get("num_recommendations", 10))
        thr_rec  = float(d.get("threshold_recommended", 4.0))
        thr_rel  = float(d.get("threshold_relevant",    4.0))
    except Exception:
        return jsonify({"error": "Payload inválido"}), 400

    results = {}
    types_to_eval = ['hybrid'] if len(types) > 1 else types

    # ---------- recorrer algoritmos ----------------------------------------
    for algo in types_to_eval:
        results[algo] = {}

        # pesos
        if algo == 'hybrid':
            set_w  = None
            weights = {k: (1 if k in types else 0)
                       for k in ['collaborative', 'content', 'demographic']}
        else:
            set_w  = {k: (1 if k == algo else 0)
                      for k in ['collaborative', 'content', 'demographic']}
            weights = set_w.copy()

        # normalizar pesos
        tot = sum(weights.values())
        weights = {k: (v/tot if tot else 1/3) for k, v in weights.items()}

        # ---------- cada usuario -------------------------------------------
        for uid in user_ids:

            raw = hybrid_recommender(
                uid,
                user_item_matrix,
                sim_matrix,
                usuarios_historico,
                items_names,
                preferencias,
                padres,
                items_clasificacion,
                datos_personales,
                grupos_preferencias,
                base_weights=weights,
                top_n=200,
                set_weights=set_w
            )
            #  raw  ➜  [{'id_item': .., 'hybrid_score': .., ...}, ...]

            # --- seleccionar recomendaciones relevantes según umbral --------
            rec_rel = { r['id_item'] for r in raw if r['hybrid_score'] >= thr_rec }

            # conjunto de ítems relevantes en test
            test_u   = test_set[test_set['id_user'] == uid]
            test_rel = set(test_u[test_u['valoracion'] >= thr_rel]['id_item'])

            # métricas clásicas
            tp     = len(rec_rel & test_rel)
            prec   = tp / len(rec_rel) if rec_rel else 0.0
            recall = tp / len(test_rel) if test_rel else 0.0
            f1     = (2*prec*recall)/(prec+recall) if (prec+recall)>0 else 0.0

            # MAE sobre predicciones escaladas (solo si ≥ thr_rec)
            y_true, y_pred = [], []
            for r in raw:
                if r['hybrid_score'] < thr_rec:
                    continue
                y_pred.append(1 + r['hybrid_score']*6)        # escala 1‑7
                fila = test_u[test_u['id_item'] == r['id_item']]
                y_true.append(float(fila['valoracion'].iloc[0]) if not fila.empty else 0.0)
            mae = mean_absolute_error(y_true, y_pred) if y_pred else None

            results[algo][uid] = {
                "precision": round(prec, 4),
                "recall":    round(recall, 4),
                "f1":        round(f1, 4),
                "mae": None if mae is None else round(mae, 4)
            }

    return jsonify({"metrics": results})

@app.route("/group_recommendations", methods=["POST"])
def get_group_recommendations():
    global usuarios_historico
    global items_names
    global preferencias
    global padres
    global items_clasificacion
    global datos_personales
    global grupos_preferencias
    global user_item_matrix
    global all_items
    global sim_matrix
    global data_up_to_date

    if not data_up_to_date:
        (usuarios_historico,
            items_names, 
            preferencias, 
            padres, 
            items_clasificacion, 
            datos_personales, 
            grupos_preferencias,
            user_item_matrix, 
            all_items, 
            sim_matrix) = update_data()
        
    try:
        data = request.get_json()
        users = data.get("users")
        print("Users:", users)
        user_ids = [int(uid) for uid in users]
        num_recommendations = data.get("num_recommendations")
        selectedTypes = data.get("recommendation_types")
        print("Selected Types:", selectedTypes)
        if not isinstance(num_recommendations, int):
            num_recommendations = int(num_recommendations)
        base_weights = {'collaborative': int("collaborative" in selectedTypes)/len(selectedTypes),
                        'content': int("content" in selectedTypes)/len(selectedTypes),
                        'demographic': int("demographic" in selectedTypes)/len(selectedTypes)}
        raw_recommendations = group_hybrid_recommender_with_aggregation(user_ids,
                                                           user_item_matrix, sim_matrix,
                                                           usuarios_historico, items_names,
                                                           preferencias, padres, items_clasificacion,
                                                           datos_personales, grupos_preferencias,
                                                           base_weights=base_weights,
                                                           bonus_factor=0.1,
                                                           top_n=10)
        recommendations = []
        for item, score in raw_recommendations:
            # Se obtiene el nombre del ítem a partir de su id
            item_name = items_names.loc[items_names['id_item'] == item, 'name_item'].values[0]
            recommendations.append({"name": item_name, "similarity": round(score, 4)})
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error getting recommendations"}), 500
@app.route("/user_preferences/<int:user_id>", methods=["GET"])
def user_preferences(user_id):
    global matriz_filtrada, padres

    # 1) Verifica si el usuario está en la matriz filtrada
    if user_id in matriz_filtrada.columns:
        # 2) Extrae la serie de scores y elimina la fila 'padre'
        prefs_series = (
            matriz_filtrada[user_id]
            .drop(labels='padre', errors='ignore')
        )
        # 3) Filtra solo los valores positivos
        prefs_series = prefs_series[prefs_series > 0]

        # 4) Construye un DataFrame con id_preferencia y score
        df = (
            prefs_series
            .to_frame(name='score')
            .reset_index()
            .rename(columns={'index': 'id_preferencia'})
        )

        # 5) Une con los nombres de preferencia
        padres_clean = padres.rename(
            columns={padres.columns[0]: 'id', padres.columns[1]: 'name'}
        )[['id', 'name']]
        df = (
            df
            .merge(padres_clean, left_on='id_preferencia', right_on='id', how='left')
            .drop(columns=['id'])
        )
    else:
        # Usuario no existe o no tiene puntuaciones positivas
        df = pd.DataFrame(columns=['id_preferencia', 'name', 'score'])

    # 6) Prepara el payload JSON
    preferences = [
        {
            "id_preferencia": int(row.id_preferencia),
            "name":           row.name or "",
            "score":          float(row.score)
        }
        for row in df.itertuples()
    ]

    # 7) Devuelve siempre 200 con la lista (vacía si no hay nada)
    return jsonify({"preferences": preferences})

@app.route("/user_visits/<int:user_id>", methods=["GET"])
def user_visits(user_id):
    # Historial de visitas
    user_hist = usuarios_historico[usuarios_historico['id_user']==user_id]
    if user_hist.empty:
        return jsonify({"error":"User not found"}), 404

    visitas = []
    for row in user_hist.itertuples():
        item_id = row.id_item
        name    = items_names.loc[
                     items_names['id_item']==item_id,'name_item'
                  ].iat[0]
        valor   = float(row.valoracion)
        count   = int(items_names.loc[
                     items_names['id_item']==item_id,'visitas'
                  ].iat[0])
        visitas.append({
            "id_item":item_id,
            "name_item":name,
            "valoracion":valor,
            "visitas":count
        })
    return jsonify({"visits":visitas})


@app.route("/visits_to_rate", methods=["GET"])
def visits_to_rate():
    """
    Devuelve una muestra aleatoria de 20 ítems para que el usuario
    indique si los ha visitado y con qué puntuación.
    Parámetro en query string: userId (int)
    """
    try:
        user_id = int(request.args.get("userId"))
    except (TypeError, ValueError):
        return jsonify({"error": "userId debe ser numérico"}), 400

    # Aquí usamos la lista global all_items y items_names
    sample = random.sample(all_items.tolist(), 20)
    items = [
        {"id_item": itm,
         "name": items_names.loc[items_names['id_item']==itm, 'name_item'].iloc[0]}
        for itm in sample
    ]
    return jsonify({"items": items})


@app.route("/submit_visits", methods=["POST"])
def submit_visits():
    """
    Recibe JSON:
      { userId: int, visits: [{id_item: int, valoracion: int}, …] }
    1) Añade a usuarios_historico (DataFrame en memoria).
    2) Persiste en disco con dataloader.add_user_visits.
    3) Marca data_up_to_date=False para recálculo.
    """
    data = request.get_json()
    try:
        user_id = int(data["userId"])
        visits  = data.get("visits", [])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Payload inválido"}), 400

    # -- 1) Actualizar DataFrame en memoria --
    nuevos = pd.DataFrame([
        {"id_user": user_id, "id_item": v["id_item"], "valoracion": v["valoracion"]}
        for v in visits
    ])
    global usuarios_historico
    usuarios_historico = pd.concat([usuarios_historico, nuevos], ignore_index=True)

    # -- 2) Persistir en disco para que load_data() lo recargue --
    dataloader.add_user_visits(user_id, visits)

    # -- 3) Forzar recálculo de la matriz colaborativa --
    global data_up_to_date
    data_up_to_date = False

    return jsonify({"message": "Visitas registradas correctamente"})
    
if __name__ == "__main__":
    app.run(debug=True)
