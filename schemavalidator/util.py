import logging
import copy

from jsonschema.exceptions import by_relevance

import schemavalidator

logger = logging.getLogger(schemavalidator.__name__)

def log_error_table(validator, document, schema):
    errors = collect_errors(validator, document, schema)
    if len(errors)>0:
        logger.error(errors[0])
    table = errors_to_table(errors)
    if len(table) > 0:
        logger.debug(format_table(table, ['schema path', 'instance path', 'message']))
    else:
        logger.debug("No additional info available.")


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
    field_scores = {
        'type': 3
    }
    validator_scores = {
        'enum': 2
    }
    validator_scores_nonprop = {
        'anyOf': 1
    }
    todo = list(validator.iter_errors(document, schema))
    errors = []
    while todo:
        error = todo.pop()
        errors.append(error)
        todo.extend(error.context)
    scores = {}
    for error in errors:
        score = 0       # propagating score, affects neighbors.
        error.score = 0 # nonpropagating score
        if len(error.absolute_path) > 0 and len(error.absolute_schema_path) > 0:
            if error.absolute_path[-1] in field_scores:
                score += field_scores[error.absolute_path[-1]]
            if error.absolute_schema_path[-1] in validator_scores:
                score += validator_scores[error.absolute_schema_path[-1]]
            if error.absolute_schema_path[-1] in validator_scores_nonprop:
                error.score += validator_scores_nonprop[error.absolute_schema_path[-1]]

        schema_path = copy.copy(error.absolute_schema_path)
        while schema_path:
            path_string = format_path(schema_path)
            if path_string not in scores:
                scores[path_string] = 0
            scores[path_string] += score
            schema_path.pop()

    for error in errors:
        path_todo = copy.copy(error.absolute_schema_path)
        path = []
        while len(path_todo):
            path.append(path_todo.popleft())
            path_string = format_path(path)
            if path_string in scores:
                error.score += scores[path_string]

    errors.sort(key=lambda e: e.score)
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
