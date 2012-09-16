from elixir import (Entity, OneToMany, Field, Unicode, Integer, Enum, Float)
from draughtcraft.model.deepcopy import ShallowCopyMixin


class InvalidStatistic(Exception):
    pass


class Style(Entity, ShallowCopyMixin):

    TYPES = [
        'LAGER',
        'ALE',
        'MEAD',
        'CIDER'
    ]

    uid = Field(Unicode(32), unique=True)
    name = Field(Unicode(256), index=True)
    url = Field(Unicode(256))

    # Gravities
    min_og = Field(Float)
    max_og = Field(Float)
    min_fg = Field(Float)
    max_fg = Field(Float)

    # IBU
    min_ibu = Field(Integer)
    max_ibu = Field(Integer)

    # SRM
    min_srm = Field(Integer)
    max_srm = Field(Integer)

    # ABV
    min_abv = Field(Float)
    max_abv = Field(Float)

    category = Field(Unicode(64))
    category_number = Field(Integer)
    style_letter = Field(Unicode(1))

    type = Field(Enum(*TYPES, native_enum=False))

    recipes = OneToMany('Recipe', inverse='style')

    def defined(self, statistic):
        if statistic not in (
            'og',
            'fg',
            'abv',
            'srm',
            'ibu'
        ):
            raise InvalidStatistic('Invalid statistic, %s' % statistic)

        minimum = getattr(self, 'min_%s' % statistic)
        maximum = getattr(self, 'max_%s' % statistic)

        return minimum is not None and maximum is not None

    def matches(self, recipe, statistic):
        if statistic not in (
            'og',
            'fg',
            'abv',
            'srm',
            'ibu'
        ):
            raise InvalidStatistic('Invalid statistic, %s' % statistic)

        minimum = getattr(self, 'min_%s' % statistic)
        maximum = getattr(self, 'max_%s' % statistic)

        if minimum is None or maximum is None:
            return False

        actual = getattr(recipe.calculations, statistic)

        if actual <= maximum and actual >= minimum:
            return True

        return False

    def to_xml(self):
        from draughtcraft.lib.beerxml import export
        kw = {
            'name': self.name,
            'category': self.category,
            'category_number': self.category_number,
            'style_letter': self.style_letter,
            'style_guide': 'BJCP',
            'type': self.type.capitalize(),
            'og_min': self.min_og,
            'og_max': self.max_og,
            'fg_min': self.min_fg,
            'fg_max': self.max_fg,
            'ibu_min': self.min_ibu,
            'ibu_max': self.max_ibu,
            'color_min': self.min_srm,
            'color_max': self.max_srm,
            'abv_min': self.min_abv,
            'abv_max': self.max_abv
        }
        return export.Style(**kw)
