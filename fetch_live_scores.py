import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore
import firebase_admin
import os
import json
from datetime import datetime

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
    """SofaScore'dan canlı maç verilerini çeker"""
    url = "https://www.sofascore.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        matches = []
        match_elements = soup.find_all("div", class_="event")
        
        for match in match_elements[:30]:
            try:
                home_team = match.find("div", class_="participant-home").text.strip()
                away_team = match.find("div", class_="participant-away").text.strip()
                score = match.find("div", class_="score").text.strip()
                
                matches.append({
                    "ev_sahibi": home_team,
                    "deplasman": away_team,
                    "skor": score,
                    "guncelleme_zamani": datetime.now().isoformat()
                })
            except:
                continue
        
        print(f"✅ {len(matches)} maç bulundu")
        return matches
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return []

def update_firestore(matches):
    if not matches:
        print("⚠️ Güncellenecek maç bulunamadı")
        return
    
    try:
        collection_ref = db.collection("mac_sonuclari")
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        
        for idx, match in enumerate(matches):
            collection_ref.document(f"mac_{idx}").set(match)
        
        print(f"✅ {len(matches)} maç güncellendi")
        
    except Exception as e:
        print(f"❌ Firebase hatası: {e}")

def fetch_and_update_scores():
    """Ana fonksiyon"""
    print(f"🔄 Maç sonuçları güncelleniyor...")
    matches = fetch_live_scores()
    update_firestore(matches)

if __name__ == "__main__":
    fetch_and_update_scores()