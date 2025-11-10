import uuid
import time
import subprocess
from storage import execute_query
from config import load_config

def enqueue_job(command, max_retries):
    """Add a job to the queue"""
    job_id = str(uuid.uuid4())
    execute_query(
        "INSERT INTO jobs (id, command, state, attempts, max_retries, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
        (job_id, command, "pending", 0, max_retries),
    )
    print(f" Job enqueued: {job_id}")
    return job_id


def run_job(job):
    """Execute the job command"""
    job_id, command, state, attempts, max_retries = job
    try:
        print(f"⚙️ Running job: {job_id} → {command}")
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            execute_query("UPDATE jobs SET state='completed', updated_at=datetime('now') WHERE id=?", (job_id,))
            print(f" Job {job_id} completed successfully")
        else:
            handle_failure(job)
    except Exception as e:
        print(f" Job {job_id} failed: {e}")
        handle_failure(job)


def handle_failure(job):
    """Handle job retries and move to DLQ if exhausted"""
    job_id, command, state, attempts, max_retries = job
    new_attempts = attempts + 1
    cfg = load_config()
    delay = cfg["backoff_base"] ** new_attempts
    if new_attempts <= max_retries:
        print(f" Job {job_id} failed. Retrying in {delay}s (attempt {new_attempts}/{max_retries})")
        time.sleep(delay)
        execute_query(
            "UPDATE jobs SET attempts=?, state='pending', updated_at=datetime('now') WHERE id=?",
            (new_attempts, job_id),
        )
    else:
        print(f" Job {job_id} moved to DLQ after {max_retries} attempts")
        execute_query("DELETE FROM jobs WHERE id=?", (job_id,))
        execute_query(
            "INSERT INTO dlq (id, command, failed_at) VALUES (?, ?, datetime('now'))",
            (job_id, command),

        )
