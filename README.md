# LogWhisperer

**LogWhisperer** is a self-hosted, AI-powered log summarizer for Linux systems. It uses local LLMs (via [Ollama](https://ollama.com)) like [Mistral](https://ollama.com/library/mistral) or [Phi](https://ollama.com/library/phi) to analyze system logs and generate concise summaries — entirely offline, with zero cloud dependency.

---

## Features

- Summarizes logs using a local LLM  
- Supports `journalctl`, raw log files, and Docker container logs  
- Automatically pulls missing models via Ollama  
- `--follow` mode: live log monitoring & auto-summarization  
- Saves human-readable summaries in Markdown format  
- Prompt customization via `config.yaml`  
- Works fully offline after initial model pull  
- One-line installer with virtualenv, dependency setup, and Ollama integration  
- Configurable model, host, and timeout — ideal for air-gapped or private deployments  

---

## Installation

```bash
git clone https://github.com/binary-knight/logwhisperer
cd logwhisperer
chmod +x install_logwhisperer.sh
./install_logwhisperer.sh
```

> This sets up a virtual environment, installs dependencies, sets up Ollama, and pulls your selected model (if not already installed).

---

## Usage Examples

### 🔹 Basic Run (uses `journalctl` and model from config)

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
# Available models from Ollama:
# - mistral
# - llama2
# - codellama
# - phi
# - gemma
# - tinyllama
# - dolphin-mixtral
# - or your own pulled/custom model
model: mistral
source: journalctl        # or "file", "docker"
log_file_path: /var/log/syslog  # only used if source == file
priority: err             # journalctl log level: emerg, alert, crit, err, warning, etc.
entries: 500              # number of log entries to fetch
timeout: 90               # number of seconds before LLM timeout
docker_container: my_container  # container name or ID
ollama_host: http://localhost:11434  # change if using remote Ollama
prompt: |
  You are a helpful Linux operations assistant. Analyze the following logs:
  - Identify root causes
  - Summarize key issues
  - Recommend next steps

  LOGS:
  {{LOGS}}
```

> The model defined here is used by default and will be pulled automatically if not found.

---

## Custom Prompts

Customize how logs are interpreted using the `prompt:` field in `config.yaml`.

Use `{{LOGS}}` as a placeholder for the actual log content injected at runtime.

---

## Flags and CLI Options

| Flag               | Description                                      |
|--------------------|--------------------------------------------------|
| `--source`         | `journalctl`, `file`, or `docker`               |
| `--logfile`        | Path to a file (if `source` is `file`)          |
| `--container`      | Docker container name or ID (if `source` is `docker`) |
| `--entries`        | Number of log entries to analyze                |
| `--model`          | Override model name (else uses `config.yaml`)   |
| `--ollama-host`    | Override Ollama API URL                         |
| `--timeout`        | Request timeout (in seconds)                    |
| `--follow`         | Enable continuous summarization mode            |
| `--interval`       | Seconds between summaries (used with `--follow`)|
| `--list-models`    | Show models currently installed in Ollama       |
| `--version`        | Show version number and exit                    |

---

## Output

Summaries are saved in the `reports/` directory with timestamped `.md` filenames:

```
reports/log_summary_2025-05-08_14-15-01.md
```

---

## Troubleshooting

- **Missing virtualenv or pip issues?**

```bash
sudo apt install python3-venv
rm -rf venv
./install_logwhisperer.sh
```

- **On WSL?**  
  `journalctl` won’t work — use `source: file` in your config or pass `--source file`.

- **Model not found?**  
  LogWhisperer now **auto-pulls missing models**. If that fails (e.g., offline), you can pull manually:

```bash
ollama pull phi
```

---

## Coming Soon

- Output format options: `json`, `txt`, `md`  
- Scheduled summaries via `cron` or `systemd`  
- Pattern matching and alert triggers  
- PyPI packaging (`pip install logwhisperer`)  
- Fully air-gapped installer with pre-bundled models  

---

## Support

If LogWhisperer saves you time or headaches, consider:

- [Sponsoring me on GitHub](https://github.com/sponsors/binary-knight) 🙏  
- Or [buy me a coffee](https://buymeacoffee.com/binaryknight) ☕

---

## Contributing

Pull requests, feedback, and bug reports are welcome.  
If you’re using LogWhisperer in production or have ideas, feel free to open an issue or submit a PR.
