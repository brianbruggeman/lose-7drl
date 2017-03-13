# -*- coding: utf-8 -*-
import copy
import os

import yaml


def normalize_name(name):
    # First add spaces for every capital letter
    new_name = []
    last_character = ''
    for character in name:
        if character.upper() == character:
            new_name.append(' ')
        elif character.isdigit():
            if not last_character.isdigit():
                new_name.append(' ')
            new_name.append(' ')
        new_name.append(character)
        last_character = character
    new_name = ''.join(new_name).strip().replace(' ', '_').lower()
    return new_name


class Schema(object):
    """A mechanism for defining a component

    Schemas are loosely built off of the Apache Avro format.
    See: https://avro.apache.org/docs/1.8.1/spec.html

    Args:
        name (str): A way for a human to identify the schema
        fields (dict): A json compatible schema


    Schemas are defined as follows:

    - name: schema-name
      doc: what this schema does
      fields:
          - name: field-name
            doc: documentation for field-name
            type: a well known python primitive type or list of types
            default: an optional default value
    """
    def _validate(self):
        # Check for top level schema
        required_fields = ['name', 'fields']
        for field in required_fields:
            if not hasattr(self, field):
                raise KeyError(f'ERROR: Key "{field}" not found in "{self}".')

        # Validate fields
        required_type_fields = ['name', 'type']
        for attribute in self.fields:
            for field_id, field in enumerate(required_type_fields):
                if field not in attribute:
                    name = attribute.get('name') or attribute
                    raise KeyError(f'ERROR: Key "{field}" not found in attribute "{name}" on "{self}"')
            for key, value in attribute.items():
                try:
                    exec(f'{key}')
                except SyntaxError:
                    raise KeyError(f'ERROR: "{key}" is an invalid key name.')
                except NameError:
                    pass

        # Refactor field data-type
        fields = copy.deepcopy(self.fields)
        self.fields = {}
        for attribute in fields:
            attribute_name = attribute['name']
            self.fields[attribute_name] = attribute

    def __init__(self, **fields):
        fields['name'] = normalize_name(fields['name'])
        for key, value in fields.items():
            setattr(self, key, value)
        self._validate()

    def __new__(cls, *args, **kwds):
        name = kwds.pop('name')
        cls_name = ''.join(
            name_fragment.capitalize() for name_fragment in name.split(' ')
        ) + 'Schema'
        cls_type = type(cls_name, (cls,), kwds)
        cls_instance = super(Schema, cls_type).__new__(cls_type)
        cls_instance.components = {}
        return cls_instance

    def __repr__(self):
        cname = self.__class__.__name__
        schema_fields = getattr(self, 'fields', [])
        fields = {}
        for field in schema_fields:
            field_name = field['name']
            field_type = field['type'].__name__
            default_value = field.get('default') or None
            fields[field_name] = (field_type, default_value)
        fields_string = []
        for key, value in fields.items():
            field_type, default_value = value
            if default_value is not None:
                fields_string.append(f'{field_type}: {key} = {default_value}')
            else:
                fields_string.append(f'{field_type}: {key}')
        fields_string = ' | '.join(fields_string)
        if fields_string:
            string = f'<{cname} [{fields_string}]>'
        else:
            string = f'<{cname}>'
        return string


def load_yaml_schema_file(filepath):
    """Loads a component schema yaml file

    Yields:
        Schema: a schema for each one found within the file
    """
    data = []
    if os.path.exists:
        with open(filepath, 'r') as yaml_stream:
            data = yaml.safe_load(yaml_stream.read())
    for schema in data:
        yield Schema(**data)


def load_yaml_schemas_from_tree(filepath):
    """Loads all data found within a folder tree

    Yeilds:
        Schema: a schema for each schema found within the tree
    """
    if os.path.isdir(filepath):
        for root, folders, files in os.walk(filepath):
            for filename in files:
                if not filename.endswith(('.yaml', '.yml')):
                    continue
                fullpath = os.path.join(root, filename)
                yield from load_yaml_schema_file(fullpath)
