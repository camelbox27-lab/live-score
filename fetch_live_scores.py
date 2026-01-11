import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore
import firebase_admin
import os
import json

# Environment variable'dan Firebase credentials oku
creds_json = os.environ.get('FIREBASE_CREDENTIALS')
if creds_json:
    cred_dict = json.loads(creds_json)
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate("serviceAccountKey.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_live_scores():
    url = "https://www.sofascore.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    matches = []
    
    # SofaScore'dan maç verilerini çek
    match_elements = soup.find_all("div", class_="event")
    
    for match in match_elements:
        try:
            home_team = match.find("div", class_="participant-home").text.strip()
            away_team = match.find("div", class_="participant-away").text.strip()
            score = match.find("div", class_="score").text.strip()
            
            matches.append({
                "ev_sahibi": home_team,
                "deplasman": away_team,
                "skor": score
            })
        except:
            continue
    
    return matches

def update_firestore(matches):
    collection_ref = db.collection("mac_sonuclari")
    
    # Eski verileri sil
    docs = collection_ref.stream()
    for doc in docs:
        doc.reference.delete()
    
    # Yeni verileri ekle
    for match in matches:
        collection_ref.add(match)
    
    print(f"Basarili! {len(matches)} mac guncellendi")

def fetch_and_update_scores():
    matches = fetch_live_scores()
    update_firestore(matches)

if __name__ == "__main__":
    fetch_and_update_scores()