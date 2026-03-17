---

# Country Detection Pipeline for Social Media Locations

## Overview

This project processes social media records stored in PostgreSQL and determines the **country of origin** from the `location` field. The detected country is stored as an **ISO3 country code**.

### Core Operations

1. **Country Detection**: Determines the country from the `location` field and stores it in `salert_basic.country`.
2. **Post Synchronization**: After each processed hour, the detected country is copied into `salert_post_temp.pais` for related posts.

The system processes records **starting from the most recent dates** and works in **hourly batches** to improve performance, consistency, and recovery in case of failure.

---

## Project Structure

```text
project/
├── bd_connection.py        # PostgreSQL connection
├── ia_connection.py        # AI inference for country detection
├── determinate_country.py  # Location cleaning and validation
├── assign_country.py       # Main pipeline script
├── salert_repository.py    # DB data access
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Orchestration
├── requirements.txt        # Dependencies
└── .env                    # Environment variables

```

---

## Pipeline Architecture

---

## Processing Strategy

The pipeline uses an incremental approach to ensure reliability:

* **Order**: Most recent dates first.
* **Batching**: Hourly processing batches.
* **Integrity**: Commit and Post-sync performed after each hour.

---

## Scripts

### 1. `assing_country.py`

The main pipeline script. It retrieves pending records, cleans the `location` field, determines the country using a multi-step strategy and synchronizes the detected country into the related posts table :

1. Location cleaning.
2. Location validation.
3. Direct detection via `pycountry`.
4. AI inference using **Groq LLM**.
5. Post synchronization

*If the country cannot be determined, it stores the value: `UNK`.*

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
DB_HOST=localhost
DB_NAME=database_name
DB_USER=username
DB_PASS=password
DB_PORT=5432
GROQCLOUD_API_KEY=your_api_key

```

### Installation

```bash
# Clone the repository
git clone <repo_url>
cd project

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

---

## Usage

### Running Locally

```bash
python assign_country.py

```

### Running with Docker

```bash
docker compose up --build

```

---

## Features

* **ISO3 country detection** & text cleaning.
* **AI fallback** for ambiguous locations.
* **In-memory cache** to minimize AI API costs.
* **Hourly batch processing** for better recovery.
* **PostgreSQL integration** with automatic post synchronization.

---

## Dependencies

* `psycopg2`
* `python-dotenv`
* `pycountry`
* `openai`

---

## Example Output

```text
Procesando fecha: 2025-07-17
Horas con registros: 2

Procesando hora: 2025-07-17 15:00:00
Registros encontrados: 3

Procesando: Madrid  -> ISO3: ESP
Procesando: Guayaquil -> ISO3: ECU

Commit realizado para la hora 2025-07-17 15:00:00
Sincronización completada

```

---