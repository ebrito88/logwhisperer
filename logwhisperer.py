import yaml
import subprocess
import json
import os
import time
import sys
import argparse
import requests
from datetime import datetime
from spinner import Spinner

__version__ = "1.0.0"

def save_summary_to_markdown(summary, messages):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = f"reports/log_summary_{timestamp}.md"

    with open(filepath, "w") as f:
        f.write(f"# Log Summary Report — {timestamp}\n\n")
        f.write("## 🔍 Summary\n\n")
        f.write(summary + "\n\n")
        f.write("## 📜 Raw Log Messages (last 100)\n\n")
        for msg in messages[-100:]:
            f.write(f"- {msg}\n")

    print(f"\nSummary saved to `{filepath}`")

def build_prompt(messages, config):
    joined_logs = "\n".join(messages[-50:])
    raw_template = config.get("prompt", None)
    if raw_template:
        return raw_template.replace("{{LOGS}}", joined_logs)

    # Default prompt
    return (
        "You are a helpful Linux operations assistant. Summarize the following system log entries, "
        "identify likely causes of errors, and recommend next steps if possible.\n\n" + joined_logs
    )

def run_follow_loop(config, args, source, entries, priority, logfile, model, ollama_host, timeout):
    print(f"Starting follow mode — summarizing every {args.interval}s\n")
    while True:
        if source == "journalctl":
            logs = read_from_journalctl(priority, entries)
        elif source == "file":
            logs = read_from_file(logfile, entries)
        elif source == "docker":
            container = args.container or config.get("docker_container")
            if not container:
                print("Docker container name must be provided via --container or config.yaml")
                return
            logs = read_from_docker_logs(container, entries)
        else:
            print("Invalid source.")
            return

        messages = filter_messages(logs)
        if messages:
            prompt = build_prompt(messages, config)
            summary = try_generate_with_retry(prompt, model=model, host=ollama_host, timeout=timeout)
            save_summary_to_markdown(summary, messages)

        time.sleep(args.interval)

def summarize_logs_with_ollama(prompt, model="mistral", host="http://localhost:11434", timeout=60):
    try:
        response = requests.post(
            f"{host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as e:
        print("Error communicating with local LLM:", e)
        return "[Error: Could not generate summary.]"

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def read_from_journalctl(priority, entries):
    cmd = ["journalctl", "-p", priority, "-n", str(entries), "--output", "json"]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        logs = [json.loads(line) for line in lines if line.strip()]
        return logs
    except subprocess.CalledProcessError as e:
        print("Error reading from journalctl:", e.stderr)
        return []

def read_from_file(path, entries):
    if not os.path.exists(path):
        print(f"Log file {path} does not exist.")
        return []
    with open(path, "r") as f:
        lines = f.readlines()[-entries:]
    return [{"__REALTIME_TIMESTAMP": str(datetime.now()), "MESSAGE": line.strip()} for line in lines]

def filter_messages(logs):
    return [entry["MESSAGE"] for entry in logs if "MESSAGE" in entry]

def try_generate_with_retry(prompt, model, host, timeout):
    # First attempt
    try:
        return summarize_logs_with_ollama(prompt, model=model, host=host, timeout=timeout)
    except requests.exceptions.ReadTimeout:
        print("First request timed out — triggering model warm-up...")
        
        dummy_prompt = prompt[:200] 
        try:
            _ = summarize_logs_with_ollama(dummy_prompt, model=model, host=host, timeout=timeout)
            print("Model warm-up complete. Retrying full prompt...")
        except Exception as e:
            print("Warm-up failed:", e)

        time.sleep(2)
        return summarize_logs_with_ollama(prompt, model=model, host=host, timeout=timeout)

def force_model_load(host, model):
    try:
        print(f"Ensuring model '{model}' is loaded...")
        response = requests.post(
            f"{host}/api/show",
            json={"name": model},
            timeout=10
        )
        if response.ok:
            print("Model is ready.\n")
        else:
            print(f"Model info check failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to contact Ollama API: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="LogWhisperer - AI-powered log summarizer")
    parser.add_argument("--source", choices=["journalctl", "file", "docker"], help="Log source")
    parser.add_argument("--logfile", help="Path to log file (if source is 'file')")
    parser.add_argument("--entries", type=int, help="Number of log entries to analyze")
    parser.add_argument("--priority", help="Journalctl priority (e.g., err, warning)")
    parser.add_argument("--model", default="mistral", help="LLM model name for summarization (default: mistral)")
    parser.add_argument("--version", action="store_true", help="Show the current version of LogWhisperer")
    parser.add_argument("--container", help="Docker container name (if source is 'docker')")
    parser.add_argument("--ollama-host", help="Override Ollama server address (default: from config.yaml or localhost)")
    parser.add_argument("--timeout", type=int, help="Request timeout in seconds (overrides config.yaml)")
    parser.add_argument("--follow", action="store_true", help="Continuously summarize logs at intervals")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds between summaries (used with --follow)")
    return parser.parse_args()

def read_from_docker_logs(container, entries=500):
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(entries), container],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        return [{"MESSAGE": line} for line in lines]
    except subprocess.CalledProcessError as e:
        print("Error reading Docker logs:", e.stderr)
        return []


def main():
    config = load_config()
    args = parse_args()
    timeout = args.timeout or config.get("timeout", 60)
    source = args.source or config.get("source", "journalctl")
    entries = args.entries or config.get("entries", 500)
    priority = args.priority or config.get("priority", "err")
    logfile = args.logfile or config.get("log_file_path", "/var/log/syslog")
    model = args.model or "mistral"
    ollama_host = args.ollama_host or config.get("ollama_host", "http://localhost:11434")

    print("Configuration:")
    print(f"Source: {source}")
    print(f"Entries: {entries}")
    if source == "journalctl":
        print(f"Priority: {priority}")
    elif source == "file":
        print(f"Log file: {logfile}")
    elif source == "docker":
        print(f"Docker container: {args.container or config.get('docker_container')}")
    print(f"Ollama host: {ollama_host}")
    print(f"Timeout: {timeout}s\n")

    if args.version:
        print(f"Logwhisperer version {__version__}")
        sys.exit(0)

    if source == "journalctl":
        logs = read_from_journalctl(priority, entries)
    elif source == "file":
        path = args.logfile or config.get("log_file_path", "/var/log/syslog")
        logs = read_from_file(path, entries)
    elif source == "docker":
        container = args.container or config.get("docker_container")
        if not container:
            print("Docker container name must be provided via --container or config.yaml")
            sys.exit(1)
        logs = read_from_docker_logs(container, entries)

    else:
        print("Invalid source: must be 'journalctl' or 'file'")
        sys.exit(1)

    messages = filter_messages(logs)

    if not messages:
        if not args.follow:
            print("No log messages found.")
            sys.exit(0)
    elif not args.follow:
        print(f"\n{len(messages)} log entries retrieved.\n")

    if args.follow:
        run_follow_loop(config, args, source, entries, priority, logfile, model, ollama_host, timeout)
        return

    prompt = build_prompt(messages, config)
    print(f"Prompt length: {len(prompt)} characters")
    force_model_load(ollama_host, model)
    spinner = Spinner("Summarizing log entries")
    spinner.start()
    try:
        summary = try_generate_with_retry(prompt, model=model, host=ollama_host, timeout=timeout)
    finally:
        spinner.stop()

    print("Done!\n")
    print("Summary:\n")
    print(summary)
    save_summary_to_markdown(summary, messages)



if __name__ == "__main__":
    main()

