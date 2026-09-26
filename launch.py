from pyngrok import ngrok
import subprocess, time, threading

TOKEN = "3Jr76lM0rxiZsISGcfAxakSIhk9_sBuePbWaNvma3TFANJbb"
ngrok.set_auth_token(TOKEN)

print("Starting Gold Pro app on NEW port 8502...")

def run_app():
    subprocess.run(["python", "-m", "streamlit", "run", "app.py", "--server.port", "8502"])

t = threading.Thread(target=run_app, daemon=True)
t.start()
time.sleep(5)
print("Creating public link...")
url = ngrok.connect(8502)
print("\n==========================================")
print(f" YOUR APP IS LIVE: {url}")
print("==========================================")
print("\nOpen this on your PHONE NOW!")
while True:
    time.sleep(1)