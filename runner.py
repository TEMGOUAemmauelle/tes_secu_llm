import subprocess
import time
import json
import requests
import threading

from attacks.prompt_injection import run as run_prompt_injection
from attacks.jailbreak import run as run_jailbreak

API_URL = "http://localhost:8000"

def log_output(process):
    """Thread pour logger stdout et stderr du processus API en temps réel."""
    def read_stream(stream, label):
        for line in iter(stream.readline, b''):
            print(f"[{label}] {line.decode('utf-8').strip()}")

    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "API_STDOUT"))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "API_STDERR"))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

def start_api():
    print("[+] Démarrage du serveur LLM API...")
    process = subprocess.Popen(
        ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    log_output(process)  # Lancer le logging en background
    return process

def wait_for_api(timeout=300):
    print("[*] Attente que l'API soit disponible...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            r = requests.get(f"{API_URL}/health", timeout=5)  # Augmenté à 5s pour le health check
            if r.status_code == 200:
                print("[+] API prête ✔")
                return True
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Erreur health check: {e}")
            pass

        time.sleep(2)

    raise RuntimeError("❌ Timeout : l'API n'est jamais devenue disponible")

def main():
    api_process = start_api()

    try:
        wait_for_api()

        time.sleep(5)  # Pause supplémentaire pour s'assurer que l'API est stable

        print("[+] Lancement des attaques...")
        results = []
        results += run_prompt_injection()
        results += run_jailbreak()

        with open("logs/results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("✔ Tests terminés. Résultats dans logs/results.json")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
    finally:
        print("[+] Arrêt du serveur API...")
        api_process.terminate()
        api_process.wait()  # Attendre que le process se termine proprement
        print("[+] Serveur arrêté.")

if __name__ == "__main__":
    main()
