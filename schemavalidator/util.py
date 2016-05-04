def format_error_table(validator, document, schema):
    errors = collect_errors(validator, document, schema)
    table = errors_to_table(errors)
    if len(table) > 0:
        return format_table(table, ['schema path', 'instance path', 'message'])
    else:
        return "No additional info available."


def errors_to_table(errors):
    table = []
    for error in errors:
        path = format_path(error.absolute_path)
        schema_path = format_path(error.absolute_schema_path, "schema")

        table.append([schema_path, path, error.message])
    return table


def format_path(path, prefix="$"):
    if len(path) == 0:
        return prefix
    return "{}[{}]".format(prefix, ']['.join((repr(x) for x in path)))


def collect_errors(validator, document, schema):
    todo = list(validator.iter_errors(document, schema))
    errors = []
    while todo:
        error = todo.pop()
        errors.append(error)
        todo.extend(error.context)
    errors.sort(key=lambda e: e.absolute_schema_path)
    return errors


def format_table(table, headings):
    outlines = ['']
    widths = [len(max(list(col) + [headings[i]],
              key=lambda v: len(v)))
              for i, col in enumerate(zip(*table))]

    outlines.append('╔═' + '═╤═'.join(['═' * w for w in widths]) + '═╗')
    outlines.append('║ ' + ' │ '.join([
        h.center(widths[i]) for i, h in enumerate(headings)
        ]) + ' ║')
    outlines.append('╠═' + '═╪═'.join(['═' * w for w in widths]) + '═╣')
    for row in table:
        row_padded = []
        for i, column in enumerate(row):
            row_padded.append(column.ljust(widths[i]))
        outlines.append('║ ' + ' │ '.join(row_padded) + ' ║')
    outlines.append('╚═' + '═╧═'.join(['═' * w for w in widths]) + '═╝')
    return '\n'.join(outlines)
