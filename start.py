"""
METROLOGYC - Unified Startup Script
Starts both the backend (FastAPI/Uvicorn) and frontend (Vite) dev servers
with a single command.

Usage:
    python start.py
"""
import subprocess
import sys
import os
import signal
import time

# Resolve project paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# Detect the Python executable — prefer the project venv if it exists
VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe")
PYTHON_EXE = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

# npm is typically on PATH; use npm.cmd on Windows
NPM_CMD = "npm.cmd" if os.name == "nt" else "npm"
VITE_BIN = os.path.join(
    FRONTEND_DIR,
    "node_modules",
    ".bin",
    "vite.cmd" if os.name == "nt" else "vite",
)


def ensure_frontend_dependencies():
    """Install frontend dependencies when this is a fresh clone."""
    if os.path.exists(VITE_BIN):
        return

    install_command = [NPM_CMD, "ci"]
    if not os.path.exists(os.path.join(FRONTEND_DIR, "package-lock.json")):
        install_command = [NPM_CMD, "install"]

    print("[Frontend] Dependencies not found; installing them now...")
    try:
        result = subprocess.run(install_command, cwd=FRONTEND_DIR)
    except FileNotFoundError:
        print("[ERROR] npm was not found. Install Node.js and npm, then run python start.py again.")
        raise SystemExit(1)

    if result.returncode != 0:
        print("[ERROR] Frontend dependency installation failed.")
        raise SystemExit(result.returncode)


def main():
    processes = []

    print("=" * 60)
    print("  METROLOGYC - Starting All Services")
    print("=" * 60)
    print()

    ensure_frontend_dependencies()

    # ── 1. Start Backend (FastAPI + Uvicorn on port 8080) ────────
    print("[Backend]  Starting FastAPI server on http://localhost:8080 ...")
    backend_proc = subprocess.Popen(
        [PYTHON_EXE, "main.py"],
        cwd=BACKEND_DIR,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(("Backend", backend_proc))

    # Wait for /api/health to return 200 before launching frontend
    print("[Backend]  Waiting for http://127.0.0.1:8080/api/health to respond...")
    backend_ready = False
    max_retries = 30
    import urllib.request
    import urllib.error

    for attempt in range(max_retries):
        # Check if backend process died early
        retcode = backend_proc.poll()
        if retcode is not None:
            print(f"\n[ERROR] Backend process exited prematurely with code {retcode} during startup.")
            print("[ERROR] Check your Python environment, database permissions, or .env file.")
            raise SystemExit(retcode)

        try:
            with urllib.request.urlopen("http://127.0.0.1:8080/api/health", timeout=1.5) as resp:
                if resp.status == 200:
                    backend_ready = True
                    print("[Backend]  Health check passed (HTTP 200 OK).")
                    break
        except Exception:
            time.sleep(0.5)

    if not backend_ready:
        print("\n[WARNING] Backend health check timed out after 15 seconds. Proceeding with caution...")

    # ── 2. Start Frontend (Vite dev server on port 3000) ─────────
    print("[Frontend] Starting Vite dev server on http://localhost:3000 ...")
    frontend_proc = subprocess.Popen(
        [NPM_CMD, "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append(("Frontend", frontend_proc))

    print()
    print("=" * 60)
    print("  [OK] Backend  -> http://localhost:8080")
    print("  [OK] Frontend -> http://localhost:3000")
    print("  Press Ctrl+C to stop all services")
    print("=" * 60)
    print()

    # ── Wait for either process to exit ──────────────────────────
    try:
        while True:
            for name, proc in processes:
                retcode = proc.poll()
                if retcode is not None:
                    print(f"\n[{name}] exited with code {retcode}")
                    raise SystemExit(retcode)
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\n\nShutting down all services...")
        for name, proc in processes:
            if proc.poll() is None:
                print(f"  Stopping {name} (PID {proc.pid})...")
                if os.name == "nt":
                    # On Windows, terminate the process tree
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print("  All services stopped.")


if __name__ == "__main__":
    main()
