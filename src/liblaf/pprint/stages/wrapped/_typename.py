from collections import defaultdict

_BUILTIN_TYPENAMES: dict[type, str] = {dict: "", list: "", set: "", tuple: ""}


def disambiguate_typenames(types: set[type]) -> dict[type, str]:
    candidates: dict[type, list[str]] = {cls: _candidates(cls) for cls in types}
    rungs: dict[type, int] = dict.fromkeys(types, 0)
    while True:
        groups: dict[str, list[type]] = defaultdict(list)
        for cls, cls_candidates in candidates.items():
            rung: int = rungs[cls]
            candidate: str = cls_candidates[rung]
            groups[candidate].append(cls)
        updates: list[type] = []
        for group in groups.values():
            if len(group) <= 1:
                continue
            updates.extend(group)
        if not updates:
            break
        for cls in updates:
            rungs[cls] = min(rungs[cls] + 1, len(candidates[cls]) - 1)
    typenames: dict[type, str] = {cls: candidates[cls][rungs[cls]] for cls in types}
    typenames.update(_BUILTIN_TYPENAMES)
    return typenames


def _candidates(cls: type) -> list[str]:
    name: str = cls.__name__
    module: str = cls.__module__
    qualname: str = cls.__qualname__
    candidates: list[str] = [name, f"{module}.{name}", qualname, f"{module}.{qualname}"]
    return candidates
