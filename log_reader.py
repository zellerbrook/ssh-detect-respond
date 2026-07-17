import re
from dataclasses import dataclass

@dataclass
class AuthEvent:
    timestamp: str
    source_ip: str
    username: str
    outcome: str

def parse_line(line):
    if "Failed password" not in line and "Accepted password" not in line:
        return None
    source_ip = re.search(r"from (\S+)", line).group(1)
    outcome = re.search(r"(\w+) password", line).group(1)
    username = re.search(r"for (.+) from", line).group(1)
    timestamp = re.search(r"^(\S+ \S+ \S+)", line).group(1)

    return AuthEvent(
        timestamp=timestamp,
        source_ip=source_ip,
        username=username,
        outcome=outcome,
    )

if __name__ == "__main__":
    with open("tests/fixtures/sample_auth.log") as f:
        for line in f:
            print(parse_line(line))
