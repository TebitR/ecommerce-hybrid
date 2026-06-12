# E-Shop PRO — Application Flutter

Client mobile et web de la plateforme e-commerce hybride (`ecommerce-hybrid`).

## Prérequis

- Flutter SDK 3.12+
- Backend Docker lancé (Django `8000`, FastAPI `8001`)

## Lancer l'app

```powershell
cd flutter_app
flutter pub get
flutter run -d chrome
```

## Configuration réseau

Les URLs API sont dans **`lib/core/network/api_client.dart`** (`_host = '192.168.1.117'`).

| Contexte | Django | FastAPI |
|----------|--------|---------|
| Même PC (Chrome) | `http://localhost:8000/api/v1` | `http://localhost:8001/api/v2` |
| Émulateur Android | `http://10.0.2.2:8000/api/v1` | `http://10.0.2.2:8001/api/v2` |
| Téléphone (Wi-Fi) | `http://VOTRE_IP:8000/api/v1` | `http://VOTRE_IP:8001/api/v2` |

Trouver votre IP : `ipconfig` (Windows) → Adresse IPv4.

Ajoutez aussi votre IP dans `ALLOWED_HOSTS` du fichier `.env` à la racine du monorepo, puis :

```powershell
docker compose up -d --force-recreate django celery_worker
```

Documentation complète : [README principal](../README.md#configuration-réseau--adresse-ip).

## Structure

```
lib/
├── core/
│   ├── network/api_client.dart
│   ├── services/     # auth, shop, order
│   ├── providers/    # cart
│   └── theme/
└── presentation/screens/
    ├── login_screen.dart
    ├── register_screen.dart
    ├── home_screen.dart
    ├── product_detail_screen.dart
    ├── cart_screen.dart
    └── order_tracking_screen.dart
```

## Documentation

Voir le [README du monorepo](../README.md) pour l'architecture, le checkout et le dépannage.
