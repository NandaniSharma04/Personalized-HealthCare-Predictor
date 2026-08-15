def chunk_list(xs: list, n: int):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]
