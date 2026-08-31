def sum_or_none(*values: int | None) -> int | None:
    result: int = 0
    for value in values:
        if value is None:
            return None
        result += value
    return result
