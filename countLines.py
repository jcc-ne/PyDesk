#! /usr/bin/env python
# count lines of the file

def countLines(filename):
    f = open(filename)
    try:
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read # loop optimization
        buf = read_f(buf_size)

        # Empty file
        if not buf:
            return 0

        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)

        return lines
    finally:
        f.close()
