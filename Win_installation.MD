# Installation Manual for Study Material RAG Project on Windows - Updated

This guide provides step-by-step instructions for installing and running the Study Material RAG (Retrieval-Augmented Generation) project on a Windows computer. This project utilizes Ollama for local LLM capabilities, Docker for containerization, and Docker Compose for orchestrating the application. This update addresses the "MarkItDown returned None result" error.

## 1. Install Ollama and Pull the Required Model

Ollama allows you to run Large Language Models (LLMs) locally.

1. **Download Ollama:** Go to [https://ollama.ai/download/windows](https://ollama.ai/download/windows) and download the Windows installer.
2. **Install Ollama:** Run the downloaded installer and follow the on-screen instructions.
3. **Open Terminal:** Open a new Command Prompt or PowerShell window.
4. **Pull the Model:** Use the following command to download the `phi4:14b` model:
    ```sh
    ollama pull phi4:14b
    ```
    This command downloads the necessary model files. Wait for the download to complete.

## 2. Install Docker Desktop

Docker is a platform for running applications in containers.

1. **Download Docker Desktop:** Go to [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) and download Docker Desktop for Windows.
2. **Install Docker Desktop:** Run the installer. Ensure that you enable WSL 2 integration during installation if prompted. You might need to enable virtualization in your BIOS settings if it's not already enabled.
3. **Start Docker Desktop:** After installation, start Docker Desktop from the Windows Start menu. Docker might prompt you to log in or create an account.
4. **Verify Installation:** Open a new Command Prompt or PowerShell window and run:
    ```sh
    docker --version
    docker compose version
    ```
    This verifies that Docker and Docker Compose are installed correctly.

## 3. Clone the GitHub Repository

Clone the Study Material RAG project repository to your local machine.

1. **Open Command Prompt or PowerShell:** Navigate to the directory where you want to store the project.
2. **Clone the Repository:** Use the following command to clone the repository:
    ```sh
    git clone https://github.com/MichalCervenansky/Study-material-RAG
    ```
    This command downloads the project files to your local machine.
3. **Navigate to the Project Directory:**
    ```sh
    cd Study-material-RAG
    ```

## 4. Configure the .env File

Create and configure the `.env` file with the necessary environment variables.

1. **Create a `.env` file:** In the root directory of the project (i.e., `Study-material-RAG`), create a file named `.env`.
2. **Edit the `.env` file:** Open the `.env` file in a text editor and add the following content:
    ```env
    BACKEND_URL=http://localhost:8000
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    OLLAMA_MODEL=phi4:14b
    CHUNK_SIZE=1000
    CHUNK_OVERLAP=200
    CHROMA_ALLOW_RESET=true
    CHROMA_ANONYMIZED_TELEMETRY=false
    CHROMA_IS_PERSISTENT=true
    DISTANCE_THRESHOLD=1.5
    N_RESULTS=5  # Number of chunks to retrieve in document queries
    ```
    - **BACKEND_URL:** The URL for the backend service.
    - **OLLAMA_BASE_URL:** The base URL for the Ollama server. `host.docker.internal` is used to access the host machine from within a Docker container on Windows.
    - **OLLAMA_MODEL:** The name of the Ollama model to use (`phi4:14b` in this case).
    - **CHUNK_SIZE, CHUNK_OVERLAP, DISTANCE_THRESHOLD, N_RESULTS:** Parameters influencing the RAG pipeline.
    - **CHROMA_**: ChromaDB settings.

    Save the file.

## 5. Run the Project with Docker Compose

Use Docker Compose to build and start the application.

1. **Open Command Prompt or PowerShell:** Navigate to the project's root directory (`Study-material-RAG`) if you are not already there.
2. **Run Docker Compose:** Execute the following command:
    ```sh
    docker compose up --build
    ```
    This command performs the following actions:
    - **--build:** Builds the Docker images for the backend and frontend services if they don't exist or if there are changes in the Dockerfiles.
    - **up:** Starts the containers defined in the `docker-compose.yml` file.

    Wait for the command to complete. Docker Compose will build the images and start the containers. You can follow the progress in the terminal.

## 6. Access the Application

Once the Docker Compose command has finished and the containers are running, you can access the application in your web browser.

1. **Backend Service:** Open your web browser and go to `http://localhost:8000`. You should see the FastAPI default page.
2. **Streamlit Frontend:** Open your web browser and go to `http://localhost:8501`. This will open the Streamlit frontend, providing the user interface for querying the study material.
