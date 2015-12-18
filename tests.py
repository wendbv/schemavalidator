import jsonschema
import pytest

from schemavalidator import SchemaValidator, SchemaError, UnkownSchemaError,\
    SchemaValidatorError, SchemaValidationError
from schemavalidator.schemavalidator import Resolver


def raise_exception(*args, **kwargs):
    raise Exception()


@pytest.fixture
def schema_validator(monkeypatch):
    monkeypatch.setattr(SchemaValidator, 'load_schemas', lambda self, p: None)
    return SchemaValidator()


def test_load_schemas_non_existing_schema_file(schema_validator, monkeypatch,
                                               tmpdir):
    monkeypatch.undo()
    monkeypatch.setattr(
        schema_validator, 'get_schema_files',
        lambda *args: ['non_existend.json'])
    with pytest.raises(SchemaError):
        schema_validator.load_schemas(str(tmpdir))


def test_load_schemas_invalid_json(schema_validator, monkeypatch, tmpdir):
    monkeypatch.undo()
    schema_file = tmpdir.join('test.json')
    schema_file.write('{')
    monkeypatch.setattr(
        schema_validator, 'get_schema_files', lambda *args: ['test.json'])
    with pytest.raises(SchemaError):
        schema_validator.load_schemas(str(tmpdir))


def test_load_schemas_no_schema_id(schema_validator, monkeypatch, tmpdir):
    monkeypatch.undo()
    schema_file = tmpdir.join('test.json')
    schema_file.write('{"$schema":"no_id", "type":"string"}')
    monkeypatch.setattr(
        schema_validator, 'get_schema_files', lambda *args: ['test.json'])
    with pytest.raises(SchemaError):
        schema_validator.load_schemas(str(tmpdir))


def test_load_schemas_invalid_schema(schema_validator, monkeypatch, tmpdir):
    monkeypatch.undo()
    schema_file = tmpdir.join('test.json')
    schema_file.write('{"$schema":"invalid","type"="objects"}')
    monkeypatch.setattr(
        schema_validator, 'get_schema_files', lambda *args: ['test.json'])
    with pytest.raises(SchemaError):
        schema_validator.load_schemas(str(tmpdir))


def test_load_schemas_stores_valid_schema(schema_validator, monkeypatch,
                                          tmpdir):
    monkeypatch.undo()
    schema_file = tmpdir.join('test.json')
    schema_file.write('{"$schema":"valid","id":"test.json","type":"string"}')
    monkeypatch.setattr(
        schema_validator, 'get_schema_files', lambda *args: ['test.json'])
    schema_validator.load_schemas(str(tmpdir))
    assert schema_validator.schemas['test.json']['id'] == 'test.json'


def test_get_schema(schema_validator, monkeypatch):
    monkeypatch.setattr(schema_validator, 'schemas', {'test_schema': 'test'})

    assert schema_validator.get_schema('test_schema') == 'test'


def test_get_schema_non_existend(schema_validator, monkeypatch):
    monkeypatch.setattr(schema_validator, 'schemas', {})
    with pytest.raises(UnkownSchemaError):
        schema_validator.get_schema('does not exist')


def test_validate_resolver_exception(monkeypatch, schema_validator):
    monkeypatch.setattr(schema_validator, 'get_schema', lambda a: {})
    monkeypatch.setattr(Resolver, '__init__', raise_exception)

    with pytest.raises(SchemaValidatorError):
        schema_validator.validate({}, 'test.json')


def test_validate_validator_exception(monkeypatch, schema_validator):
    monkeypatch.setattr(schema_validator, 'schemas', {})
    monkeypatch.setattr(Resolver, '__init__', lambda *args: None)
    monkeypatch.setattr(
        jsonschema.Draft4Validator, '__init__', raise_exception)

    with pytest.raises(SchemaValidatorError):
        schema_validator.validate({}, 'test.json')


def test_validate_validate(monkeypatch, schema_validator):
    monkeypatch.setattr(schema_validator, 'get_schema', lambda a: {})
    monkeypatch.setattr(Resolver, '__init__', lambda *args: None)
    monkeypatch.setattr(
        jsonschema.Draft4Validator, '__init__', lambda *args, **kwargs: None)

    monkeypatch.setattr(
        jsonschema.Draft4Validator, 'validate', lambda *args: None)
    schema_validator.validate({}, 'test.json')


def test_validate_validate_exception(monkeypatch, schema_validator):
    monkeypatch.setattr(schema_validator, 'get_schema', lambda a: {})
    monkeypatch.setattr(Resolver, '__init__', lambda *args: None)
    monkeypatch.setattr(
        jsonschema.Draft4Validator, '__init__', lambda *args, **kwargs: None)

    monkeypatch.setattr(
        jsonschema.Draft4Validator, 'validate', lambda *args: raise_exception)
    schema_validator.validate({}, 'test.json')


def test_get_schema_files(schema_validator, tmpdir):
    tmpdir.join('test.json').write('')
    tmpdir.join('test.jpg').write('')
    tmpdir.mkdir('test')
    files = schema_validator.get_schema_files(str(tmpdir))

    assert files == ['test.json']


def test_resolver_init(schema_validator):
    resolver = Resolver(schema_validator, {})
    assert resolver.schema_validator == schema_validator


def test_resolver_from_url(schema_validator, monkeypatch):
    monkeypatch.setattr(
        schema_validator, 'get_schema', lambda url: '{}-schema'.format(url))
    resolver = Resolver(schema_validator, {})
    assert resolver.resolve_from_url('url') == 'url-schema'


def test_validation_error():
    try:
        raise SchemaValidationError('First row\nsecond row')
    except SchemaValidationError as e:
        assert str(e) == 'First row'
