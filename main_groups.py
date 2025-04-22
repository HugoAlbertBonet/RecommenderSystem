from recommenders.collaborative import compute_user_similarity
from recommenders.group import group_hybrid_recommender_with_aggregation
from dataloader import load_data


def main():
    usuarios_historico, items_names, preferencias, padres, items_clasificacion = load_data()

    user_item_matrix = usuarios_historico.pivot_table(index='id_user', columns='id_item', values='valoracion')
    all_items = items_names['id_item'].unique()
    user_item_matrix = user_item_matrix.reindex(columns=all_items)

    sim_matrix = compute_user_similarity(user_item_matrix)

    try:
        ids = input("Ingrese los IDs de usuario separados por coma: ").strip()
        user_ids = [int(uid.strip()) for uid in ids.split(',') if uid.strip().isdigit()]
    except Exception as e:
        print("Error con los IDs:", e)
        return

    if not user_ids:
        print("No se ingresaron IDs válidos.")
        return

    
     
    final_recs = group_hybrid_recommender_with_aggregation(user_ids,
                                                           user_item_matrix, sim_matrix,
                                                           usuarios_historico, items_names,
                                                           preferencias, padres, items_clasificacion,
                                                           base_weights={'collaborative': 0.33,
                                                                         'content': 0.33,
                                                                         'demographic': 0.34},
                                                           bonus_factor=0.1,
                                                           top_n=10)

    print(f"\n🎯 Recomendaciones GRUPALES para usuarios {user_ids}:")
    for item, score in final_recs:
        item_name = items_names.loc[items_names['id_item'] == item, 'name_item'].values[0]
        print(f"✅ {item_name} (Score: {score:.4f})")



if __name__ == "__main__":
    main()