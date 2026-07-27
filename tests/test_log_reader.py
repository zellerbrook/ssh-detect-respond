import time
from log_reader import parse_line, AuthEvent, follow_log, try_read_line


def test_sudo_line_is_ignored():
    line = "Nov 12 09:17:41 target-vm sudo:     zach : TTY=pts/0 ; PWD=/home/zach ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx"
    assert parse_line(line) is None

def test_failed_password_line_parses():
    line = "Nov 12 09:15:22 target-vm sshd[2145]: Failed password for invalid user admin from 192.168.56.101 port 52344 ssh2"
    assert parse_line(line) == AuthEvent(
        timestamp="Nov 12 09:15:22",
        source_ip="192.168.56.101",
        username="invalid user admin",
        outcome="Failed",
    )

def test_try_read_line_returns_line_when_available(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("line one\n")
    f = open(log_file)

    line, returned_f = try_read_line(f, str(log_file))

    assert line == "line one\n"
    assert returned_f is f


def test_try_read_line_returns_none_when_no_line_available(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("")
    f = open(log_file)

    line, returned_f = try_read_line(f, str(log_file))

    assert line is None
    assert returned_f is f

def test_try_read_line_detects_rotation(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("old line\n")
    f = open(log_file)

    # consume the old content so the handle sits at EOF
    line, f = try_read_line(f, str(log_file))
    assert line == "old line\n"

    # rotate: move the old file aside, create a fresh one at the same path
    log_file.rename(tmp_path / "auth.log.1")
    log_file.write_text("new line\n")

    # first call after rotation: detects mismatch, reopens, returns no line
    line, new_f = try_read_line(f, str(log_file))
    assert line is None
    assert new_f is not f

    # second call: reads from the reopened handle
    line, f2 = try_read_line(new_f, str(log_file))
    assert line == "new line\n"

    f2.close()

def test_try_read_line_detects_truncation(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("old line one\n")
    f = open(log_file)

    # consume the old content so the handle sits at EOF
    line, f = try_read_line(f, str(log_file))
    assert line == "old line one\n"
    assert f.tell() == 13

    # copytruncate: same inode, contents wiped in place
    log_file.write_text("")

    # first call after truncation: detects it, seeks to 0, returns no line
    line, returned_f = try_read_line(f, str(log_file))
    assert line is None
    assert returned_f is f
    assert f.tell() == 0

    # writer appends to the now-empty file
    with open(log_file, "a") as writer:
        writer.write("new line\n")

    line, f2 = try_read_line(f, str(log_file))
    assert line == "new line\n"

    f2.close()

def test_try_read_line_survives_missing_file(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text("old line\n")
    f = open(log_file)

    line, f = try_read_line(f, str(log_file))
    assert line == "old line\n"

    # the gap: old file moved aside, replacement not created yet
    log_file.unlink()

    line, returned_f = try_read_line(f, str(log_file))
    assert line is None
    assert returned_f is f

    # replacement appears; the next call takes the rotation branch
    log_file.write_text("new line\n")
    line, new_f = try_read_line(f, str(log_file))
    assert line is None
    assert new_f is not f

    line, f2 = try_read_line(new_f, str(log_file))
    assert line == "new line\n"

    f2.close()
