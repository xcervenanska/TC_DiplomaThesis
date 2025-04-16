# Inštalačný manuál pre projekt na operačnom systéme Windows

Táto príručka obsahuje podrobné inštrukcie pre inštaláciu a spustenie projektu na počítači s operačným systémom Windows. Projekt využíva Ollama na lokálne spúšťanie veľkých jazykových modelov (LLM), Docker na kontajnerizáciu a Docker Compose na orchestráciu aplikácie. 

## 1. Inštalácia Ollama a stiahnutie požadovaného modelu
Ollama umožňuje lokálne spúšťanie veľkých jazykových modelov (LLM).

Stiahnutie Ollama: Navštívte stránku https://ollama.ai/download/windows a stiahnite si inštalačný súbor pre Windows.

Inštalácia Ollama: Spustite stiahnutý inštalačný súbor a postupujte podľa inštrukcií.

Otvorenie terminálu: Otvorte nový príkazový riadok (Command Prompt) alebo PowerShell.

Stiahnutie modelu: Použite nasledujúci príkaz na stiahnutie modelu phi4-mini:


ollama pull phi4-mini

Počkajte, kým sa stiahnutie dokončí.

## 2. Inštalácia Docker Desktop
Docker je platforma pre spúšťanie aplikácií v kontajneroch.

Stiahnutie Docker Desktop: Prejdite na stránku https://www.docker.com/products/docker-desktop/ a stiahnite Docker Desktop pre Windows.

Inštalácia Docker Desktop: Spustite inštalačný súbor. Pri inštalácii povoľte integráciu WSL 2, ak budete vyzvaní. Ak ešte nemáte povolenú virtualizáciu, zapnite ju v nastaveniach BIOS.

Spustenie Docker Desktop: Po inštalácii spustite Docker Desktop z ponuky Štart. Môže byť potrebné prihlásiť sa alebo vytvoriť účet.

Overenie inštalácie: Otvorte nový príkazový riadok alebo PowerShell a spustite:


docker --version
docker compose version

Tieto príkazy overia správnu inštaláciu Docker a Docker Compose.

## 3. Klonovanie GitHub repozitára
Naklonujte repozitár projektu na váš počítač.

Otvorenie príkazového riadku alebo PowerShell: Prejdite do adresára, v ktorom chcete projekt uložiť.

Klonovanie repozitára: Spustite nasledujúci príkaz:

git clone https://github.com/xcervenanska/TC_DiplomaThesis

Prechod do adresára projektu:


cd TC_DiplomaThesis


## 4. Konfigurácia súboru .env
Vytvorte a nastavte súbor .env s potrebnými premennými prostredia.

Vytvorenie súboru .env: V koreňovom adresári projektu (t.j. TC_DiplomaThesis) vytvorte súbor s názvom .env.

Úprava súboru .env: Otvorte súbor v textovom editore a vložte nasledovný obsah:


BACKEND_URL=http://localhost:8000
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=phi4-mini
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHROMA_ALLOW_RESET=true
CHROMA_ANONYMIZED_TELEMETRY=false
CHROMA_IS_PERSISTENT=true
DISTANCE_THRESHOLD=1.5
N_RESULTS=5  # Počet úsekov textu načítaných pri dopytoch do dokumentov

BACKEND_URL: URL adresa backendovej služby.

OLLAMA_BASE_URL: URL adresa pre server Ollama. Použitie host.docker.internal umožňuje prístup k hostiteľskému počítaču z Docker kontajnera v systéme Windows.

OLLAMA_MODEL: Názov používaného Ollama modelu (phi4-mini v tomto prípade).

CHUNK_SIZE, CHUNK_OVERLAP, DISTANCE_THRESHOLD, N_RESULTS: Parametre ovplyvňujúce spracovanie dokumentov.

CHROMA_*: Nastavenia databázy ChromaDB.

Uložte súbor.

## 5. Spustenie projektu pomocou Docker Compose
Pomocou Docker Compose zostavíte a spustíte aplikáciu.

Otvorenie príkazového riadku alebo PowerShell: Prejdite do koreňového adresára projektu (TC_DiplomaThesis), ak sa tam ešte nenachádzate.

Spustenie Docker Compose: Spustite nasledujúci príkaz:


docker compose up --build

Tento príkaz vykoná nasledovné operácie:

--build: Zostaví Docker obrazy pre backend a frontend, ak ešte neexistujú, alebo ak nastali zmeny v Dockerfile súboroch.

up: Spustí kontajnery definované v súbore docker-compose.yml.

Počkajte, kým sa proces zostavovania dokončí. Vývoj môžete sledovať v termináli.

## 6. Prístup k aplikácii
Po dokončení príkazu Docker Compose a spustení kontajnerov môžete pristúpiť k aplikácii cez webový prehliadač.

Backend služba: Otvorte webový prehliadač a prejdite na http://localhost:8000. Mali by ste vidieť predvolenú stránku FastAPI.

Streamlit Frontend: Otvorte webový prehliadač a prejdite na http://localhost:8501. Tým sa otvorí frontendová aplikácia Streamlit poskytujúca používateľské rozhranie pre zadávanie otázok k študijným materiálom.



 
