import click
import threading
from job_manager import enqueue_job
from worker import worker_loop
from storage import init_db, execute_query
from config import load_config, save_config

@click.group()
def cli():
    """QueueCTL - Minimal Job Queue System"""
    init_db()

@cli.command()
@click.option("--command", required=True, help="Shell command to execute")
@click.option("--id", default=None, help="Optional job ID")
def enqueue(command, id):
    """Add a new job to the queue"""
    import uuid
    cfg = load_config()
    job_id = id or str(uuid.uuid4())
    enqueue_job(command, cfg["max_retries"])
    click.echo(f" Job enqueued: {job_id}")

@cli.group()
def worker():
    """Worker management commands"""
    pass

@worker.command("start")
@click.option("--count", default=1, help="Number of workers to start")
def start_workers(count):
    for i in range(count):
        t = threading.Thread(target=worker_loop, daemon=True)
        t.start()
    click.echo(f" Started {count} workers. Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        click.echo(" Gracefully stopping workers...")

@worker.command("stop")
def stop_workers():
    click.echo("Workers stopped manually.")

@cli.command()
def status():
    """Show queue status"""
    jobs = execute_query("SELECT state, COUNT(*) FROM jobs GROUP BY state", fetch=True)
    click.echo("Job Status:")
    if not jobs:
        click.echo("No jobs found.")
    for s, c in jobs:
        click.echo(f"{s}: {c}")

@cli.command()
@click.option("--state", default="pending")
def list(state):
    """List jobs by state"""
    jobs = execute_query("SELECT id, command, attempts FROM jobs WHERE state=?", (state,), fetch=True)
    if not jobs:
        click.echo(f"No jobs found in state: {state}")
        return
    for j in jobs:
        click.echo(f" {j}")

# Dead Letter Queue commands
@cli.group()
def dlq():
    """Dead Letter Queue operations"""
    pass

@dlq.command("list")
def list_dlq():
    jobs = execute_query("SELECT * FROM dlq", fetch=True)
    if not jobs:
        click.echo("No jobs in DLQ.")
        return
    for j in jobs:
        click.echo(f" {j}")

@dlq.command("retry")
@click.argument("job_id")
def retry_dlq(job_id):
    job = execute_query("SELECT * FROM dlq WHERE id=?", (job_id,), fetch=True)
    if not job:
        click.echo("No such job in DLQ.")
        return
    _, command, _, _ = job[0]
    enqueue_job(command, load_config()["max_retries"])
    execute_query("DELETE FROM dlq WHERE id=?", (job_id,))
    click.echo(f" Retried job {job_id} from DLQ.")

# Configuration commands
@cli.group()
def config():
    """Configuration management"""
    pass

@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    cfg = load_config()
    if key in cfg:
        cfg[key] = int(value)
        save_config(cfg)
        click.echo(f" Config updated: {key}={value}")
    else:
        click.echo("Invalid config key")

if __name__ == "__main__":

    cli()
