from datetime import datetime, timezone
from events import parse_line, AuthEvent, EventKind

UTC = timezone.utc

def test_failed_password_real_corpus_line():
    line = ("2026-08-02T00:00:06.926664+00:00 zachellerbrook-vps sshd[1678511]: "
            "Failed password for invalid user hasti from 92.118.39.62 port 56722 ssh2")
    assert parse_line(line) == AuthEvent(
        timestamp=datetime(2026, 8, 2, 0, 0, 6, 926664, tzinfo=UTC),
        kind=EventKind.FAILED_PASSWORD,
        source_ip="92.118.39.62",
        username="hasti",
        invalid_user=True,
        count=1,
    )

def test_sudo_line_is_ignored():
    line = "Nov 12 09:17:41 target-vm sudo:     zach : TTY=pts/0 ; PWD=/home/zach ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx"
    assert parse_line(line) is None

def test_valid_user_not_flagged_invalid():
    line = "2026-08-02T00:00:06+00:00 h sshd[1]: Failed password for root from 46.224.203.89 port 42346 ssh2"
    e = parse_line(line)
    assert e.username == "root" and e.invalid_user is False

def test_collapsed_repeat_carries_multiplier():
    line = ("2026-08-02T00:00:06+00:00 h sshd[1]: message repeated 4 times: "
            "[ Failed password for root from 1.2.3.4 port 22 ssh2]")
    e = parse_line(line)
    assert e.kind is EventKind.FAILED_PASSWORD and e.count == 4

def test_invalid_user_line_is_its_own_kind():
    line = "2026-08-02T00:00:06+00:00 h sshd[1]: Invalid user hasti from 92.118.39.62 port 56722"
    assert parse_line(line).kind is EventKind.INVALID_USER

def test_pam_noise_is_ignored():
    # this is the line that would cause 3.15x double-counting
    line = ("2026-08-02T00:00:06+00:00 h sshd[1]: pam_unix(sshd:auth): authentication "
            "failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=92.118.39.62")
    assert parse_line(line) is None
