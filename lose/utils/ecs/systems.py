# -*- coding: utf-8 -*-
import hashlib


class System(object):
    """Basic System class

    Controls when and how components are updated.  The `update` method
    should be modified.
    """

    def register_schema(self, schema):
        self.schemas.append(schema)

    def update(self):
        raise RuntimeError('Not implemented')

    def __call__(self):
        for schema in self.schemas:
            for component_name, component in schema.components:
                self.update(component)

    def __init__(self):
        self.id = hashlib.sha256()  # shouldn't ever be a collision
        self.component_types = []

    def __repr__(self):
        cname = self.__class__.__name__
        schemas = [schema.name for schema in self.schemas]
        string = f'<{cname}> {schemas}'
        return string
