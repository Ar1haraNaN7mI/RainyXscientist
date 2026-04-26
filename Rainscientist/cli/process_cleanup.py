"""Process cleanup helpers for CLI startup."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
from typing import Any

logger = logging.getLogger(__name__)


def release_old_rxsci_processes(config: Any) -> int:
    """Terminate stale RxSci CLI processes before this instance binds resources."""
    if not bool(getattr(config, "release_old_rxsci_on_start", True)):
        return 0
    if sys.platform.startswith("win"):
        return _release_old_rxsci_processes_windows()
    return _release_old_rxsci_processes_posix()


def _release_old_rxsci_processes_windows() -> int:
    script = r"""
$currentPid = [int]$args[0]
$current = Get-CimInstance Win32_Process -Filter "ProcessId = $currentPid"
$parentPid = if ($current) { [int]$current.ParentProcessId } else { 0 }
$targets = Get-CimInstance Win32_Process | Where-Object {
    $_.ProcessId -ne $currentPid -and
    $_.ProcessId -ne $parentPid -and
    (
        $_.Name -ieq 'rxsci.exe' -or
        $_.Name -ieq 'Rxscientist.exe' -or
        (
            ($_.Name -ieq 'python.exe' -or $_.Name -ieq 'pythonw.exe') -and
            ($_.CommandLine -match '(?i)(^|[\s\\/])(rxsci|Rxscientist|Rainscientist)(\.py)?($|[\s\\/])')
        )
    )
}
$count = 0
foreach ($target in $targets) {
    try {
        Stop-Process -Id $target.ProcessId -Force -ErrorAction Stop
        $count += 1
    } catch {}
}
Write-Output $count
"""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
                str(os.getpid()),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        logger.debug("Failed to release old RxSci processes: %s", exc)
        return 0
    if result.returncode != 0:
        logger.debug("RxSci process cleanup failed: %s", result.stderr.strip())
        return 0
    return _parse_cleanup_count(result.stdout)


def _release_old_rxsci_processes_posix() -> int:
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid=,ppid=,comm=,args="],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        logger.debug("Failed to list old RxSci processes: %s", exc)
        return 0
    if result.returncode != 0:
        return 0

    current_pid = os.getpid()
    parent_pid = os.getppid()
    killed = 0
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) < 3:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
        except ValueError:
            continue
        command = parts[2]
        args = parts[3] if len(parts) > 3 else ""
        if pid in (current_pid, parent_pid) or ppid == current_pid:
            continue
        if not _looks_like_rxsci_process(command, args):
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            killed += 1
        except OSError:
            continue
    return killed


def _looks_like_rxsci_process(command: str, args: str) -> bool:
    lower_command = command.lower()
    lower_args = args.lower()
    if lower_command in {"rxsci", "rxsci.exe", "rxscientist", "rxscientist.exe"}:
        return True
    if "python" not in lower_command:
        return False
    markers = (
        " rxsci ",
        "/rxsci",
        "\\rxsci",
        " rxscientist",
        "/rxscientist",
        "\\rxscientist",
        " rainscientist",
        "/rainscientist",
        "\\rainscientist",
    )
    padded_args = f" {lower_args} "
    return any(marker in padded_args for marker in markers)


def _parse_cleanup_count(raw: str) -> int:
    for line in reversed(raw.splitlines()):
        text = line.strip()
        if not text:
            continue
        try:
            return int(text)
        except ValueError:
            continue
    return 0
