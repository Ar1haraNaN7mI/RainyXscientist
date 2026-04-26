from __future__ import annotations

from types import SimpleNamespace

from Rxscientist.cli import process_cleanup


def test_release_old_rxsci_processes_respects_config(monkeypatch):
    called = False

    def _fake_windows():
        nonlocal called
        called = True
        return 1

    monkeypatch.setattr(process_cleanup.sys, "platform", "win32")
    monkeypatch.setattr(
        process_cleanup,
        "_release_old_rxsci_processes_windows",
        _fake_windows,
    )

    count = process_cleanup.release_old_rxsci_processes(
        SimpleNamespace(release_old_rxsci_on_start=False)
    )

    assert count == 0
    assert called is False


def test_release_old_rxsci_processes_dispatches_by_platform(monkeypatch):
    monkeypatch.setattr(process_cleanup.sys, "platform", "win32")
    monkeypatch.setattr(
        process_cleanup,
        "_release_old_rxsci_processes_windows",
        lambda: 2,
    )

    count = process_cleanup.release_old_rxsci_processes(
        SimpleNamespace(release_old_rxsci_on_start=True)
    )

    assert count == 2


def test_looks_like_rxsci_process_matches_cli_entrypoints():
    assert process_cleanup._looks_like_rxsci_process("rxsci.exe", "") is True
    assert (
        process_cleanup._looks_like_rxsci_process(
            "python.exe",
            r"C:\repo\Rainscientist\cli\__init__.py serve",
        )
        is True
    )
    assert (
        process_cleanup._looks_like_rxsci_process("python.exe", "-m pytest tests")
        is False
    )


def test_parse_cleanup_count_uses_last_integer_line():
    assert process_cleanup._parse_cleanup_count("noise\n3\n") == 3
    assert process_cleanup._parse_cleanup_count("noise\n") == 0
