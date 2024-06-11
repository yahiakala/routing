def trim_path(path):
    start = 0
    end = len(path)
    while start < end and path[start] == "/":
        start += 1
    while end > start and path[end-1] == "/":
        end -= 1
    return path[start:end]
