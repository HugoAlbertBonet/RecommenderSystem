from recommenders.collaborative import get_collaborative_recommendations
from recommenders.content_dynamic import get_content_recommendations
from recommenders.demographic import get_demographic_recommendations

# =============================================================================
# CÁLCULO DE PESOS DINÁMICOS
# =============================================================================
def compute_dynamic_weights(collab_neighbors, content_count, demo_count, base_weights):
    """
    Ajusta los pesos base según la disponibilidad de información.
    Si el usuario tiene pocos vecinos similares, se reduce el peso colaborativo,
    y se compensan con los otros sistemas.
    """
    expected_neighbors = collab_neighbors+content_count
    factor_collab = min(1, collab_neighbors / expected_neighbors) if expected_neighbors > 0 else 1
    
    expected_content = collab_neighbors+content_count
    factor_content = min(1, content_count / expected_content) if expected_content > 0 else 1
    
    expected_demo = 5  # Umbral esperado para el demográfico
    factor_demo = min(1, demo_count / expected_demo) if expected_demo > 0 else 1
    
    dynamic_weights = {
        'collaborative': base_weights.get('collaborative', 0) * factor_collab,
        'content': base_weights.get('content', 0) * factor_content,
        'demographic': base_weights.get('demographic', 0) * factor_demo
    }
    total = sum(dynamic_weights.values())
    if total > 0:
        for key in dynamic_weights:
            dynamic_weights[key] /= total
    else:
        dynamic_weights = {key: 1/3 for key in ['collaborative', 'content', 'demographic']}
    return dynamic_weights

# =============================================================================
# FUNCIÓN HÍBRIDA PARA COMBINAR RECOMENDACIONES
# =============================================================================
def hybrid_recommender(target_user, 
                       user_item_matrix, sim_matrix, 
                       usuarios_historico, items_names, 
                       preferencias, padres, items_clasificacion,
                       base_weights={'collaborative': 0.33, 'content': 0.33, 'demographic': 0.34},
                       bonus_factor=0.1,
                       top_n=10,
                       set_weights = None):
    """
    Combina de forma híbrida (y de manera dinámica) múltiples sistemas recomendadores:
      - Colaborativo
      - Basado en contenido
      - Demográfico (stub)
    
    Se ajustan los pesos dinámicamente según la información disponible
    (por ejemplo, si el usuario tiene pocos vecinos similares, se le da menos peso al colaborativo).
    
    Retorna una lista de tuplas (id_item, score_híbrido) ordenadas de mayor a menor.
    """
    # Obtener recomendaciones de cada sistema
    if (set_weights is not None and 
        set_weights["collaborative"] == 0) or base_weights["collaborative"] == 0:
        rec_collab, collab_count = {}, 0
    else:
        rec_collab, collab_count = get_collaborative_recommendations(user_item_matrix, sim_matrix, target_user)
    
    if (set_weights is not None and 
        set_weights["content"] == 0) or base_weights["content"] == 0:
        rec_content, content_count = {}, 0
    else:
        rec_content, content_count = get_content_recommendations(usuarios_historico, items_names,
                                                             preferencias, padres, items_clasificacion,
                                                             target_user, N=top_n)

    if (set_weights is not None and 
        set_weights["demographic"] == 0) or base_weights["demographic"] == 0:
        rec_demo, demo_count = {}, 0
    else:
        rec_demo, demo_count = get_demographic_recommendations(target_user, N=top_n)
    # Calcular pesos dinámicos
    if set_weights is not None:
        dynamic_w = set_weights
    else:
        dynamic_w = compute_dynamic_weights(collab_count, content_count, demo_count, base_weights)
    print("Pesos dinámicos:", dynamic_w)
    print("Vecinos colaborativos:", collab_count, "Recs contenido:", content_count, "Recs demográficas:", demo_count)
    
    # Combinar scores de todos los sistemas
    all_items = set(rec_collab.keys()) | set(rec_content.keys()) | set(rec_demo.keys())
    hybrid_scores = {}
    for item in all_items:
        score = 0
        sources = 0
        if item in rec_collab:
            score += dynamic_w['collaborative'] * rec_collab[item]
            sources += 1
        if item in rec_content:
            score += dynamic_w['content'] * rec_content[item]
            sources += 1
        if item in rec_demo:
            score += dynamic_w['demographic'] * rec_demo[item]
            sources += 1
        hybrid_scores[item] = score
    
    # Ordenar y retornar las top_n recomendaciones
    hybrid_sorted = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return hybrid_sorted[:top_n]