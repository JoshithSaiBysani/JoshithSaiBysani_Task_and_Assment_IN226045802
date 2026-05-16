# RAG-Based Customer Support Assistant

This project implements a Retrieval-Augmented Generation (RAG) customer support assistant that:

- ingests a PDF knowledge base
- chunks and embeds content locally
- stores vectors in ChromaDB
- retrieves relevant context for user queries
- routes queries through a LangGraph workflow
- supports Human-in-the-Loop (HITL) escalation when confidence is low or the request is complex

## Project Structure

- `src/rag_support/`: application code
- `data/knowledge_base/`: sample customer-support knowledge base
- `docs/`: source documentation
- `docs/pdf/`: generated HLD, LLD, and technical documentation PDFs
- `scripts/`: PDF generation helpers

## Quick Start

Use the bundled Python runtime for this project. The local `.deps` folder was installed for Python 3.12, so a system Python such as `C:\Python313\python.exe` will fail.

Recommended interpreter:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

1. Install dependencies:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r requirements.txt
```

2. Generate the sample knowledge-base PDF:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\build_sample_kb.py
```

3. Ingest the PDF:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe main.py ingest data\knowledge_base\customer_support_handbook.pdf
```

4. Ask a question:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe main.py ask "How long do refunds take?"
```

5. Start interactive chat with optional human review:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe main.py chat --auto-hitl
```

## Deliverables

Run the documentation generator to create the required PDFs:

```powershell
C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\build_docs.py
```

Generated files:

- `docs/pdf/HLD_RAG_Customer_Support_Assistant.pdf`
- `docs/pdf/LLD_RAG_Customer_Support_Assistant.pdf`
- `docs/pdf/Technical_Documentation_RAG_Customer_Support_Assistant.pdf`
