import json

# Hack to be compatible with json in python < 3.5
try:
    from json import JSONDecodeError
except:
    # json in python < 3.5 has no JSONDecodeError
    JSONDecodeError = ValueError

import os

import jsonschema
from jsonschema.exceptions import ValidationError
import requests


class SchemaValidatorError(Exception):
    """Base Exception for the schemavalidator module."""
    pass


class SchemaValidationError(SchemaValidatorError):
    """
    Raised during validate if the given object is not valid for the given
    schema.
    """

    def __init__(self, message):
        message = message.split('\n')[0]
        super().__init__(message)


class SchemaError(SchemaValidatorError):
    """Raise when an error occurs during validation of a schema."""

    def __init__(self, original_e, schema_file_name, *args, **kwargs):
        message = "An error occured while parsing '{}'.\n"\
                  "Original exception: {}"\
                  .format(schema_file_name, str(original_e))
        super().__init__(message, *args, **kwargs)


class SchemaOpenError(SchemaError):
    """Raise when a schema can not be opened."""


class SchemaJSONError(SchemaError):
    """Raise when a schema contains invalid JSON."""


class SchemaValidError(SchemaError):
    """Raise when a schema contains an invalid schema."""


class SchemaStrictnessError(SchemaError):
    """Raise when a schema doesn't pass the strictness test."""


class SchemaKeyError(SchemaError):
    """Raise when a schema doesn't contain an id-key."""


class UnkownSchemaError(SchemaValidatorError):
    pass


class SchemaValidator(object):
    """
    Reads in all the JSON schemas in the given folder and validates them.
    A SchemaValidator instance can be used to validate documents against
    one of the schemas. Internal references are automatically
    resolved.
    """
    schemas = None

    def __init__(self, schema_base_path='schemas/',
                 strictness_schema='http://json-schema.org/draft-04/schema'):
        self._load_strictness_schema(strictness_schema)

        self.load_schemas(schema_base_path)

    def _load_strictness_schema(self, schema_uri):
        r = requests.get(schema_uri)
        strictness_schema = r.json()

        self.strictness_validator = jsonschema.Draft4Validator(
            strictness_schema)

    def load_schemas(self, schema_base_path):
        self.schemas = {}

        for schema_file_name in self.get_schema_files(schema_base_path):
            full_path = os.path.join(schema_base_path, schema_file_name)
            try:
                with open(full_path) as schema_file:
                    schema = json.load(schema_file)
                    jsonschema.Draft4Validator.check_schema(schema)
                    self.strictness_validator.validate(schema)
                    self.schemas[schema['id']] = schema
            except OSError as e:
                raise SchemaOpenError(e, schema_file_name) from e
            except JSONDecodeError as e:
                raise SchemaJSONError(e, schema_file_name) from e
            except jsonschema.exceptions.SchemaError as e:
                raise SchemaValidError(e, schema_file_name) from e
            except jsonschema.exceptions.ValidationError as e:
                raise SchemaStrictnessError(e, schema_file_name) from e
            except KeyError as e:
                raise SchemaKeyError(e, schema_file_name) from e

    def get_schema(self, schema_id):
        try:
            return self.schemas[schema_id]
        except KeyError:
            raise UnkownSchemaError(
                "No schema found with id '{}'".format(schema_id))

    def validate(self, document, schema_id):
        schema = self.get_schema(schema_id)

        try:
            resolver = Resolver(self, schema)
            validator = jsonschema.Draft4Validator(schema, resolver=resolver)
        except Exception as e:
            raise SchemaValidatorError from e

        try:
            validator.validate(document, schema)
        except ValidationError as e:
            raise SchemaValidationError(e.message) from e

    def get_schema_files(self, schema_base_path):
        return [file_name for file_name in os.listdir(schema_base_path)
                if os.path.splitext(file_name)[1] == '.json']


class Resolver(jsonschema.RefResolver):
    schema_validator = None

    def __init__(self, schema_validator, schema):
        self.schema_validator = schema_validator
        super().__init__('', schema)

    def resolve_from_url(self, url):
        return self.schema_validator.get_schema(url)
