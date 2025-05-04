from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from recommenders.collaborative import compute_user_similarity
from recommenders.hybrid import hybrid_recommender
from recommenders.group import group_hybrid_recommender_with_aggregation
import dataloader

is_group = False

def update_data():
    (usuarios_historico, 
    items_names, preferencias, 
    padres, 
    items_clasificacion,
    datos_personales, 
    grupos_preferencias,) = dataloader.load_data()

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
    print(userAge)
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
                                         datos_personales, grupos_preferencias,
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
                                                           datos_personales, grupos_preferencias
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

if __name__ == "__main__":
    app.run(debug=True)
