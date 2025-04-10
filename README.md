# Study Material RAG Project

An advanced retrieval-augmented generation (RAG) pipeline designed for exploring study material using a backend service and a Streamlit frontend. It leverages local LLM capabilities via Ollama for efficient and interactive document retrieval and answer generation.

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Running the Project](#running-the-project)
- [Ollama Integration](#ollama-integration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview
This project implements a RAG pipeline that extracts and processes study materials, enabling users to retrieve information and get answers using local LLMs. It comprises two main components:

- A **Backend Service** built with FastAPI that handles document processing, vector storage, and interactions with local LLMs via Ollama.
- A **Streamlit Frontend** that provides a user-friendly interface for querying and exploring the study material.

## Project Structure
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

## Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Ollama](https://ollama.ai/) - a local LLM server
  - Install Ollama by following the instructions at [ollama.ai](https://ollama.ai).
  - Pull your preferred model (e.g., mistral, llama2, phi) using:
    ```bash
    ollama pull mistral
    ```
  - Ensure Ollama is running locally on port **11434**.

## Environment Setup
1. Create a `.env` file in the root directory with the following content:
    ```env
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=mistral  # or your preferred model
    ```
2. Adjust any other configurations as necessary for your local setup.

## Running the Project

We have simplified the process by using Docker Compose to orchestrate the multi-container application. Make sure Docker Compose is installed.

From the project root directory, run the following command:

```bash
docker compose up --build
```

This command will build and start both the backend service and the Streamlit frontend containers.

**Notes:**
- The backend service will be accessible at [http://localhost:8000](http://localhost:8000).
- The Streamlit frontend will be accessible at [http://localhost:8501](http://localhost:8501).
- For Linux Users, the backend service uses host network mode. For macOS and Windows, the Docker Compose configuration sets the environment variable OLLAMA_BASE_URL to use `host.docker.internal` so that the local Ollama server is accessible within the containers.

## Ollama Integration
This project integrates with Ollama to power local LLM responses. Key features include:
- Support for multiple open-source models (mistral, llama2, phi, etc.)
- Streaming responses for interactive and real-time querying
- Easy model switching via the `.env` file

Ensure that Ollama is running and accessible before starting the backend service.

## Troubleshooting
- **Docker Networking on macOS/Windows:** If you experience connectivity issues due to `--network host`, use the `host.docker.internal` approach as shown above.
- **Ollama Connection Issues:** Verify that the Ollama server is running by visiting [http://localhost:11434](http://localhost:11434). Adjust the `OLLAMA_BASE_URL` in your `.env` file if necessary.
- **Permission Issues:** Make sure Docker has the required permissions, and that your firewall settings are not blocking the necessary ports.

## Contributing
Contributions are welcome! Please fork the repository, make your improvements, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the [MIT License](LICENSE).