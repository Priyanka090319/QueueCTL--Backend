import time
from storage import execute_query
from job_manager import run_job

def worker_loop():
    """Continuously fetch and process jobs"""
    while True:
        # pick one pending job
        job = execute_query("SELECT * FROM jobs WHERE state='pending' LIMIT 1", fetch=True)
        if not job:
            time.sleep(2)
            continue
        job_id, command, state, attempts, max_retries, *_ = job[0]
        execute_query("UPDATE jobs SET state='processing' WHERE id=?", (job_id,))
        run_job((job_id, command, state, attempts, max_retries))