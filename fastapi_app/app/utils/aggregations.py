"""
Pipeline builders pour agrégations MongoDB réutilisables.
"""
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime


def build_search_pipeline(
    query: Optional[str] = None,
    category_slug: Optional[str] = None,
    price_min: Optional[Decimal] = None,
    price_max: Optional[Decimal] = None,
    tags: Optional[List[str]] = None,
    is_active: bool = True,
    sort_by: str = "relevance",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20
) -> List[Dict[str, Any]]:
    """
    Construit un pipeline d'agrégation MongoDB pour la recherche avancée.
    Retourne une liste d'étapes à passer à collection.aggregate().
    """
    pipeline = []

    # 1️⃣ Filtre de base : produits actifs + catégorie
    match_stage = {"$match": {"is_active": is_active}}
    if category_slug:
        match_stage["$match"]["category.slug"] = category_slug
    pipeline.append(match_stage)

    # 2️⃣ Recherche texte (si query fournie)
    if query:
        # Option A: Simple regex (compatible toutes versions MongoDB)
        text_filter = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"sku": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }
        # Ajouter au match existant ou créer nouveau stage
        if "$match" in pipeline[-1]:
            pipeline[-1]["$match"] = {"$and": [pipeline[-1]["$match"], text_filter]}
        else:
            pipeline.append({"$match": text_filter})

        # Option B: Score de pertinence (si index text créé)
        # pipeline.append({"$addFields": {"relevance_score": {"$meta": "textScore"}}})
        # pipeline.append({"$sort": {"relevance_score": {"$meta": "textScore"}}})

    # 3️⃣ Filtres prix
    price_filter = {}
    if price_min is not None:
        price_filter["$gte"] = float(price_min)
    if price_max is not None:
        price_filter["$lte"] = float(price_max)
    if price_filter:
        pipeline.append({"$match": {"price_ht": price_filter}})

    # 4️⃣ Filtres tags (match ALL ou ANY ? Ici: ANY)
    if tags:
        pipeline.append({"$match": {"tags": {"$in": tags}}})

    # 5️⃣ Tri
    sort_field = {
        "relevance": "relevance_score" if query else "created_at",
        "price": "price_ht",
        "rating": "rating.average",
        "created_at": "created_at"
    }.get(sort_by, "created_at")

    sort_direction = 1 if sort_order.lower() == "asc" else -1
    pipeline.append({"$sort": {sort_field: sort_direction}})

    # 6️⃣ Pagination : compter le total AVANT skip/limit
    pipeline.append({
        "$facet": {
            "results": [
                {"$skip": (page - 1) * per_page},
                {"$limit": per_page}
            ],
            "total": [{"$count": "count"}]
        }
    })

    # 7️⃣ Formatage de la réponse
    pipeline.append({
        "$project": {
            "results": 1,
            "total": {"$arrayElemAt": ["$total.count", 0]},
            "page": {"$literal": page},
            "per_page": {"$literal": per_page}
        }
    })

    return pipeline
