import numpy as np 
from recommenders.collaborative import get_collaborative_recommendations
from recommenders.content_dynamic import get_content_recommendations
from recommenders.demographic import get_demographic_recommendations


def aggregate_recommendations_by_type(user_recs_dict, group_seen_items, top_n=10):
    combined = {'collaborative': {}, 'content': {}, 'demographic': {}}
    user_ids = list(user_recs_dict.keys())

    for rec_type in combined.keys():
        all_scores = {}

        # Recolectar scores por ítem
        for uid in user_ids:
            recs = user_recs_dict[uid].get(rec_type, [])
            recommended_items = dict(recs)

            for item in recommended_items:
                if item in group_seen_items:
                    continue
                if item not in all_scores:
                    all_scores[item] = {}
                all_scores[item][uid] = recommended_items[item]

        # Calcular media (llenando ceros donde falte)
        scores_combined = {}
        #print(all_scores)
        for item, user_scores in all_scores.items():
            full_scores = [user_scores.get(uid, 0.0) for uid in user_ids]
            scores_combined[item] = np.mean(full_scores)
        top_items = sorted(scores_combined.items(), key=lambda x: x[1], reverse=True)[:top_n]
        combined[rec_type] = dict(top_items)
        #print(combined)
    return combined



def aggregate_recommendations_by_type(user_recs_dict, group_seen_items, top_n=10):
    combined = {'collaborative': {}, 'content': {}, 'demographic': {}}
    user_ids = list(user_recs_dict.keys())

    for rec_type in combined.keys():
        all_scores = {}

        # Recolectar scores por ítem
        for uid in user_ids:
            recs = user_recs_dict[uid].get(rec_type, [])
            recommended_items = dict(recs)

            for item in recommended_items:
                if item in group_seen_items:
                    continue
                if item not in all_scores:
                    all_scores[item] = {}
                all_scores[item][uid] = recommended_items[item]

        # Calcular media (llenando ceros donde falte)
        scores_combined = {}
        #print(all_scores)
        for item, user_scores in all_scores.items():
            full_scores = [user_scores.get(uid, 0.0) for uid in user_ids]
            scores_combined[item] = np.mean(full_scores)
        top_items = sorted(scores_combined.items(), key=lambda x: x[1], reverse=True)[:top_n]
        combined[rec_type] = dict(top_items)
        #print(combined)
    return combined

def group_hybrid_recommender_with_aggregation(user_ids,
                                              user_item_matrix, sim_matrix,
                                              usuarios_historico, items_names,
                                              preferencias, padres, items_clasificacion,
                                              datos_personales, grupos_preferencias,
                                              base_weights={'collaborative': 0.33, 'content': 0.33, 'demographic': 0.34},
                                              bonus_factor=0.1,
                                              top_n=50):
    """
    Recomendación grupal avanzada con agregación por tipo y fusión híbrida.
    """
    user_recs_by_type = {}

    for uid in user_ids:
        # Individual recommendations
        if base_weights["collaborative"] > 0: rec_collab, _, _ = get_collaborative_recommendations(user_item_matrix, sim_matrix, uid)
        else: rec_collab = {}
        if base_weights["content"] > 0:
            rec_content, _, _ = get_content_recommendations(usuarios_historico, items_names,
                                                     preferencias, padres, items_clasificacion,
                                                     uid, N=top_n * 2)
        else: rec_content = {}
        if base_weights["demographic"] > 0:
            demo_list = get_demographic_recommendations(uid, datos_personales, grupos_preferencias,
            items_clasificacion, items_names, top_n=top_n * 2)
            rec_demo    = {d['id_item']: d['demo_score'] for d in demo_list}
        else: rec_demo = {}

        # Convert to list of tuples and truncate
        user_recs_by_type[uid] = {
            'collaborative': sorted(rec_collab.items(), key=lambda x: x[1], reverse=True)[:top_n * 2],
            'content': sorted(rec_content.items(), key=lambda x: x[1], reverse=True)[:top_n * 2],
            'demographic': sorted(rec_demo.items(), key=lambda x: x[1], reverse=True)[:top_n * 2]
        }

        
        
    # Combinar cada tipo de recomendador
    group_seen_items = get_group_seen_items(usuarios_historico, user_ids)

    aggregated_by_type = aggregate_recommendations_by_type(user_recs_by_type,
                                                           group_seen_items,
                                                           top_n=top_n)

    # Fusión híbrida final
    hybrid_scores = {}
    for rec_type, item_scores in aggregated_by_type.items():
        weight = base_weights.get(rec_type, 0.33)
        for item, score in item_scores.items():
            hybrid_scores[item] = hybrid_scores.get(item, 0) + weight * score

    # Top-N híbrido
    hybrid_top = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    return hybrid_top


def get_group_seen_items(usuarios_historico, user_ids):
    """
    Retorna el conjunto de ítems ya vistos por cualquier usuario del grupo.
    """
    vistos = usuarios_historico[usuarios_historico['id_user'].isin(user_ids)]
    return set(vistos['id_item'].unique())