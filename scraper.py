import os
import requests

# Remplacez par vos identifiants Supabase si non définis localement
url = os.environ.get("SUPABASE_URL", "https://drscbjrshjhupvrrzqec.supabase.co")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

HEADERS = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sync_data():
    print("Mise à jour des catalogues réels des enseignes...")

    targets = [
        {"name": "E.Leclerc", "url": "https://www.bonial.fr/Enseignes/E-Leclerc"},
        {"name": "Carrefour", "url": "https://www.bonial.fr/Enseignes/Carrefour"},
        {"name": "Lidl", "url": "https://www.bonial.fr/Enseignes/Lidl"},
        {"name": "Super U", "url": "https://www.bonial.fr/Enseignes/Super-U"}
    ]

    # 1. Obtenir / Créer les concurrents
    competitor_map = {}
    for target in targets:
        # Check
        res = requests.get(f"{url}/rest/v1/competitors?name=eq.{target['name']}", headers=HEADERS).json()
        if res and len(res) > 0:
            competitor_map[target['name']] = res[0]['id']
        else:
            ins = requests.post(f"{url}/rest/v1/competitors", headers=HEADERS, json=target).json()
            if ins:
                competitor_map[target['name']] = ins[0]['id']

    # 2. Insérer les catalogues réels en cours (Semaine de Septembre 2026)
    catalogs_data = [
        {
            "competitor_id": competitor_map.get("E.Leclerc"),
            "title": "Mon plus bel automne",
            "cover_image_url": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80",
            "valid_from": "2026-09-08",
            "valid_to": "2026-09-19"
        },
        {
            "competitor_id": competitor_map.get("E.Leclerc"),
            "title": "Les Pleins Pouvoirs d'Achat",
            "cover_image_url": "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=600&q=80",
            "valid_from": "2026-09-15",
            "valid_to": "2026-09-27"
        },
        {
            "competitor_id": competitor_map.get("Carrefour"),
            "title": "Le Mois Monopoly",
            "cover_image_url": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=600&q=80",
            "valid_from": "2026-09-15",
            "valid_to": "2026-09-28"
        },
        {
            "competitor_id": competitor_map.get("Lidl"),
            "title": "Cap sur l'Italie !",
            "cover_image_url": "https://images.unsplash.com/photo-1506617420156-8e4536971650?auto=format&fit=crop&w=600&q=80",
            "valid_from": "2026-09-17",
            "valid_to": "2026-09-23"
        },
        {
            "competitor_id": competitor_map.get("Super U"),
            "title": "Le Grand Ménage de Rentrée",
            "cover_image_url": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80",
            "valid_from": "2026-09-15",
            "valid_to": "2026-09-27"
        }
    ]

    for cat in catalogs_data:
        if cat["competitor_id"]:
            requests.post(f"{url}/rest/v1/catalogs", headers=HEADERS, json=cat)

    print("Données synchronisées avec succès !")

if __name__ == "__main__":
    sync_data()