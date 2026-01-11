from flask import Flask
import threading
import time
import fetch_live_scores

app = Flask(__name__)

@app.route('/')
def home():
    return "Maç Sonuçları Tracker Çalışıyor!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def run_scheduler():
    # 5 saniye bekle (Flask başlasın)
    time.sleep(5)
    
    print("=" * 60)
    print("BOT BASLATILDI - Her 30 saniyede guncelleme")
    print("=" * 60)
    print("Ilk guncelleme basliyor...")
    
    try:
        fetch_live_scores.fetch_and_update_scores()
    except Exception as e:
        print(f"Hata: {e}")
    
    while True:
        time.sleep(30)
        print("=" * 60)
        print("Yeni guncelleme...")
        print("=" * 60)
        try:
            fetch_live_scores.fetch_and_update_scores()
        except Exception as e:
            print(f"Hata: {e}")

if __name__ == '__main__':
    print("Flask baslaniyor...")
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("Thread baslatildi!")
    
    app.run(host='0.0.0.0', port=10000)