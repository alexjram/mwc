

def convert_time_to_int(time: str) -> int:
    seconds = 0
    time_parts = time.split(':')
    seconds = int(time_parts[0]) * 60 + int(time_parts[1])
    return seconds