(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.units = n.recipes.units || {};
    ns = n.recipes.units;

    var punctuationRe = /[^0-9a-zA-z.\s]/;
    var unitRe = /[a-zA-Z]+( \.)?/;

    function PoundOunceMerge(){
        this.signature = ['POUND', 'OUNCE'];
        this.merge = function(units){
            var pounds = units[0];
            var ounces = units[1];
            return [pounds[0] + (ounces[0] / 16), 'POUND'];
        };
    };

    function OunceMerge(){
        this.signature = ['OUNCE'];
        this.merge = function(ounces){
            return [ounces[0] / 16, 'POUND'];
        };
    };

    function GramMerge(){
        this.signature = ['GRAM'];
        this.merge = function(grams){
            return [grams[0] / 453.59237, "POUND"];
        };
    };

    function KilogramMerge(){
        this.signature = ['KILOGRAM'];
        this.merge = function(kilograms){
            return [kilograms[0] / .45359237, "POUND"];
        };
    };

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
        var pairs = __pairs__(val);
        var units = $.map(pairs, function(value){
            return value[1];
        });

        var pair;

        $.each([
            new PoundOunceMerge(),
            new OunceMerge(),
            new GramMerge(),
            new KilogramMerge()
        ], function(index, value){
            if(JSON.stringify(value.signature) == JSON.stringify(units)){
                pair = value.merge(pairs);
                return;
            }
        });

        if(pair)
            return pair;

        return pairs[0];
    };

    (function test_pairs(){
        var eq = function(a, b){
            chai.expect(__pairs__(a)).to.deep.equal(b);
        };

        eq('2lb', [[2.0, 'POUND']]);
        eq('2Lb', [[2.0, 'POUND']]);
        eq('2lb 5oz', [[2.0, 'POUND'], [5.0, 'OUNCE']]);
        eq('2.5lb 5oz', [[2.5, 'POUND'], [5.0, 'OUNCE']]);
        eq('2.5lb 5.5oz', [[2.5, 'POUND'], [5.5, 'OUNCE']]);

        eq('2lb.', [[2.0, 'POUND']]);
        eq('2lb. 5oz.', [[2.0, 'POUND'], [5.0, 'OUNCE']]);
        eq('2.5lb. 5oz.', [[2.5, 'POUND'], [5.0, 'OUNCE']]);
        eq('2.5lb. 5.5oz.', [[2.5, 'POUND'], [5.5, 'OUNCE']]);

        eq('2lb5oz', [[2.0, 'POUND'], [5.0, 'OUNCE']]);
        eq('2.5lb5oz', [[2.5, 'POUND'], [5.0, 'OUNCE']]);
        eq('2.5lb5.5oz', [[2.5, 'POUND'], [5.5, 'OUNCE']]);
        eq('2lb.5oz', [[2.0, 'POUND'], [.5, 'OUNCE']]);
        eq('2.5lb.5oz', [[2.5, 'POUND'], [.5, 'OUNCE']]);
        eq('2lb.5oz.', [[2.0, 'POUND'], [.5, 'OUNCE']]);
    })();

    (function test_coerce_amounts(){
        var eq = function(a, b){
            chai.expect(__coerce_amounts__(a)).to.deep.equal(b);
        };
        eq(['525.75'], [525.75]);
    })();

    (function test_coerce_units(){
        var eq = function(a, b){
            chai.expect(__coerce_units__(a)).to.deep.equal(b);
        };

        eq(['lb'], ['POUND'])
        eq(['lbs'], ['POUND'])
        eq(['pound'], ['POUND'])
        eq(['Pound'], ['POUND'])
        eq(['pounds'], ['POUND'])
        eq(['Pounds'], ['POUND'])

        eq(['oz'], ['OUNCE'])
        eq(['ounce'], ['OUNCE'])
        eq(['ounces'], ['OUNCE'])
        eq(['Ounce'], ['OUNCE'])
        eq(['Ounces'], ['OUNCE'])

        eq(['g'], ['GRAM'])
        eq(['gram'], ['GRAM'])
        eq(['Gram'], ['GRAM'])
        eq(['grams'], ['GRAM'])
        eq(['Grams'], ['GRAM'])

        eq(['kg'], ['KILOGRAM'])
        eq(['kilogram'], ['KILOGRAM'])
        eq(['Kilogram'], ['KILOGRAM'])
        eq(['kilograms'], ['KILOGRAM'])
        eq(['Kilograms'], ['KILOGRAM'])

        eq(['t'], ['TEASPOON'])
        eq(['ts'], ['TEASPOON'])
        eq(['tsp'], ['TEASPOON'])
        eq(['tspn'], ['TEASPOON'])
        eq(['teaspoon'], ['TEASPOON'])
        eq(['teaspoons'], ['TEASPOON'])
        eq(['Teaspoon'], ['TEASPOON'])
        eq(['Teaspoons'], ['TEASPOON'])

        eq(['T'], ['TABLESPOON'])
        eq(['tbs'], ['TABLESPOON'])
        eq(['tbsp'], ['TABLESPOON'])
        eq(['tblsp'], ['TABLESPOON'])
        eq(['tblspn'], ['TABLESPOON'])
        eq(['tablespoon'], ['TABLESPOON'])
        eq(['tablespoons'], ['TABLESPOON'])
        eq(['Tablespoon'], ['TABLESPOON'])
        eq(['Tablespoons'], ['TABLESPOON'])

        eq(['G'], ['GALLON'])
        eq(['gal'], ['GALLON'])
        eq(['Gal'], ['GALLON'])
        eq(['gallon'], ['GALLON'])
        eq(['Gallon'], ['GALLON'])
        eq(['gallons'], ['GALLON'])
        eq(['Gallons'], ['GALLON'])
        
        eq(['l'], ['LITER'])
        eq(['L'], ['LITER'])
        eq(['liter'], ['LITER'])
        eq(['Liter'], ['LITER'])
        eq(['liters'], ['LITER'])
        eq(['Liters'], ['LITER'])
    })();

})($.draughtcraft = $.draughtcraft || {}, $);
