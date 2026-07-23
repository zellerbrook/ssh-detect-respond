import re
import os
from time import sleep
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

def follow_log(path):
    f = open(path)
    try:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                fd_stat = os.fstat(f.fileno())
                try:
                    path_stat = os.stat(path)
                except FileNotFoundError:
                    sleep(1)
                    continue
                if fd_stat.st_ino != path_stat.st_ino:
                    f.close()
                    f = open(path)
                elif fd_stat.st_size < f.tell():
                    f.seek(0, os.SEEK_SET)
                sleep(1)
                continue
            yield line
    finally:
        f.close()


if __name__ == "__main__":
    for line in follow_log("tests/fixtures/sample_auth.log"):
        print(parse_line(line))
