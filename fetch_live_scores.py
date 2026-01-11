import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Environment variable'dan Firebase credentials oku
creds_json = os.environ.get('FIREBASE_CREDENTIALS')
if creds_json:
    cred_dict = json.loads(creds_json)
    cred = credentials.Certificate(cred_dict)
else:
    # Lokal test için (opsiyonel)
    cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_live_scores():
    """Mackolik'ten canli mac sonuclarini ceker"""
    url = "https://www.mackolik.com/canli-sonuclar"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        maclar = []
        mac_elemanlari = soup.find_all('div', class_='match-row')
        
        for mac in mac_elemanlari[:20]:  # Ilk 20 mac
            try:
                ev_sahibi = mac.find('span', class_='home-team').text.strip()
                deplasman = mac.find('span', class_='away-team').text.strip()
                skor = mac.find('span', class_='score').text.strip()
                durum = mac.find('span', class_='status').text.strip()
                
                maclar.append({
                    'ev_sahibi': ev_sahibi,
                    'deplasman': deplasman,
                    'skor': skor,
                    'durum': durum,
                    'guncelleme_zamani': datetime.now().isoformat()
                })
            except AttributeError:
                continue
        
        return maclar
    
    except Exception as e:
        print(f"Hata: {e}")
        return []

def update_firestore(maclar):
    """Firebase'e mac sonuclarini kaydeder"""
    if not maclar:
        print("Guncellenecek mac bulunamadi")
        return
    
    try:
        collection_ref = db.collection('mac_sonuclari')
        
        # Eski kayitlari sil
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        
        # Yeni kayitlari ekle
        for mac in maclar:
            collection_ref.add(mac)
        
        print(f"Basarili! {len(maclar)} mac guncellendi")
    
    except Exception as e:
        print(f"Firebase hatasi: {e}")

def fetch_and_update_scores():
    """Ana fonksiyon: Skorlari cek ve guncelle"""
    print("Mac sonuclari cekiliyor...")
    maclar = fetch_live_scores()
    update_firestore(maclar)

if __name__ == '__main__':
    fetch_and_update_scores()