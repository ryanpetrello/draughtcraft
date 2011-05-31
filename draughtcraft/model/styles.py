from elixir import Entity, OneToMany, Field, Unicode, Integer, Float

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
