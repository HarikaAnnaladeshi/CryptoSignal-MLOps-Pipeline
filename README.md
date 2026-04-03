MetaStackerBandit Trading-Signal Pipeline
This project is a robust MLOps batch processing pipeline designed to generate trading signals based on a rolling mean of asset closing prices. It was built as part of a technical assessment to demonstrate skills in data validation, containerization, and observability.

Features
Advanced CSV Parsing: Custom logic to handle quoted headers and malformed CSV structures (e.g., "timestamp,open,high...").

Reproducibility: Uses a YAML-based configuration with a fixed random seed (42) to ensure deterministic results across environments.

Containerization: Fully Dockerized using python:3.9-slim for "one-command" deployment readiness.

Observability: Generates structured metrics.json for automated monitoring and run.log for human-readable execution history.

Project Structure
run.py: The core engine containing data cleaning, rolling mean math, and signal generation.

config.yaml: Configuration file (seed=42, window=5, version="v1").

data.csv: The input dataset (10,000 rows of OHLCV data).

requirements.txt: Python dependencies (pandas, pyyaml, numpy).

Dockerfile: Instructions for building the isolated Docker environment.

README.md: Project documentation and execution guide.

Installation & Setup
1. Local Execution
To run the script directly on your machine (requires Python 3.9+):
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

2. Docker Execution (Recommended)
To run the pipeline in a fully isolated container:
# Build the Docker image
docker build -t mlops-task .

# Run the container (auto-removes after completion)
docker run --rm mlops-task

Sample Output (metrics.json)
Upon a successful run, the pipeline outputs the following structured JSON:
{
    "version": "v1",
    "status": "success",
    "seed": 42,
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.4991,
    "latency_ms": 108
}
Error Handling
The pipeline is equipped to handle:

Missing or malformed configuration files.

Missing 'close' columns in datasets.

Quoted or "squashed" CSV headers.

Empty input files.