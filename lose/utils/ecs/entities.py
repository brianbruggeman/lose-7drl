# -*- coding: utf-8 -*-
import hashlib

from components import Component


from collections import namedtuple


class Entity(object):
    """Basic entity

    Args:
        name (str): A way for a human to identify the entity if needed
        schemas (list):  Register several schemas at instantiation
    """
    def register(self, schema):
        schema_name = schema.name
        component = Component(schema)
        components = self.__dict__.get('components', {})
        if not components:
            self.components = components
        self.components[schema_name] = component

    def remove_component(self, name):
        return self.components.pop(name)

    def __dir__(self):
        data = object.__dir__(self)
        data.extend(self.components.keys())
        data = [d for d in data if d not in ['components']]
        return data

    def __getattr__(self, name):
        components = self.__dict__.get('components', {})
        if components:
            component = components.get(name)
            if component:
                component_name = component.schema.name
                component_fields = [field_name for field_name in component.schema.fields]
                if len(component_fields) > 1:
                    component_data_class = namedtuple(component_name, component_fields)
                    component_data = [getattr(component, field) for field in component_fields]
                    data = component_data_class(*component_data)
                elif len(component_fields) == 1:
                    data = getattr(component, component_fields[0])
                return data
            else:
                raise AttributeError(f'ERROR: "{name}" is not a valid attribute.')
        else:
            return self.__dict__[name]

    def __init__(self, name=None, *schemas):
        self.id = hashlib.sha256()  # shouldn't ever be a collision
        self.components = {}
        for schema in schemas:
            self.register(schema)

        # Not all entities need names, but it would be nice to know
        # what the entities are if possible.
        self.name = name or 'Unnamed-{}'.format(self.id)

    def __repr__(self):
        cname = self.__class__.__name__
        name = self.__dict__.get('name')
        data = []
        for component_name, component_data in self.components.items():
            component_data = getattr(self, component_name)
            if isinstance(component_data, tuple):
                data.append(f'{component_data}')
            else:
                data.append(f'{component_name}={component_data}')
        data = ' | '.join(data)
        if name:
            string = f'<{cname} {name} [{data}]>'
        else:
            string = f'<{cname} [{data}]>'
        return string

    def __setattr__(self, name, value):
        components = self.__dict__.get('components', {})
        if components:
            component = components.get(name)
            if component:
                component_name = component.schema.name
                component_fields = [field_name for field_name in component.schema.fields]
                if len(component_fields) > 1:
                    if len(value) != len(component_fields):
                        raise ValueError(f'ERROR: "{value}" cannot be set for "{name}" on "{self}"')
                    component_data_class = namedtuple(component_name, component_fields)
                    component_data = [getattr(component, field) for field in component_fields]
                    data = component_data_class(*component_data)
                elif len(component_fields) == 1:
                    data = setattr(component, component_fields[0], value)
                return data
            else:
                self.__dict__[name] = value
        else:
            self.__dict__[name] = value
