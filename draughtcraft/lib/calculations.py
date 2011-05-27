import math

class Calculations(object):

    def __init__(self, recipe):
        self.recipe = recipe

    #
    # Gravity and alcohol content calculations
    #
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
    
    #
    # Color Calculations
    #
    @property
    def srm(self):
        total = 0
        fermentables = [a for a in self.recipe.additions if a.fermentable]
        for f in fermentables:
            total += (f.amount * f.ingredient.lovibond)

        gallons = float(self.recipe.gallons)
        srm = total / gallons

        return round(srm, 1)

    #
    # International Bittering Units Calculations
    # 
    @property
    def ibu(self):
        """
        (Estimated) IBU of the recipe based on available hops and utilization.
        """
        return self.tinseth

    @property
    def tinseth(self):
        """
        IBU as calculated with Glenn Tinseth's formula:
        http://www.realbeer.com/hops/FAQ.html
        """
        total = 0

        gallons = float(self.recipe.gallons)
        hops = [a for a in self.recipe.additions if a.hop and a.step == 'boil']
        for h in hops:
            #
            # Start by calculating utilization
            # Bigness factor * Boil Time factor
            #
            
            # Calculate duration in minutes
            minutes = h.duration.seconds / 60 

            # Calculate the bigness factor
            bigness = 1.65 * (math.pow(0.000125, (self.original_gravity - 1)))

            # Calculate the boil time factor
            boiltime = (1 - math.exp(-0.04 * minutes)) / 4.15

            # Calculate utilization
            utilization = bigness * boiltime
            #
            # If the hops are in pellet form,
            # increase utilization by 15%
            #
            if h.form == 'PELLET':
                utilization *= 1.15

            # Convert pounds to ounces
            ounces = h.amount * 16.0

            # IBU = Utilization * ((Ounces * AAU * 7490) / Gallons)
            alpha_acid = h.alpha_acid / 100
            total += utilization * ((ounces * alpha_acid * 7490) / gallons)

        return round(total, 1)

    @property
    def rager(self):
        """
        IBU as calculated with Jakie Rager's formula:
        http://www.realbeer.com/hops/FAQ.html
        """
        total = 0

        gallons = float(self.recipe.gallons)
        hops = [a for a in self.recipe.additions if a.hop and a.step == 'boil']
        for h in hops:
            # Calculate duration in minutes
            minutes = h.duration.seconds / 60 

            # Calculate utilization as a decimal
            utilization = 18.11 + 13.86 * math.tanh((minutes - 31.32) / 18.27)
            utilization /= 100
            #
            # If the hops are in pellet form,
            # increase utilization by 15%
            #
            if h.form == 'PELLET':
                utilization *= 1.15

            #
            # If the estimated OG exceeds 1.050, make an adjustment:
            #
            gravity_adjustment = 1
            if self.original_gravity > 1.050:
                gravity_adjustment += ((self.original_gravity - 1.050) / 0.2)

            # Convert pounds to ounces
            ounces = h.amount * 16.0

            # Convert AA rating to a decimal
            alpha_acid = h.alpha_acid / 100

            total += (ounces * utilization * alpha_acid * 7462) / (gallons * gravity_adjustment)

        return round(total, 1)

    @property
    def daniels(self):
        """
        IBU as calculated with Ray Daniels' formula in
        "Designing Great Beers".
        """
        total = 0

        gallons = float(self.recipe.gallons)
        hops = [a for a in self.recipe.additions if a.hop and a.step == 'boil']
        for h in hops:
            # Calculate duration in minutes
            minutes = h.duration.seconds / 60 

            #
            # Calculate utilization based on the table provided in chapter 9 of
            # Ray Daniels' book, "Designing Great Beers".
            #
            utilization = .05
            if h.form == 'PELLET':
                # Generic utilization values for pellet-form hops
                utilization_table = [
                    (75, .34),
                    (60, .30),
                    (45, .27),
                    (30, .24),
                    (20, .19),
                    (10, .15),
                    (0, .06)
                ]
            else:
                # Generic utilization values for whole leaf and plug-form hops
                utilization_table = [
                    (75, .27),
                    (60, .24),
                    (45, .22),
                    (30, .19),
                    (20, .15),
                    (10, .12),
                    (0, .05)
                ]

            #
            # From the highest time range in the list working down,
            # loop through until we find a range the recipe's boil duration
            # fits into.  Once we've found the highest matched range,
            # we know the utilization value.
            #
            for time, ratio in utilization_table:
                if minutes > time:
                    utilization = ratio
                    break

            # Convert pounds to ounces
            ounces = h.amount * 16.0

            # Convert AA rating to a decimal
            alpha_acid = h.alpha_acid / 100

            #
            # If the estimated OG exceeds 1.050, make an adjustment:
            #
            gravity_adjustment = 1
            if self.original_gravity > 1.050:
                gravity_adjustment += ((self.original_gravity - 1.050) / 0.2)

            total += (ounces * utilization * alpha_acid * 7462) / (gallons * gravity_adjustment)

        return round(total, 1)
