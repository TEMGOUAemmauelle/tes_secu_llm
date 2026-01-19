import json
from attacks import prompt_injection, jailbreak

def main():
    results = []
    results += prompt_injection.run()
    results += jailbreak.run()

    with open("logs/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✔ Tests terminés. Résultats dans logs/results.json")

if __name__ == "__main__":
    main()
