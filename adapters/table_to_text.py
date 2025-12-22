from typing import Sequence, Mapping, Any, Union

async def table_to_text(data: Union[Sequence[Mapping[str, Any]], Mapping[str, Any]]) -> str:
    if not data:
        raise ValueError("Пустые данные")
    if isinstance(data, Mapping):
        data = [data]
    headers = list(data[0].keys())
    max_key_len = max(len(str(key)) for key in headers)
    lines = []
    for i, row in enumerate(data):
        for key in headers:
            value = str(row.get(key, ""))
            lines.append(f"{str(key).ljust(max_key_len)} : {value}")
        if i < len(data) - 1:
            lines.append("-" * (max_key_len + 20))
    return f"<pre>{'\n'.join(lines)}</pre>"
