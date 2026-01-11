from flask import Flask
import threading
import time
import fetch_live_scores

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Maç Sonuçları Tracker Çalışıyor! Her 30 saniyede güncelleniyor."

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def run_scheduler():
    print("🚀 İlk güncelleme başlıyor...")
    fetch_live_scores.fetch_and_update_scores()
    
    while True:
        time.sleep(30)
        print("🔄 Yeni güncelleme...")
        fetch_live_scores.fetch_and_update_scores()

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("✅ BOT BAŞLATILDI - Her 30 saniyede güncelleme")
    app.run(host='0.0.0.0', port=10000)