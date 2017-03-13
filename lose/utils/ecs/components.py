# -*- coding: utf-8 -*-
import hashlib


class Component(object):
    """Basic component

    """
    def __getattr__(self, name):
        schema = self.__dict__.get('schema')
        if schema:
            if name in schema.fields:
                return self.__dict__[name]
            else:
                raise AttributeError(f'ERROR: "{name}" is not a valid attribute for "{self}"')
        else:
            raise AttributeError(f'ERROR: "{name}" is not a valid attribute for "{self}"')

    def __getitem__(self, key):
        if key in self.schema.fields:
            return getattr(self, key)
        else:
            raise KeyError(f'ERROR: "{key}" is not a valid key name for "{self}"')

    def __init__(self, schema, **kwds):
        self.id = hashlib.sha256()  # shouldn't ever be a collision
        self.entity = None
        self.schema = schema
        schema.components[self.id] = self
        for field_name, field in schema.fields.items():
            default_value = field.get('default', None)
            setattr(self, field_name, default_value)

    def __repr__(self):
        cname = self.__class__.__name__
        entity = self.entity.name if self.entity else None
        name = self.schema.name
        if entity:
            string = f'<{cname} {name}:{entity}>'
        else:
            string = f'<{cname} {name}>'
        return string

    def __setattr__(self, name, value):
        schema = self.__dict__.get('schema')
        if schema:
            if name in schema.fields:
                field_type = schema.fields[name]['type']
                if not isinstance(value, field_type):
                    raise ValueError(f'ERROR: "{value}" is not of type "{field_type}" for attribute "{name}" on "{self}"')
                return object.__setattr__(self, name, value)
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def __setitem__(self, key, value):
        if key in self.schema.fields:
            field_type = self.schema.fields[key]['type']
            if type(value) not in [field_type, None]:
                # TODO: Handle field types that are unions
                raise ValueError('ERROR: Required type for "{key}" is "{field_type}"')
            return getattr(self, key)
        else:
            raise KeyError(f'ERROR: "{key}" is not a valid key name for "{self}"')
