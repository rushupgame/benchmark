import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Connexion Supabase via les variables d'environnement
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # On utilise la clé service role pour écrire
supabase: Client = create_client(url, key)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_bonial(competitor_name, bonial_url):
    print(f"Scraping de {competitor_name}...")
    
    # 1. Vérifier ou insérer le concurrent dans la base
    res = supabase.table("competitors").select("id").eq("name", competitor_name).execute()
    if not res.data:
        comp = supabase.table("competitors").insert({"name": competitor_name, "bonial_url": bonial_url}).execute()
        competitor_id = comp.data[0]["id"]
    else:
        competitor_id = res.data[0]["id"]

    # 2. Scraper les catalogues Bonial
    response = requests.get(bonial_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraction basique des brochures sur Bonial
    brochures = soup.find_all('article') or soup.find_all('div', class_=lambda c: c and 'brochure' in c.lower())
    
    for item in brochures[:5]: # On prend les 5 premiers catalogues
        title_elem = item.find(['h2', 'h3', 'p'])
        img_elem = item.find('img')
        
        if title_elem and img_elem:
            title = title_elem.get_text(strip=True)
            img_url = img_elem.get('src') or img_elem.get('data-src')
            
            if img_url and not img_url.startswith('http'):
                img_url = 'https:' + img_url

            # Éviter les doublons sur le titre et le concurrent
            check = supabase.table("catalogs").select("id").eq("competitor_id", competitor_id).eq("title", title).execute()
            if not check.data:
                supabase.table("catalogs").insert({
                    "competitor_id": competitor_id,
                    "title": title,
                    "cover_image_url": img_url,
                    "valid_from": "2026-09-15",
                    "valid_to": "2026-09-30"
                }).execute()
                print(f"Nouveau catalogue ajouté : {title}")

if __name__ == "__main__":
    targets = [
        {"name": "E.Leclerc", "url": "https://www.bonial.fr/Enseignes/E-Leclerc"},
        {"name": "Carrefour", "url": "https://www.bonial.fr/Enseignes/Carrefour"},
        {"name": "Lidl", "url": "https://www.bonial.fr/Enseignes/Lidl"}
    ]
    
    for target in targets:
        scrape_bonial(target["name"], target["url"])