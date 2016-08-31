import argparse
import sys
import os
from . import SchemaValidator

parser = argparse.ArgumentParser(description='Validate a schema')
parser.add_argument('schema')
parser.add_argument('--document', type=open, default=sys.stdin)
parser.add_argument('--base_path', default=os.getcwd(), type=os.path.abspath)


args = parser.parse_args()

document = args.document.read()


schema_validator = SchemaValidator(args.base_path)
schema_validator.validate_json_string(document, args.schema)
print('OK')