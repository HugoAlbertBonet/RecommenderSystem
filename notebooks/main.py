from recommenders.collaborative import compute_user_similarity
from recommenders.hybrid import hybrid_recommender
from dataloader import load_data


def main():
    # Cargar todos los datos
    usuarios_historico, items_names, preferencias, padres, items_clasificacion = load_data()
    
    # Crear la matriz usuario-ítem para el colaborativo
    user_item_matrix = usuarios_historico.pivot_table(index='id_user', columns='id_item', values='valoracion')
    all_items = items_names['id_item'].unique()
    user_item_matrix = user_item_matrix.reindex(columns=all_items)
    
    # Calcular la matriz de similitud entre usuarios
    sim_matrix = compute_user_similarity(user_item_matrix)
    
    try:
        target_user = int(input("Ingrese su ID de usuario: ").strip())
    except Exception as e:
        print("ID inválido:", e)
        return
    
    # Ejecutar el recomendador híbrido
    recommendations = hybrid_recommender(target_user, user_item_matrix, sim_matrix,
                                         usuarios_historico, items_names,
                                         preferencias, padres, items_clasificacion,
                                         base_weights={'collaborative': 0.33,
                                                       'content': 0.33,
                                                       'demographic': 0.33},
                                         bonus_factor=0.1,
                                         top_n=10)
    
    print(f"\nRecomendaciones híbridas para el usuario {target_user}:")
    for item, score in recommendations:
        # Se obtiene el nombre del ítem a partir de su id
        item_name = items_names.loc[items_names['id_item'] == item, 'name_item'].values[0]
        print(f"{item_name} (Score: {score:.4f})")


if __name__ == "__main__":
    main()