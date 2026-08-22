import os
import time


def try_read_line(f, path):
    line = f.readline()
    if line:
        return line, f

    fd_stat = os.fstat(f.fileno())
    try:
        path_stat = os.stat(path)
    except FileNotFoundError:
        return None, f

    if fd_stat.st_ino != path_stat.st_ino:
        f.close()
        f = open(path)
    elif fd_stat.st_size < f.tell():
        f.seek(0, os.SEEK_SET)

    return None, f


def follow_log(path):
    f = open(path)
    try:
        f.seek(0, os.SEEK_END)
        while True:
            line, f = try_read_line(f, path)
            if line is None:
                time.sleep(1)
                continue
            yield line
    finally:
        f.close()


if __name__ == "__main__":
    from events import parse_line

    for line in follow_log("tests/fixtures/sample_auth.log"):
        print(parse_line(line))
