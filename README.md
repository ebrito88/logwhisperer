# 🔍 LogWhisperer

**LogWhisperer** is a self-hosted, AI-powered log summarizer for Linux systems. It uses local LLMs (via [Ollama](https://ollama.com)) like [Mistral](https://ollama.com/library/mistral) or [Phi](https://ollama.com/library/phi) to analyze system logs and generate concise summaries — entirely offline, with zero cloud dependency.

---

## Features

- Summarizes logs using a local LLM  
- Supports `journalctl`, raw log files, and Docker container logs  
- `--follow` mode: live log monitoring & auto-summarization  
- Saves human-readable summaries in Markdown format  
- Prompt customization via `config.yaml`  
- Works fully offline (after initial install) — no API keys  
- One-line installer with automatic environment + model setup  
- Configurable Ollama host, timeout, and model  
- Ideal for air-gapped, self-hosted, or private environments  

---

## Installation

```bash
git clone https://github.com/binary-knight/logwhisperer
cd logwhisperer
chmod +x install_logwhisperer.sh
./install_logwhisperer.sh
```

> This sets up a virtual environment, installs dependencies, installs Ollama (if needed), and pulls your selected model.

---

## Usage Examples

### 🔹 Basic Run (default to journalctl)

```bash
python3 logwhisperer.py
```

### 🔹 Use a raw log file

```bash
python3 logwhisperer.py --source file --logfile /var/log/syslog
```

### 🔹 Use Docker container logs

```bash
python3 logwhisperer.py --source docker --container my_app_container
```

### 🔹 Continuous monitoring (`--follow` mode)

```bash
python3 logwhisperer.py --follow --interval 60
```

---

## Configuration (`config.yaml`)

LogWhisperer supports a fully configurable YAML file:

```yaml
source: journalctl            # or "file", "docker"
log_file_path: /var/log/syslog
priority: err                 # journalctl log level: emerg, alert, crit, err, warning, etc.
entries: 500
timeout: 90                   # request timeout (seconds)
ollama_host: http://localhost:11434
docker_container: my_container

prompt: |
  You are a helpful Linux operations assistant. Analyze the following logs:
  - Identify root causes
  - Summarize key issues
  - Recommend next steps

  LOGS:
  {{LOGS}}
```

---

## Custom Prompts

You can fully define how the model interprets your logs via the `prompt` field in `config.yaml`, using `{{LOGS}}` as a placeholder for the actual log content.

---

## Flags and CLI Options

| Flag               | Description                                      |
|--------------------|--------------------------------------------------|
| `--source`         | `journalctl`, `file`, or `docker`               |
| `--logfile`        | Path to a file if using `--source file`         |
| `--container`      | Docker container name if using `--source docker`|
| `--entries`        | Number of log entries to include                |
| `--model`          | Ollama model to use (default: `mistral`)        |
| `--ollama-host`    | Override Ollama server URL                      |
| `--timeout`        | Request timeout in seconds                      |
| `--follow`         | Enables continuous summarization mode           |
| `--interval`       | Interval between summaries (used with `--follow`)|
| `--version`        | Print version and exit                          |

---

## Output

Summaries are saved to the `reports/` directory as timestamped `.md` files:

```
reports/log_summary_2025-05-08_14-15-01.md
```

---

## Troubleshooting

- If you see `venv not found` errors, try:
  ```bash
  sudo apt install python3-venv
  rm -rf venv
  ./install_logwhisperer.sh
  ```

- If you're on **WSL**, `journalctl` likely won’t work — set your source to `"file"` in `config.yaml` or via CLI.

---

## 📦 Coming Soon (Planned Features)

- Output format options: `json`, `txt`, `md`
- Custom alert pattern matching
- PyPI release for `pip install logwhisperer`
- Scheduled summaries via cron or systemd
- Offline Mode, fully encapsulated offline installs

---

## 🤝 Contributing

Buy me a coffee if this is helpful! https://buymeacoffee.com/binaryknight

Pull requests, ideas, and feedback are welcome. If you're using LogWhisperer in production or want to contribute features, feel free to open an issue or fork the project.
