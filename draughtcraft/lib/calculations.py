class Calculations(object):

    def __init__(self, recipe):
        self.recipe = recipe

    @property
    def original_gravity(self):
        """
        Original gravity of the recipe.
        """

        points = 0
        volume = float(5) # Gallons

        for a in self.recipe.additions:
            if a.fermentable:

                #
                # Default to the mash efficiency specified by the
                # recipe.
                efficiency = self.recipe.efficiency

                #
                # If the fermentable is extract, we don't take mash
                # efficiency into account - instead, we just use the
                # potential on record for the ingredient.
                #
                if a.fermentable.type == 'EXTRACT':
                    efficiency = 1

                points += (a.amount * a.fermentable.ppg * efficiency) / volume

        return round(points / 1000 + 1, 3)

    @property
    def final_gravity(self):
        """
        (Estimated) final gravity of the recipe based on yeast attenuation.
        """

        # Default the attenuation to 75%
        attenuation = .75

        #
        # If one or more yeast addition is specified,
        # use the highest attenuation available.
        #
        yeast = [a.yeast.attenuation
                    for a in self.recipe.additions
                    if a.yeast]
        if yeast:
            attenuation = max(yeast)

        points = (self.original_gravity - 1) * 1000
        final = points - (points * attenuation)
        
        return round(final / 1000 + 1, 3)

    @property
    def abv(self):
        abv = (self.original_gravity - self.final_gravity) * 131
        return round(abv, 1) / 100
