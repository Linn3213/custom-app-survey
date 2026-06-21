import pytest
from conftest import run

from coworklocal.tools import needs_confirmation


def test_write_creates_and_reads(tools):
    out, err = run(tools.execute("write_file", {"path": "notes/a.txt", "content": "hello"}))
    assert not err and "Created" in out
    out, err = run(tools.execute("read_file", {"path": "notes/a.txt"}))
    assert not err and out == "hello"


def test_edit_file(tools):
    run(tools.execute("write_file", {"path": "a.txt", "content": "hello world"}))
    out, err = run(tools.execute("edit_file", {"path": "a.txt", "old_string": "world", "new_string": "there"}))
    assert not err
    out, _ = run(tools.execute("read_file", {"path": "a.txt"}))
    assert out == "hello there"


def test_edit_ambiguous_match_is_rejected(tools):
    run(tools.execute("write_file", {"path": "a.txt", "content": "x x"}))
    out, err = run(tools.execute("edit_file", {"path": "a.txt", "old_string": "x", "new_string": "y"}))
    assert err and "matched 2 times" in out


def test_list_directory(tools):
    run(tools.execute("write_file", {"path": "d/a.txt", "content": "1"}))
    out, err = run(tools.execute("list_directory", {"path": "d"}))
    assert not err and "a.txt" in out


def test_confinement_rejects_paths_outside_root(tools):
    out, err = run(tools.execute("read_file", {"path": "/etc/passwd"}))
    assert err and "outside the allowed workspace" in out


def test_confinement_rejects_parent_traversal(tools):
    out, err = run(tools.execute("write_file", {"path": "../escape.txt", "content": "x"}))
    assert err and "outside the allowed workspace" in out


def test_run_shell_safe_command(tools):
    out, err = run(tools.execute("run_shell", {"command": "echo hi"}))
    assert not err and "hi" in out and "[exit code: 0]" in out


def test_run_shell_nonzero_exit_is_error(tools):
    out, err = run(tools.execute("run_shell", {"command": "false"}))
    assert err and "[exit code: 1]" in out


def test_run_shell_blocked_command(tools):
    out, err = run(tools.execute("run_shell", {"command": "rm -rf /"}))
    assert err and "blocked" in out.lower()


def test_run_shell_timeout(settings, tools):
    settings.shell_timeout = 1
    out, err = run(tools.execute("run_shell", {"command": "sleep 5"}))
    assert err and "timed out" in out


@pytest.mark.parametrize(
    "name, exists, expected",
    [
        ("read_file", False, False),
        ("list_directory", False, False),
        ("edit_file", True, True),
    ],
)
def test_needs_confirmation(tools, name, exists, expected):
    assert needs_confirmation(name, {"path": "x"}, tools.settings, tools.workspace) is expected


def test_write_confirmation_depends_on_existence(tools):
    ws = tools.workspace
    assert needs_confirmation("write_file", {"path": "new.txt"}, tools.settings, ws) is False
    run(tools.execute("write_file", {"path": "exists.txt", "content": "x"}))
    assert needs_confirmation("write_file", {"path": "exists.txt"}, tools.settings, ws) is True
