import pandas as pd
import numpy as np
import yaml
import json
import argparse
import time
import logging
import sys
import os

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def write_metrics(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    # Print to stdout as required by the Docker instruction
    print(json.dumps(data, indent=4))

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--log-file', required=True)
    args = parser.parse_args()

    setup_logging(args.log_file)
    logging.info("Job started")

    metrics = {"version": "unknown", "status": "error"}

    try:
        # 1. Load + Validate Config
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file {args.config} not found")
        
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        
        metrics["version"] = config.get('version', "v1")
        metrics["seed"] = config.get('seed', 42)
        
        np.random.seed(metrics["seed"])
        logging.info(f"Config loaded: seed={metrics['seed']}, window={config.get('window', 5)}")

        # 2. Load + Validate Dataset
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file {args.input} not found")
            
        # Initial read
        df = pd.read_csv(args.input)
        
        # FIX: If headers are trapped in a single string due to quotes
        if len(df.columns) == 1:
            col_raw = df.columns[0].replace('"', '').replace("'", "")
            new_columns = [c.strip().lower() for c in col_raw.split(',')]
            
            # Manually split the data rows
            df = df.iloc[:, 0].str.split(',', expand=True)
            df.columns = new_columns
            
            # Ensure 'close' is numeric
            if 'close' in df.columns:
                df['close'] = pd.to_numeric(df['close'], errors='coerce')

        # Standard cleaning for any remaining quotes/spaces
        df.columns = [c.strip().replace('"', '').lower() for c in df.columns]

        if df.empty:
            raise ValueError("Input CSV is empty")
        
        if 'close' not in df.columns:
            raise ValueError(f"Missing 'close' column. Found: {list(df.columns)}")
        
        logging.info(f"Rows loaded: {len(df)}")

        # 3. Processing: Rolling Mean
        window = config.get('window', 5)
        df['rolling_mean'] = df['close'].rolling(window=window).mean()

        # 4. Processing: Signal Generation
        # Logic: 1 if close > rolling_mean, else 0. Ignore NaNs from initial window.
        df['signal'] = np.where(df['rolling_mean'].isna(), np.nan, 
                                (df['close'] > df['rolling_mean']).astype(int))
        
        # 5. Final Metrics
        valid_signals = df['signal'].dropna()
        end_time = time.time()

        metrics.update({
            "status": "success",
            "rows_processed": len(df),
            "metric": "signal_rate",
            "value": float(round(valid_signals.mean(), 4)) if not valid_signals.empty else 0.0,
            "latency_ms": int((end_time - start_time) * 1000)
        })
        
        logging.info("Job end - Status: success")
        write_metrics(args.output, metrics)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        metrics["status"] = "error"
        metrics["error_message"] = str(e)
        write_metrics(args.output, metrics)
        sys.exit(1)

if __name__ == "__main__":
    main()