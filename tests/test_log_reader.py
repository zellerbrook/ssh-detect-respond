from log_reader import parse_line, AuthEvent


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
