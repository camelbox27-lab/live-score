from flask import Flask
import threading
import time
from fetch_live_scores import fetch_and_update_scores

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Maç Sonuçları Tracker</title>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>✅ Maç Sonuçları Tracker Çalışıyor!</h1>
        <p>🔄 Her 30 saniyede bir güncelleniyor</p>
        <p>⚽ SofaScore'dan canlı maç verileri çekiliyor</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "message": "Bot aktif"}, 200

def run_scheduler():
    """Her 30 saniyede bir skorları güncelle"""
    
    # İlk başta 1 kez çalıştır
    print("🚀 İlk güncelleme başlıyor...")
    fetch_and_update_scores()
    
    while True:
        time.sleep(30)  # 30 saniye bekle
        print("🔄 Yeni güncelleme başlıyor...")
        fetch_and_update_scores()

if __name__ == '__main__':
    # Scheduler'ı arka planda çalıştır
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("=" * 60)
    print("✅ BOT BAŞLATILDI!")
    print("🔄 Her 30 saniyede güncelleme yapılacak")
    print("⚽ SofaScore → Firebase otomatik senkronizasyon")
    print("=" * 60)
    
    # Flask'ı başlat (Render canlı tutmak için)
    app.run(host='0.0.0.0', port=10000)