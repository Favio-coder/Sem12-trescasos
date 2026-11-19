#!/usr/bin/env python3
"""Inicia los servidores Django de caso1, caso2 y caso3 en puertos separados."""

import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
CASES = [
    ("caso1", 8001),
    ("caso2", 8002),
    ("caso3", 8003),
]


def python_for(case_dir: Path) -> str:
    """Usa el Python del entorno virtual del caso."""
    if sys.platform == "win32":
        executable = case_dir / ".venv" / "Scripts" / "python.exe"
    else:
        executable = case_dir / ".venv" / "bin" / "python"

    if not executable.is_file():
        raise FileNotFoundError(
            f"No se encontró el entorno virtual: {executable}\n"
            f"Crea el entorno con: python -m venv \"{case_dir / '.venv'}\""
        )
    return str(executable)


def port_is_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) != 0


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    deadline = time.monotonic() + 5
    for process in processes:
        if process.poll() is None:
            remaining = max(0, deadline - time.monotonic())
            try:
                process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                process.kill()


def main() -> int:
    cases = []
    for name, port in CASES:
        case_dir = ROOT / name
        if not (case_dir / "manage.py").is_file():
            print(f"Error: no se encontró {case_dir / 'manage.py'}", file=sys.stderr)
            return 1
        if not port_is_available(HOST, port):
            print(
                f"Error: el puerto {port} ya está ocupado "
                f"(caso: {name}). Cierra ese servidor o cambia el puerto.",
                file=sys.stderr,
            )
            return 1
        try:
            python = python_for(case_dir)
        except FileNotFoundError as error:
            print(error, file=sys.stderr)
            return 1
        cases.append((name, port, case_dir, python))

    processes = []
    try:
        for name, port, case_dir, python in cases:
            command = [
                python,
                "manage.py",
                "runserver",
                f"{HOST}:{port}",
                "--noreload",
            ]
            process = subprocess.Popen(command, cwd=case_dir)
            processes.append(process)
            print(f"{name}: http://{HOST}:{port}/")

        print("\nLos tres servidores están iniciando. Presiona Ctrl+C para detenerlos.")
        while True:
            for (name, port, _, _), process in zip(cases, processes):
                return_code = process.poll()
                if return_code is not None:
                    print(
                        f"\nEl servidor de {name} (puerto {port}) terminó "
                        f"con código {return_code}. Deteniendo los demás."
                    )
                    return return_code or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDeteniendo los servidores...")
    finally:
        stop_processes(processes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
