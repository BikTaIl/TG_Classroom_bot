from typing import Sequence, Mapping, Any, Union

from prettytable import PrettyTable

async def table_to_text(data: Union[Sequence[Mapping[str, Any]], Mapping[str, Any]]) -> str:
    table = await PrettyTable()
    if isinstance(data, Sequence):
        headers = list(data[0].keys())
        table.field_names = headers
        for row in data:
            data_row = []
            for header in headers:
                data_row.append(row.get(header, ""))
            table.add_row(data_row)
    else:
        headers = data.keys()
        table.field_names = headers
        data_row = []
        for header in headers:
            data_row.append(data.get(header, ""))
        table.add_row(data_row)
    return str(table)

