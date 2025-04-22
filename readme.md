
# Inštalačný manuál pre projekt

Tento návod poskytuje podrobné pokyny na inštaláciu a spustenie projektu na počítači so systémom Windows. Projekt využíva Ollama na lokálne spracovanie veľkých jazykových modelov (LLM), Docker na kontajnerizáciu a Docker Compose na orchestráciu aplikácie.

## Štruktúra projektu

```
.
├── backend
│   ├── app/                # Backend application code
│   ├── main.py             # Entry point for the backend service
│   ├── requirements.txt    # Python dependencies for the backend
│   └── Dockerfile          # Dockerfile to build the backend image
├── streamlit_frontend
│   ├── pages/              # Streamlit pages
│   ├── Home.py             # Main Streamlit application file
│   ├── requirements.txt    # Python dependencies for the frontend
│   └── Dockerfile          # Dockerfile to build the frontend image
└── .env                    # Environment variables configuration file
```

## 1. Inštalácia Ollama a stiahnutie požadovaného modelu

Ollama umožňuje spúšťať veľké jazykové modely (LLM) lokálne.

1. Stiahnite si Ollama: Prejdite na [https://ollama.ai/download/windows](https://ollama.ai/download/windows) a stiahnite inštalačný súbor pre Windows.  
2. Nainštalujte Ollama: Spustite inštalátor a postupujte podľa pokynov na obrazovke.  
3. Otvorte terminál: Spustite Command Prompt alebo PowerShell.  
4. Stiahnite model: Zadajte nasledujúci príkaz:

```bash
ollama pull phi4-mini
```

Počkajte na dokončenie sťahovania modelu.

## 2. Inštalácia Docker Desktop

Docker umožňuje spúšťať aplikácie v izolovaných kontajneroch.

1. Stiahnite si Docker Desktop: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)  
2. Nainštalujte Docker Desktop: Spustite inštalátor. Počas inštalácie povolte WSL 2 integráciu, ak budete k tomu vyzvaní. Ak virtualizácia nie je povolená, možno ju bude potrebné zapnúť v BIOS-e.  
3. Spustite Docker Desktop: Po dokončení inštalácie ho otvorte cez Štart menu.  
4. Overte inštaláciu: Spustite príkazový riadok a zadajte:

```bash
docker --version
docker compose version
```

Ak sa zobrazia verzie, Docker bol nainštalovaný správne.

## 3. Klonovanie repozitára z GitHubu

1. Otvorte Command Prompt alebo PowerShell.  
2. Prejdite do adresára, kde chcete projekt uložiť.  
3. Klonujte repozitár:

```bash
git clone https://github.com/xcervenanska/TC_DiplomaThesis
```

4. Prejdite do adresára projektu:

```bash
cd TC_DiplomaThesis
```

## 4. Konfigurácia súboru `.env`

Systém používa konfiguračný súbor `.env` na uloženie dôležitých premenných prostredia.

1. Skontrolujte, či sa v koreňovom adresári nachádza súbor `.env`. Ak nie, vytvorte ho.  
2. Otvorte ho v textovom editore a skontrolujte, či obsahuje:

```env
BACKEND_URL=http://localhost:8000
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=phi4-mini
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHROMA_ALLOW_RESET=true
CHROMA_ANONYMIZED_TELEMETRY=false
CHROMA_IS_PERSISTENT=true
DISTANCE_THRESHOLD=1.5
N_RESULTS=5
```

### Vysvetlenie premenných:
- `BACKEND_URL` – URL adresa backendu.
- `OLLAMA_BASE_URL` – URL Ollama servera (v Docker kontejnere použite `host.docker.internal`).
- `OLLAMA_MODEL` – Model, ktorý bude použitý (`phi4-mini`).
- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `DISTANCE_THRESHOLD`, `N_RESULTS` – Nastavenia ovplyvňujúce proces RAG.
- `CHROMA_` – Nastavenia databázy ChromaDB.

Uložte súbor `.env`.

## 5. Spustenie projektu pomocou Docker Compose

1. Otvorte terminál (Command Prompt alebo PowerShell).  
2. Prejdite do adresára projektu:

```bash
cd TC_DiplomaThesis
```

3. Spustite Docker Compose:

```bash
docker compose up --build
```

Tento príkaz:
- zostaví Docker obrazy backendu a frontendu,
- spustí kontajnery podľa `docker-compose.yml`.

Výstup sa zobrazí v termináli.

## 6. Prístup k aplikácii

Po úspešnom spustení kontajnerov bude aplikácia dostupná cez webový prehliadač:

- **Backend služba**: [http://localhost:8000](http://localhost:8000)  
  Zobrazí sa FastAPI rozhranie.
- **Streamlit frontend**: [http://localhost:8501](http://localhost:8501)  
  Grafické užívateľské rozhranie na kladenie otázok k dokumentom.
