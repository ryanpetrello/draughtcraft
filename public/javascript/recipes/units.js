(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.units = n.recipes.units || {};
    ns = n.recipes.units;

    var punctuationRe = /[^0-9a-zA-z.\s]/;
    var unitRe = /[a-zA-Z]+( \.)?/;
    var amountRe = /[0-9]+/;

    var UNITS = [
        'GRAM',
        'KILOGRAM',
        'OUNCE',
        'POUND',
        'TEASPOON',
        'TABLESPOON',
        'GALLON',
        'LITER'
    ];

    var UNIT_MAP = {
        'lb'            : 'POUND',
        'Lb'            : 'POUND',
        'LB'            : 'POUND',
        'oz'            : 'OUNCE',
        'Oz'            : 'OUNCE',
        'OZ'            : 'OUNCE',
        'g'             : 'GRAM',
        'kg'            : 'KILOGRAM',
        't'             : 'TEASPOON',
        'ts'            : 'TEASPOON',
        'tsp'           : 'TEASPOON',
        'Tsp'           : 'TEASPOON',
        'tspn'          : 'TEASPOON',
        'tbs'           : 'TABLESPOON',
        'tbsp'          : 'TABLESPOON',
        'tblsp'         : 'TABLESPOON',
        'tblspn'        : 'TABLESPOON',
        'Tbsp'          : 'TABLESPOON',
        'T'             : 'TABLESPOON',
        'G'             : 'GALLON',
        'gal'           : 'GALLON',
        'Gal'           : 'GALLON',
        'l'             : 'LITER',
        'L'             : 'LITER'
    };

    __zip__ = function() {
        var args = [].slice.call(arguments);
        var longest = args.reduce(function(a, b){
            return a.length > b.length ? a : b
        }, []);

        return longest.map(function(_, i){
            return args.map(function(array){return array[i]})
        });
    };

    __pairs__ = function(val){
        /*
         * Convert a unit string into a list of pairs, e.g.,
         * '2.5 lb. 6oz' => [[2.5, 'lb'], [6, 'oz']]
         *
         * Input should already be stripped of any [^0-9a-zA-Z] characters.
         */

        // Find all unit amounts
        var amounts = val.split(unitRe);
        amounts = $.grep(amounts, function(x){
            return x;
        });
        amounts = $.grep(amounts, function(x){
            return x != '.';
        });

        /*
         * Build a regex that matches the amounts.
         * Split on that regex, and filter out the amounts,
         * leaving only the remainder (units).
         */
        var partsRe = new RegExp(
            (""+(amounts.join('|'))+"").replace(/\./g, "\\.")
        );
        var parts = val.split(partsRe);
        var units = $.grep(parts, function(x){
            return x;
        });

        amounts = __coerce_amounts__(amounts);
        units = __coerce_units__(units);
        return __zip__(amounts, units);
    };

    __coerce_amounts__ = function(amounts){
        // Cast amounts to floats
        return $.map(amounts, function(x){
            return parseFloat(x.replace(/\. /g, ''))
        });
    };

    __coerce_units__ = function(units){
        // Filter all punctuation from the units
        units = $.map(units, function(x){
            return x.replace(/[^a-zA-Z]/g, '');
        });

        function unitize(unit){
            var coerced;

            // Look for exact matches
            if(UNITS.indexOf(unit.toUpperCase()) >= 0)
                coerced = unit.toUpperCase();

            // Look for alias matches
            if(UNIT_MAP[unit])
                coerced = UNIT_MAP[unit];

            var unit = unit.replace(/s$/, "");

            // Look for simple matches on plurality
            if(UNITS.indexOf(unit.toUpperCase()) >= 0)
                coerced = unit.toUpperCase();

            // Look for simple alias matches on plurality
            if(UNIT_MAP[unit])
                coerced = UNIT_MAP[unit];

            return coerced;
        };

        return $.map(units, unitize);
    };

    ns.from_str = function(val){
        val = val.trim().replace(punctuationRe, '');
        return __pairs__(val);
    };

})($.draughtcraft = $.draughtcraft || {}, $);
