import json
import os

import jsonschema
from jsonschema.exceptions import ValidationError


class SchemaValidatorError(Exception):
    """
    Base Exception for the schemavalidator module.
    """
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
    """
    Raise when an error occurs during validation of a schema.
    """

    def __init__(self, schema_file_name, *args, **kwargs):
        message = "An error occured while parsing '{}'"\
            .format(schema_file_name)
        super().__init__(message, *args, **kwargs)


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

    def __init__(self, schema_base_path='schemas/'):
        self.load_schemas(schema_base_path)

    def load_schemas(self, schema_base_path):
        self.schemas = {}

        for schema_file_name in self.get_schema_files(schema_base_path):
            full_path = os.path.join(schema_base_path, schema_file_name)
            try:
                with open(full_path) as schema_file:
                    schema = json.load(schema_file)
                    jsonschema.Draft4Validator.check_schema(schema)
                    self.schemas[schema['id']] = schema
            except Exception as e:
                raise SchemaError(schema_file_name) from e

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
