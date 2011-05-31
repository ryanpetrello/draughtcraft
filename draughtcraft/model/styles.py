from elixir import Entity, OneToMany, Field, Unicode, Integer, Float


class InvalidStatistic(Exception):
    pass


class Style(Entity):

    name            = Field(Unicode(256))

    # Gravities
    min_og          = Field(Float)
    max_og          = Field(Float)
    min_fg          = Field(Float)
    max_fg          = Field(Float)

    # IBU
    min_ibu         = Field(Integer)
    max_ibu         = Field(Integer)

    # SRM
    min_srm         = Field(Integer)
    max_srm         = Field(Integer)

    # ABV
    min_abv         = Field(Float)
    max_abv         = Field(Float)

    recipes         = OneToMany('Recipe', inverse='style')

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

        if maximum >= actual and actual >= minimum:
            return True

        return False
