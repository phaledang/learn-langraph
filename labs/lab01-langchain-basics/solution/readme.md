# Lab 01: LangChain Basics — Solution

## 🛠️ Environment Setup Guide

This guide walks you through resetting and setting up the Python virtual environment (`venv`) from the **project root folder**.

### Prerequisites

- Python 3.9 or higher installed
- Access to a terminal (PowerShell on Windows, or bash on macOS/Linux)

---

### 1. Navigate to the Project Root

```bash
cd c:\code\learn\learn-langraph
```

---

### 2. Reset the Virtual Environment

If the `venv` folder already exists and you want a clean reset, **delete it first**:

**Windows (PowerShell):**
```powershell
Remove-Item -Recurse -Force .\venv
```

**macOS / Linux:**
```bash
rm -rf venv
```

---

### 3. Create a New Virtual Environment

```bash
python -m venv venv
```

---

### 4. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

> ✅ You should see `(venv)` at the beginning of your terminal prompt when activated.

---

### 5. Install Dependencies from requirements.txt

With the `venv` activated, install the lab-specific packages from the project root:

```bash
pip install -r labs/lab01-langchain-basics/requirements.txt
```

This installs the core packages needed across all labs, including:
- `langchain`, `langchain-openai`, `langchain-core` — LangChain framework
- `langgraph` — LangGraph for stateful agents
- `python-dotenv` — Load `.env` files
- `pandas`, `pydantic` — Data processing
- And more (see [requirements.txt](../../../requirements.txt) for the full list)

---

### 6. Configure the `.env` File

Create a `.env` file in the **solution** folder (`labs/lab01-langchain-basics/solution/.env`) with your Azure OpenAI credentials:

```dotenv
USE_AZURE_OPENAI=1
AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-05-01-preview
```

> ⚠️ Do **not** include `/openai/v1` in the endpoint — the SDK adds the path automatically.

---

### 7. Run the Lab

From the **project root** (`c:\code\learn\learn-langraph`):

```bash
python labs/lab01-langchain-basics/solution/main.py
```

Or using the full `venv` path directly (without activating):

```powershell
C:/code/learn/learn-langraph/venv/Scripts/python.exe labs/lab01-langchain-basics/solution/main.py
```

---

### 🔄 Quick Reset — All-in-One Commands

**Windows (PowerShell):**
```powershell
cd c:\code\learn\learn-langraph
Remove-Item -Recurse -Force .\venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r labs/lab01-langchain-basics/requirements.txt
python labs/lab01-langchain-basics/solution/main.py
```

**macOS / Linux:**
```bash
cd /path/to/learn-langraph
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r labs/lab01-langchain-basics/requirements.txt
python labs/lab01-langchain-basics/solution/main.py
```

---

### 🔍 Verify the Environment

Check Python version and installed packages:

```bash
python --version
pip list | grep langchain
```

Expected output (versions may vary):
```
langchain          1.2.0
langchain-core     1.2.5
langchain-openai   1.1.6
```

---

### 💡 Tips

- Always **activate the venv** before running any lab script.
- The `requirements.txt` in the root folder covers dependencies for **all labs**.
- Some labs have their own `requirements.txt` for lab-specific packages — install those separately if needed.
- If you encounter `ModuleNotFoundError`, make sure your venv is activated and dependencies are installed.
