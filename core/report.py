"""Small markdown helpers."""


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_fmt(x) for x in r) + " |")
    return "\n".join(out)


def _fmt(x):
    if isinstance(x, bool):
        return "yes" if x else "**NO**"
    if isinstance(x, float):
        return str(int(x)) if x == int(x) and abs(x) < 1e6 else f"{x:.3f}"
    if x is None:
        return "-"
    return str(x)


def fmt_path(path):
    return " -> ".join(path)
