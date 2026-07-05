#!/usr/bin/env python3

def get_host_memory():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()

    mem_info = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0].rstrip(':')
            val = int(parts[1]) # Value in kB
            mem_info[key] = val

    total = mem_info.get('MemTotal', 0)
    free = mem_info.get('MemFree', 0)
    buffers = mem_info.get('Buffers', 0)
    cached = mem_info.get('Cached', 0)

    # Calculate truly used memory (Total - Free - Buffers - Cached)
    used = total - (free + buffers + cached)

    # Convert to Megabytes
    total_mb = round(total / 1024, 1)
    used_mb = round(used / 1024, 1)
    percent = round((used / total) * 100, 1)

    print(f"Used: {used_mb}MB / {total_mb}MB ({percent}%)")

if __name__ == "__main__":
    get_host_memory()
