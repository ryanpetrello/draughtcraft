import math

class Calculations(object):

    def __init__(self, recipe):
        self.recipe = recipe

    @property
    def original_gravity(self):
        """
        Original gravity of the recipe.
        """

        points = 0
        volume = float(self.recipe.gallons)

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

    @property
    def tinseth(self):
        """
        (Estimated) IBU of the recipe based on available hops and utilization.
        """
        total = 0

        #
        # Calculated with Glenn Tinseth's formula:
        # http://realbeer.com/hops/research.html
        #

        volume = float(self.recipe.gallons)
        hops = [a for a in self.recipe.additions if a.hop]
        for h in hops:
            #
            # Start by calculating utilization
            # Bigness factor * Boil Time factor
            #
            
            # Calculate duration in minutes
            duration = h.duration.seconds / 60 

            # Calculate the bigness factor
            bigness = 1.65 * (math.pow(0.000125, (self.original_gravity - 1)))

            # Calculate the boil time factor
            boiltime = (1 - math.exp(-0.04 * duration)) / 4.15

            # Calculate utilization
            utilization = bigness * boiltime

            # Convert pounds to ounces
            ounces = h.amount * 16.0

            # IBU = Utilization * ((Ounces * AAU * 7490) / Gallons)
            alpha_acid = h.alpha_acid / 100
            total += utilization * ((ounces * alpha_acid * 7490) / volume)

        return round(total, 1)

    @property
    def ibu(self):
        return self.tinseth
