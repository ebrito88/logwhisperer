# LogWhisperer

LogWhisperer is a self-hosted, AI-powered log summarization tool for Linux servers.  
It uses local LLMs like [Mistral](https://ollama.com/library/mistral) or [Phi](https://ollama.com/library/phi) via [Ollama](https://ollama.com) to interpret and summarize system logs — no cloud APIs or tokens required.

---

## Features

- Parses logs from `journalctl` or raw files
- Summarizes using a local LLM (via Ollama)
- CLI with customizable flags
- Markdown report output for audits
- Offline-friendly & privacy-respecting
- Easy to install via a single script

---

## ⚙️ Installation

Clone the repo and run the install script:

```bash
git clone https://github.com/binary-knight/logwhisperer
cd logwhisperer
chmod +x install_logwhisperer.sh
./install_logwhisperer.sh --model mistral

