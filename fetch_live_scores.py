import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import requests
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
    """SofaScore API'den canli mac sonuclarini ceker"""
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.sofascore.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        maclar = []
        
        if 'events' in data:
            for event in data['events'][:30]:  # İlk 30 maç
                try:
                    ev_sahibi = event.get('homeTeam', {}).get('name', 'Bilinmiyor')
                    deplasman = event.get('awayTeam', {}).get('name', 'Bilinmiyor')
                    
                    home_score = event.get('homeScore', {}).get('current', 0)
                    away_score = event.get('awayScore', {}).get('current', 0)
                    skor = f"{home_score}-{away_score}"
                    
                    status = event.get('status', {}).get('description', 'Bilinmiyor')
                    durum = status
                    
                    # Dakika bilgisi
                    time_str = event.get('time', {}).get('currentPeriodStartTimestamp', '')
                    
                    lig = event.get('tournament', {}).get('name', 'Bilinmiyor')
                    ulke = event.get('tournament', {}).get('category', {}).get('name', '')
                    
                    maclar.append({
                        'ev_sahibi': ev_sahibi,
                        'deplasman': deplasman,
                        'skor': skor,
                        'durum': durum,
                        'lig': lig,
                        'ulke': ulke,
                        'guncelleme_zamani': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    print(f"⚠️ Mac parse hatasi: {e}")
                    continue
        
        print(f"✅ SofaScore'dan {len(maclar)} canli mac bulundu")
        return maclar
    
    except requests.RequestException as e:
        print(f"❌ SofaScore API hatasi: {e}")
        return []
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return []

def update_firestore(maclar):
    """Firebase'e mac sonuclarini kaydeder"""
    if not maclar:
        print("⚠️ Guncellenecek mac bulunamadi")
        return
    
    try:
        collection_ref = db.collection('mac_sonuclari')
        
        # Eski kayitlari sil
        docs = collection_ref.stream()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted += 1
        
        if deleted > 0:
            print(f"🗑️ {deleted} eski kayit silindi")
        
        # Yeni kayitlari ekle
        for idx, mac in enumerate(maclar):
            collection_ref.document(f'mac_{idx}').set(mac)
        
        print(f"✅ Firebase'e {len(maclar)} mac kaydedildi")
    
    except Exception as e:
        print(f"❌ Firebase hatasi: {e}")

def fetch_and_update_scores():
    """Ana fonksiyon: Skorlari cek ve guncelle"""
    print(f"🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SofaScore'dan mac sonuclari cekiliyor...")
    maclar = fetch_live_scores()
    update_firestore(maclar)
    print("=" * 50)

if __name__ == '__main__':
    fetch_and_update_scores()