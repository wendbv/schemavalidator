# SchemaValidator

A local JSON schema validator based on [jsonschema](https://github.com/Julian/jsonschema/)

SchemaValidator can be used to validate documents against a set of locally
stored schema's. Currently only python 3 is supported.


## Installation

```bash
$ pip install schemavalidator
```


## Usage

To validate a document against `my_schema.json` located in `schemas/`:

```python
from schemavalidator import SchemaValidator, SchemaValidationError

validator = SchemaValidator('schemas/')

document = {'my': 'document'}

try:
    validator.validate(document, 'my_schema.json')
except SchemaValidationError:
    # This document does not validate.
```

## Multiple schema's example

The main purpose of this is to handle multiple schema's linking to
each other. Let's say we have two schema's: `list.json`, which defines a list,
and `item.json`, which defines the items in the list. Both are stored in the
`schemas/` folder.

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "list.json",
    "description": "Just a list of items",
    "type": "array",
    "items": {
        "$ref": "item.json"
    }
}
```

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "item.json",
    "description": "Just an item",
    "type": "object"
    "properties": {
        "name": {
            "type": "string"
        }
    }
}

Using `SchemaValidator` we can easily check a document against `list.json`
without having to do any manual referencing.

```python
from schemavalidator import SchemaValidator, SchemaValidationError

validator = SchemaValidator('schemas/')

document = [{"name": "My Name"}]

try:
    validator.validate(document, 'list.json')
except SchemaValidationError:
    pass
```

Refences are followed by `id` and not by filename. When the `id` field is
omitted, the filename is used as a fallback.