from copy import deepcopy
from sqlalchemy.orm import object_mapper, ColumnProperty, RelationshipProperty


class DeepCopyMixin(object):
    """
    Used in conjunction with `ShallowCopyMixin` to clone elixir.Entity
    instances.

    Any elixir.Entity can "mix-in" this class and be copy.deepcopy()'ed to
    produce a unique, duplicated row.

    Referenced relationships (e.g., ManyToOne, OneToMany, OneToOne) must also
    implement either `DeepCopyMixin` or `ShallowCopyMixin`.

    For example:

    ------------------------
    class Store(Entity, DeepCopyMixin):
        name        = Field(UnicodeText)
        products    = OneToMany('Product')

    class Product(Entity, DeepCopyMixin):
        name        = Field(UnicodeText)
        price       = Field(Float)
        categories  = OneToMany('GlobalCategory')

    class GlobalCategory(Entity, ShallowCopyMixin):
        category    = Field(UnicodeText)
    ------------------------

    `copy.deepcopy(Store.get(N))` would produce a new `Store` row and a new
    `Product` row, but the `GlobalCategory` would be shared between both
    products (i.e., not duplicated, just a shared reference).

    """

    def __deepcopy__(self, memo):
        # Instantiate a copy of the instance
        cls = self.__class__
        newobj = getattr(self, '__copy_target__', None) or cls()

        # Store the copied reference in the memo to avoid back-references...
        memo[self] = newobj

        # Look at each property of the object, based on the mapper definition
        for prop in object_mapper(self).iterate_properties:

            # If the property is the primary key, `id`, or is explicitly ignored, always skip it
            if prop.key == 'id' or prop.key in getattr(self, '__ignored_properties__', []):
                continue

            #
            # ColumnProperties are easy.  As long as the property isn't a
            # foreign key (e.g., ends in `_id`), just copy the values directly.
            #
            if isinstance(prop, ColumnProperty) and not prop.key.endswith('_id'):
                setattr(newobj, prop.key, getattr(self, prop.key))

            # If the property is a relationship...
            if isinstance(prop, RelationshipProperty):

                # Get the relationship value for the source object
                rel = getattr(self, prop.key)

                # If the value isn't None or [], continue...
                if rel:

                    # If the value is a list (ManyToOne)...
                    if isinstance(rel, list):

                        #
                        # Iterate over the list and generate copies of each
                        # entity in the list.
                        #
                        copies = []
                        for r in rel:
                            assert r not in memo  # avoid circular references
                            # Otherwise, copy it
                            copies.append(deepcopy(r, memo))

                        #
                        # Once we've built the new list of copies,
                        # we assign them to the destination (clone) instance.
                        #
                        setattr(newobj, prop.key, copies)
                    else:
                        #
                        # If the column doesn't represent a 1-N relationship,
                        # (e.g., it's just a static value), then make a copy
                        # of it.
                        #
                        if rel in memo:
                            setattr(newobj, prop.key, memo[rel])
                        else:
                            setattr(newobj, prop.key, deepcopy(rel, memo))

        return newobj


class ShallowCopyMixin(object):
    """
    A faux copy that just returns the source object.

    Used to "mix-in" to relationships that you don't want a unique copy of.
    """

    def __deepcopy__(self, memo):
        return self
