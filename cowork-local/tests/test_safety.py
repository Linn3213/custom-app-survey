import pytest

from coworklocal.safety import classify_command, describe_risk


@pytest.mark.parametrize(
    "command, expected",
    [
        ("ls -la", "safe"),
        ("cat foo.txt", "safe"),
        ("git status", "safe"),
        ("git log --oneline", "safe"),
        ("pwd", "safe"),
        ("grep -r needle .", "safe"),
        ("git push", "confirm"),
        ("git commit -m x", "confirm"),
        ("rm file.txt", "confirm"),
        ("echo hi > out.txt", "confirm"),
        ("cat a | sh", "confirm"),
        ('python -c "import os"', "confirm"),
        ("npm install", "confirm"),
        ("", "confirm"),
        ("rm -rf /", "block"),
        ("rm -rf ~", "block"),
        (":(){ :|:& };:", "block"),
        ("shutdown now", "block"),
        ("mkfs.ext4 /dev/sda", "block"),
        ("dd if=/dev/zero of=/dev/sda", "block"),
    ],
)
def test_classify_command(command, expected):
    assert classify_command(command) == expected


def test_describe_risk():
    assert "echo hi" in describe_risk("run_shell", {"command": "echo hi"})
    assert "a.txt" in describe_risk("write_file", {"path": "a.txt"})
    assert "b.txt" in describe_risk("edit_file", {"path": "b.txt"})
