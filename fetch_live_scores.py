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
    url = "https://www.sofascore.com/tr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        matches = []
        
        # Tüm olası class isimlerini dene
        selectors = [
            {"class_": "event"},
            {"class_": "match"},
            {"class_": "Box"},
            {"attrs": {"data-testid": "event-item"}},
        ]
        
        match_elements = []
        for selector in selectors:
            found = soup.find_all("div", **selector)
            if found:
                match_elements = found[:30]
                print(f"Bulunan selector: {selector}")
                break
        
        if not match_elements:
            print("Hicbir mac elementi bulunamadi")
            print("HTML icerigi kontrol ediliyor...")
            # HTML'in bir kısmını yazdır
            print(soup.prettify()[:500])
        
        for match in match_elements:
            try:
                # Farklı yapıları dene
                home = match.find("div", class_="participant-home") or match.find("div", class_="homeParticipant")
                away = match.find("div", class_="participant-away") or match.find("div", class_="awayParticipant")
                score_elem = match.find("div", class_="score") or match.find("div", class_="detailScore")
                
                if home and away:
                    home_team = home.text.strip()
                    away_team = away.text.strip()
                    score = score_elem.text.strip() if score_elem else "0-0"
                    
                    matches.append({
                        "ev_sahibi": home_team,
                        "deplasman": away_team,
                        "skor": score,
                        "guncelleme_zamani": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
        
        print(f"✅ {len(matches)} mac bulundu")
        return matches
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return []

def update_firestore(matches):
    if not matches:
        print("⚠️ Guncellenecek mac bulunamadi")
        return
    
    try:
        collection_ref = db.collection("mac_sonuclari")
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        
        for idx, match in enumerate(matches):
            collection_ref.document(f"mac_{idx}").set(match)
        
        print(f"✅ {len(matches)} mac guncellendi")
        
    except Exception as e:
        print(f"❌ Firebase hatasi: {e}")

def fetch_and_update_scores():
    print(f"🔄 Mac sonuclari guncelleniyor...")
    matches = fetch_live_scores()
    update_firestore(matches)

if __name__ == "__main__":
    fetch_and_update_scores()