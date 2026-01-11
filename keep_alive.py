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
    print("BOT BASLATILDI - Her 30 saniyede guncelleme")
    print("Ilk guncelleme basliyor...")
    fetch_live_scores.fetch_and_update_scores()
    
    while True:
        time.sleep(30)
        print("Yeni guncelleme...")
        fetch_live_scores.fetch_and_update_scores()

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    app.run(host='0.0.0.0', port=10000)