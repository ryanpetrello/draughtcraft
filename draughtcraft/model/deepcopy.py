from copy               import deepcopy
from sqlalchemy.orm     import object_mapper, ColumnProperty, RelationshipProperty


class ShallowCopyMixin(object):

    def __deepcopy__(self, memo):
        return self


class DeepCopyMixin(object):

    def __deepcopy__(self, memo):
        cls = self.__class__
        newobj = cls() 

        # Store the copied reference in the memo to avoid backreferences...
        memo[self] = newobj

        # Look at each property of the object, based on the mapper definition
        for prop in object_mapper(self).iterate_properties: 

            # If the property is the primary key, `id`, always skip it
            if prop.key == 'id': continue

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
                            #
                            # If we're already copied this item, just use
                            # the reference in the memo.
                            #
                            if r in memo:
                                copies.append(memo[r])
                            else:
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
