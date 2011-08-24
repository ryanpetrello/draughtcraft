from draughtcraft.model.deepcopy    import DeepCopyMixin
from elixir                         import Entity, Field, Unicode, ManyToOne

import re

class RecipeSlug(Entity, DeepCopyMixin):

    slug            = Field(Unicode(256))

    recipe          = ManyToOne('Recipe', inverse='slugs')

    def __init__(self, *args, **kwargs):
        super(RecipeSlug, self).__init__(*args, **kwargs)

        if kwargs.get('name') and kwargs.get('slug') is None:
            name = kwargs['name']

            # The name must be at least one character to generate a slug
            assert name
        
            # Lowercase and strip punctuation
            stripped = re.sub('[^a-z0-9\s-]', '', name.lower())

            # Split on spaces
            parts = stripped.split(' ')

            # Filter out empty spaces
            parts = filter(None, parts)

            # Join together with dashes
            slug = '-'.join(parts)
    
            # If a valid slug can't be built, just fallback to `custom-recipe`
            if not slug:
                slug = 'custom-recipe'

            self.slug = slug
