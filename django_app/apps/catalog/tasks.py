import logging
import os

from celery import shared_task
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


# Connexion MongoDB (lazy init pour éviter les imports circulaires)
def get_mongo_client():
    mongo_url = os.environ.get(
        "MONGODB_URL",
        "mongodb://admin:MongoPass123@mongodb:27017/ecommerce_catalog?authSource=admin",
    )
    return MongoClient(mongo_url)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_product_to_mongo(self, product_id: int):
    """
    Synchronise un produit PostgreSQL → MongoDB.
    Upsert : met à jour si existe, crée sinon.
    """
    try:
        from apps.catalog.models import Product

        # Récupérer le produit depuis PostgreSQL
        product = Product.objects.select_related("category").get(id=product_id)

        # Sécurisation du slug : si le slug vaut "informatique" ou est générique,
        # on lui ajoute le SKU pour garantir l'unicité stricte exigée par l'index MongoDB
        raw_slug = product.category.slug if product.category else None
        mongo_slug = raw_slug if raw_slug else "product"
        if mongo_slug == "informatique" or not raw_slug:
            mongo_slug = f"{mongo_slug}-{product.sku.lower()}"

        # Compiler le document MongoDB (format exact du cahier des charges)
        product_document = {
            "postgres_id": str(product.id),  # Lien vers PostgreSQL
            "mongo_id": product.mongo_id or None,  # Sera généré si null
            "sku": product.sku,
            "name": product.name,
            "slug": mongo_slug,
            "category": {
                "id": str(product.category.id) if product.category else None,
                "name": product.category.name if product.category else None,
                "slug": product.category.slug if product.category else None,
            }
            if product.category
            else None,
            "price_ht": float(product.price),
            "tax_rate": float(product.tax_rate),
            "price_ttc": float(product.price * (1 + product.tax_rate)),
            "stock_quantity": product.stock_quantity,
            "stock_reserved": product.stock_reserved,
            "stock_available": product.stock_quantity - product.stock_reserved,
            "is_active": product.is_active,
            "attributes": {},  # À enrichir plus tard avec JSONField
            "images": [],  # À enrichir avec un modèle Image
            "rating": {"average": 0.0, "count": 0},
            "tags": [],  # À enrichir avec un modèle Tag
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        }

        # Upsert dans MongoDB (update si postgres_id existe, insert sinon)
        client = get_mongo_client()
        db = client.get_database()
        collection = db["products"]

        result = collection.update_one(
            {"postgres_id": str(product.id)},
            {"$set": product_document},
            upsert=True,
        )

        # Mettre à jour mongo_id dans PostgreSQL si généré
        if result.upserted_id and not product.mongo_id:
            product.mongo_id = str(result.upserted_id)
            product.save(update_fields=["mongo_id"])

        logger.info(
            "Produit %s sync vers MongoDB (upserted=%s)",
            product.sku,
            result.upserted_id is not None,
        )
        return {
            "status": "success",
            "sku": product.sku,
            "upserted": result.upserted_id is not None,
        }

    except Product.DoesNotExist:
        logger.warning("Produit #%s non trouvé pour sync MongoDB", product_id)
        return {"status": "not_found", "product_id": product_id}

    except PyMongoError as e:
        logger.error("Erreur MongoDB pour produit #%s: %s", product_id, e)
        raise self.retry(exc=e, countdown=60)

    except Exception as e:
        logger.error("Erreur inattendue pour produit #%s: %s", product_id, e)
        raise self.retry(exc=e, countdown=120)

    finally:
        if "client" in locals():
            client.close()


@shared_task(bind=True, max_retries=2)
def delete_product_from_mongo(self, product_id: int):
    """Supprime un produit de MongoDB par son postgres_id."""
    try:
        client = get_mongo_client()
        db = client.get_database()
        result = db["products"].delete_one({"postgres_id": str(product_id)})
        logger.info(
            "Produit PostgreSQL #%s supprimé de MongoDB (deleted_count=%s)",
            product_id,
            result.deleted_count,
        )
        return {"status": "deleted", "product_id": product_id}
    except PyMongoError as e:
        logger.error("Erreur MongoDB delete pour produit #%s: %s", product_id, e)
        raise self.retry(exc=e, countdown=30)
    finally:
        if "client" in locals():
            client.close()
