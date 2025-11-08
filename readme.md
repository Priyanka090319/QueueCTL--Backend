#  QueueCTL – A Minimal Job Queue System (Python + SQLite)

A lightweight **CLI-based job queue system** built using Python.  
QueueCTL allows you to enqueue shell commands as background jobs, process them using worker threads, retry failed tasks automatically, and manage a **Dead Letter Queue (DLQ)** — all with persistent storage in SQLite.

---

##  Features

-  **Job Enqueue & Management** – Add shell commands to a persistent job queue  
-  **Worker Threads** – Process queued jobs concurrently  
-  **Retry Logic** – Automatic retry with exponential backoff  
-  **Dead Letter Queue (DLQ)** – Failed jobs are safely stored for later review  
-  **Configurable Settings** – Adjust retries, backoff, and system behavior easily  
-  **SQLite Storage** – Keeps all job and DLQ records persistent across runs  
-  **Click-based CLI** – Intuitive command-line interface for all operations  

---

## Tech Stack

| Component | Description |
|------------|-------------|
| **Language** | Python 3.10 |
| **Database** | SQLite3 |
| **CLI Framework** | Click |
| **Concurrency** | Threading |
| **Error Handling** | Retry + DLQ mechanism |

---

##  Project Structure

queuectl/
│
├── main.py             # CLI entry point for managing jobs and workers
├── job_manager.py      # Job enqueue, update, and DLQ logic
├── worker.py           # Worker thread loop and job execution logic
├── storage.py          # SQLite database connection and helper functions
├── config.py           # Config management (max retries, backoff base, etc.)        
├── queue.db            # Auto-generated SQLite database for job storage
├── requirements.txt    # Python dependencies (Click library)
└── README.md           # Project documentation
