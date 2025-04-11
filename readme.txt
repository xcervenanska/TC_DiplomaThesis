Inštalačný manuál pre projekt Study Material RAG na Windows

Tento návod poskytuje podrobné pokyny na inštaláciu a spustenie projektu Study Material RAG (Retrieval-Augmented Generation) na počítači so systémom Windows. Projekt využíva Ollama na lokálne spracovanie veľkých jazykových modelov (LLM), Docker na kontajnerizáciu a Docker Compose na orchestráciu aplikácie. Táto aktualizovaná verzia rieši chybu "MarkItDown returned None result".

1. Inštalácia Ollama a stiahnutie požadovaného modelu

Ollama umožňuje spúšťať veľké jazykové modely (LLM) lokálne.

Stiahnite si Ollama: Prejdite na https://ollama.ai/download/windows a stiahnite inštalačný súbor pre Windows.
Nainštalujte Ollama: Spustite inštalátor a postupujte podľa pokynov na obrazovke.
Otvorte terminál: Spustite Command Prompt alebo PowerShell.
Stiahnite model: Zadajte nasledujúci príkaz:

	ollama pull phi4-mini

Počkajte na dokončenie sťahovania modelu.


2. Inštalácia Docker Desktop
Docker umožňuje spúšťať aplikácie v izolovaných kontajneroch.

Stiahnite si Docker Desktop: Prejdite na https://www.docker.com/products/docker-desktop/ a stiahnite inštalačný súbor.
Nainštalujte Docker Desktop: Spustite inštalátor. Počas inštalácie povolte WSL 2 integráciu, ak budete k tomu vyzvaní. Ak virtualizácia nie je povolená, možno ju bude potrebné zapnúť v BIOS-e.
Spustite Docker Desktop: Po dokončení inštalácie ho otvorte cez Štart menu. Pri prvom spustení vás môže Docker vyzvať na prihlásenie alebo registráciu.
Overte inštaláciu: Spustite príkazový riadok a zadajte:

	docker --version
	docker compose version

Ak sa zobrazia verzie, Docker bol nainštalovaný správne.


3. Klonovanie repozitára z GitHubu
Otvorte Command Promp alebo PowerShell.
Prejdite do adresára, kde chcete projekt uložiť.
Klonujte repozitár:


	git clone https://github.com/xcervenanska/TC_DiplomaThesis

Tento príkaz stiahne všetky súbory projektu do vášho počítača.
Prejdite do adresára projektu:

	cd TC_DiplomaThesis

4. Konfigurácia súboru .env
Systém používa konfiguračný súbor .env na uloženie dôležitých premenných prostredia.

Skontrolujte, či sa v koreňovom adresári projektu (TC_DiplomaThesis) nachádza súbor .env. Ak nie, je potrebné ho vytvoriť.

Otvorte .env súbor v textovom editore a skontrolujte, či sa tam nachádzajú nasledujúce nastavenia:

	BACKEND_URL=http://localhost:8000
	OLLAMA_BASE_URL=http://host.docker.internal:11434
	OLLAMA_MODEL=phi4-mini
	CHUNK_SIZE=1000
	CHUNK_OVERLAP=200
	CHROMA_ALLOW_RESET=true
	CHROMA_ANONYMIZED_TELEMETRY=false
	CHROMA_IS_PERSISTENT=true
	DISTANCE_THRESHOLD=1.5
	N_RESULTS=5  # Počet úsekov textu, ktoré sa načítajú pri dopytoch do dokumentov


BACKEND_URL – URL adresa backendu.
OLLAMA_BASE_URL – URL adresa Ollama servera. host.docker.internal sa používa na prístup k hostiteľskému systému z Docker kontajnera.
OLLAMA_MODEL – Model, ktorý bude použitý (phi4-mini).
CHUNK_SIZE, CHUNK_OVERLAP, DISTANCE_THRESHOLD, N_RESULTS – Nastavenia ovplyvňujúce proces RAG (retrieval-augmented generation).
CHROMA_ – Nastavenia databázy ChromaDB.

Ak sa tam vyššie nastavenia nenachádzajú, doplňte ich.
Uložte súbor .env.

5. Spustenie projektu pomocou Docker Compose
Systém je možné jednoducho spustiť pomocou Docker Compose.

Otvorte Command Prompt alebo PowerShell.

Prejdite do adresára projektu (TC_DiplomaThesis), ak tam ešte nie ste.

Spustite Docker Compose:

	docker compose up --build

Tento príkaz zostaví Docker obrazy backendu a frontend aplikácie (ak neexistujú alebo boli zmenené).
Spustí kontajnery definované v súbore docker-compose.yml.
Počkajte, kým Docker Compose zostaví obrazy a spustí kontajnery. Výstup sa zobrazí v termináli.

6. Prístup k aplikácii
Po úspešnom spustení kontajnerov bude aplikácia dostupná cez webový prehliadač:

Backend služba: http://localhost:8000
Zobrazí sa FastAPI rozhranie.

Streamlit Frontend: http://localhost:8501
Toto je grafické užívateľské rozhranie, ktoré umožňuje zadávať otázky k dokumentom.
