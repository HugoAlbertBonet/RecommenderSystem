from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from recommenders.collaborative import compute_user_similarity
from recommenders.hybrid import hybrid_recommender
from recommenders.group import group_hybrid_recommender_with_aggregation
import dataloader

(usuarios_historico, 
 items_names, preferencias, 
 padres, 
 items_clasificacion) = dataloader.load_data()

# Crear la matriz usuario-ítem para el colaborativo
user_item_matrix = usuarios_historico.pivot_table(index='id_user', columns='id_item', values='valoracion')
all_items = items_names['id_item'].unique()
user_item_matrix = user_item_matrix.reindex(columns=all_items)

# Calcular la matriz de similitud entre usuarios
sim_matrix = compute_user_similarity(user_item_matrix)

################################################################################

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/get_title")
def get_title():
    title = "My Valencia Travel Guide - From Backend!"
    return jsonify({"title": title})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("userId")
    password = data.get("password")
    user_name = data.get("user_name")
    userAge = data.get("userAge")
    userGender = data.get("userGender")
    userJob = data.get("userJob")
    userChildren = data.get("userChildren")
    userChildrenOld = data.get("userChildrenOld")
    userChildrenYoung = data.get("userChildrenYoung")
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

    answer = dataloader.add_user_password(username, password)
    if answer == 0:
        return jsonify({"error": "User already exists"}), 400
    answer = dataloader.add_user_data(username, 
                                      user_name, 
                                      userAge, 
                                      userGender, 
                                      userJob, 
                                      userChildren, 
                                      userChildrenOld, 
                                      userChildrenYoung)
    if answer == 0:
        return jsonify({"error": "Error adding user data"}), 400
    
    return jsonify({"message": "User registered successfully"})


@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    try:
        data = request.get_json()
        user_id = int(data.get("userId"))
        num_recommendations = data.get("num_recommendations")
        selectedTypes = data.get("recommendation_types")
        print("Selected Types:", selectedTypes)
        if not isinstance(num_recommendations, int):
            num_recommendations = int(num_recommendations)
        base_weights = {'collaborative': int("collaborative" in selectedTypes)/len(selectedTypes),
                        'content': int("content" in selectedTypes)/len(selectedTypes),
                        'demographic': int("demographic" in selectedTypes)/len(selectedTypes)}
        if len(selectedTypes) == 1:
            set_weights = base_weights
        else:
            set_weights = None
        raw_recommendations = hybrid_recommender(user_id, user_item_matrix, sim_matrix,
                                         usuarios_historico, items_names,
                                         preferencias, padres, items_clasificacion,
                                         base_weights=base_weights,
                                         bonus_factor=0.1,
                                         top_n=num_recommendations,
                                         set_weights=set_weights)
        recommendations = []
        for item, score in raw_recommendations:
            # Se obtiene el nombre del ítem a partir de su id
            item_name = items_names.loc[items_names['id_item'] == item, 'name_item'].values[0]
            recommendations.append({"name": item_name, "similarity": round(score, 4)})
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error getting recommendations"}), 500



@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)
