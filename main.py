from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import time

app = FastAPI(title="API CDM 2026 - Flashscore Scraper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

FLASHSCORE_URL = "https://www.flashscore.fr/football/monde/championnat-du-monde/classement/SbLsX4y7/top-buteurs/"

cache = {
    "total_goals": 0,
    "last_updated": 0
}
# Cache de 5 minutes (300s) pour ne pas surcharger la machine avec le navigateur
CACHE_TTL = 300 

@app.get("/api/total-goals")
async def get_total_goals():
    current_time = time.time()
    
    # Retourne le cache s'il est encore valide
    if current_time - cache["last_updated"] < CACHE_TTL:
        return {
            "total_goals": cache["total_goals"], 
            "source": "cache"
        }

    try:
        # Lancement du navigateur en mode invisible
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True) 
            page = await browser.new_page()
            
            # Navigation et attente de la fin des requêtes réseau
            await page.goto(FLASHSCORE_URL, wait_until="networkidle")
            
            # 1. On attend l'apparition de la classe exacte de la ligne que tu as trouvée
            await page.wait_for_selector(".topScorers__row", timeout=15000)
            
            total_buts = 0
            
            # 2. On récupère toutes les lignes des buteurs
            lignes = await page.query_selector_all(".topScorers__row")
            
            for ligne in lignes:
                # 3. On cible précisément la cellule des buts avec ta classe CSS
                cellule_but = await ligne.query_selector(".topScorers__cell--goals")
                if cellule_but:
                    texte = await cellule_but.inner_text()
                    try:
                        # Ajout au total
                        total_buts += int(texte.strip())
                    except ValueError:
                        pass 
            
            await browser.close()
            
            # Mise à jour du cache
            cache["total_goals"] = total_buts
            cache["last_updated"] = current_time
            
            print(f"Total calculé via Flashscore : {total_buts}")
            
            return {
                "total_goals": cache["total_goals"], 
                "source": "flashscore_playwright"
            }
            
    except Exception as e:
        print(f"Erreur Playwright : {str(e)}")
        return {"error": "Erreur lors du scraping", "details": str(e)}