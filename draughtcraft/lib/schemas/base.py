from formencode                 import Schema, Invalid, NoDefault, validators

class FilteredSchema(Schema):

    if_missing = None
    allow_extra_fields = True
    filter_extra_fields = True

class ModelObject(validators.FancyValidator):
    """
    Checks if a key is valid for the given model.
    """
    
    __unpackargs__ = ('model', 'attr', 'filters')
    
    attr = 'id'
    filters = {}

    def __initargs__(self, new_attrs):
        if self.if_empty and not isinstance(self.if_empty, self.model):
            self._if_empty = self.if_empty
            self.if_empty = NoDefault
        validators.FancyValidator.__initargs__(self, new_attrs)

    def _to_python(self, value, state):
        criteria = {self.attr : value}
        for key, value in self.filters.iteritems():
            if callable(value):
                value = value()
            criteria[key] = value
        instance = self.model.get_by(**criteria)
        if not instance:
            raise Invalid(self.message('empty', state), value, state)
        else:
            return instance
    
    def _from_python(self, value, state):
        if value:
            return getattr(value, self.attr)
    
    def empty_value(self, value):
        if self._if_empty:
            if isinstance(self._if_empty, tuple):
                instance = self.model.get_by(**{self._if_empty[0] : self._if_empty[1]})
            else:
                instance = self.model.get_by(**{self.attr : self._if_empty})
            return instance
        else:
            return None

