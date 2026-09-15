import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def scrape_bonial(competitor_name, bonial_url):
    print(f"Scraping de {competitor_name}...")
    
    # Vérification/Création du concurrent
    res = supabase.table("competitors").select("id").eq("name", competitor_name).execute()
    if not res.data:
        comp = supabase.table("competitors").insert({"name": competitor_name, "bonial_url": bonial_url}).execute()
        competitor_id = comp.data[0]["id"]
    else:
        competitor_id = res.data[0]["id"]

    try:
        response = requests.get(bonial_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} sur {bonial_url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Détection des cartes de catalogues sur la version actuelle de Bonial
        cards = soup.select('a[data-test-id*="brochure"], a[href*="/Brochures/"], div[class*="BrochureCard"], a[class*="Tile"]')
        
        if not cards:
            # Fallback : recherche générique des liens contenant des images et des titres
            cards = [a for a in soup.find_all('a', href=True) if '/Brochures/' in a['href'] or 'brochure' in a['href'].lower()]

        print(f"Trouvé {len(cards)} éléments pour {competitor_name}")

        count = 0
        for item in cards:
            if count >= 6: break # Max 6 catalogues par enseigne
            
            # Récupération du titre
            title_elem = item.select_one('h2, h3, [class*="title"], [class*="Title"]')
            title = title_elem.get_text(strip=True) if title_elem else item.get('title', '')
            
            # Récupération de l'image de couverture
            img_elem = item.find('img')
            img_url = ""
            if img_elem:
                img_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('srcset', '').split(' ')[0]
            
            if title and img_url:
                if not img_url.startswith('http'):
                    img_url = 'https:' + img_url if img_url.startswith('//') else 'https://www.bonial.fr' + img_url

                # Éviter les doublons dans Supabase
                check = supabase.table("catalogs").select("id").eq("competitor_id", competitor_id).eq("title", title).execute()
                if not check.data:
                    supabase.table("catalogs").insert({
                        "competitor_id": competitor_id,
                        "title": title,
                        "cover_image_url": img_url,
                        "valid_from": "2026-09-15",
                        "valid_to": "2026-09-30"
                    }).execute()
                    print(f"  --> Catalogue réel ajouté : {title}")
                    count += 1

    except Exception as e:
        print(f"Erreur scraping {competitor_name}: {e}")

if __name__ == "__main__":
    targets = [
        {"name": "E.Leclerc", "url": "https://www.bonial.fr/Enseignes/E-Leclerc"},
        {"name": "Carrefour", "url": "https://www.bonial.fr/Enseignes/Carrefour"},
        {"name": "Lidl", "url": "https://www.bonial.fr/Enseignes/Lidl"},
        {"name": "Super U", "url": "https://www.bonial.fr/Enseignes/Super-U"}
    ]
    
    for target in targets:
        scrape_bonial(target["name"], target["url"])