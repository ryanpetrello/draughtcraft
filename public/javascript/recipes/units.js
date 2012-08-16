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
        this.merge = function(units){
            var ounces = units[0];
            return [ounces[0] / 16, 'POUND'];
        };
    };

    function GramMerge(){
        this.signature = ['GRAM'];
        this.merge = function(units){
            var grams = units[0];
            return [grams[0] / 453.59237, "POUND"];
        };
    };

    function KilogramMerge(){
        this.signature = ['KILOGRAM'];
        this.merge = function(units){
            var kilograms = units[0];
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

    var __zip__ = function() {
        var args = [].slice.call(arguments);
        var longest = args.reduce(function(a, b){
            return a.length > b.length ? a : b
        }, []);

        return longest.map(function(_, i){
            return args.map(function(array){return array[i]})
        });
    };

    var __pairs__ = function(val){
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

    var __coerce_amounts__ = function(amounts){
        // Cast amounts to floats
        return $.map(amounts, function(x){
            return parseFloat(x.replace(/\. /g, ''))
        });
    };

    var __coerce_units__ = function(units){
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

    var __expand_pounds__ = function(pounds){
        /*
         * Attempt to expand POUND units into whole POUND, OUNCE units, e.g.,
         *
         * 5.5 lb == 5 lb, 8 oz
         *
         * If the unit is less than a pound, just use ounce increments.
         */

        if(parseInt(pounds) === pounds)
            return [[pounds, 'POUND']];

        if(pounds < 1)
            return [[pounds * 16, 'OUNCE']];

        /*
         * There's 16 oz in a lb.
         * Multiply the weight in pounds by individual
         * ounce increments (e.g., 1, 2, 3...).
         *
         * If the result is roughly an integer,
         * we can split into lbs, oz.
         */
        for (i=0; i<16; i++){
            // We're only interested in the fractional part.
            var decimal = pounds - parseInt(pounds);
            if(decimal * 16 == i+1)
                return [[parseInt(pounds), "POUND"], [i+1, "OUNCE"]];
        }

        return [[pounds, 'POUND']];
    };

    var __str_amount__ = function(amount){
        return amount.toString().match(
            /^\d+(?:\.\d{1,3})?/
        ).toString().replace(
            /\.0*$/,
            ''
        ).replace(
            /\.*$/,
            ''
        );
    };

    var __str_unit__ = function(unit){
        unit = unit.toString();
        var _map = {
            'GRAM'          : 'g',
            'KILOGRAM'      : 'kg',
            'OUNCE'         : 'oz',
            'POUND'         : 'lb',
            'TEASPOON'      : 't',
            'TABLESPOON'    : 'T',
            'GALLON'        : 'Gal',
            'LITER'         : 'L'
        };
        return _map[unit] || '';
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

    ns.to_str = function(amount, unit){
        if(!unit)
            return amount.toString();

        var pairs = [[amount, unit]];

        if(unit == 'POUND')
            pairs = __expand_pounds__(amount);

        var result = $.map(pairs, function(pair){
            if(!pair[0])
                return '';
            return [
                __str_amount__(pair[0]),
                __str_unit__(pair[1])
            ].join(' ');
        }).join(' ');

        /*
         * If result is an empty string, we filtered out all of the "zero"
         * ingredients, leaving nothing.
         *
         * This can happen in circumstances like (0, 'POUND').  This scenario
         * is special cased.
         */
        if(result == '')
            return "0 "+__str_unit__(unit);

        return result;
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

    (function test_from_str(){
        var eq = function(a, b){
            chai.expect(ns.from_str(a)).to.deep.equal(b);
        };

        eq('2lb', [2, 'POUND']);
        eq('2Lb', [2, 'POUND']);
        eq('2LB', [2, 'POUND']);
        eq('2 lb', [2, 'POUND']);
        eq('2 Lb', [2, 'POUND']);
        eq('2 LB', [2, 'POUND']);

        eq('8oz', [.5, 'POUND']);
        eq('8.5oz', [.53125, 'POUND']);

        eq('2lb 8oz', [2.5, 'POUND']);
        eq('2.5lb 8oz', [3, 'POUND']);
        eq('2.5lb 8.5oz', [3.03125, 'POUND']);

        $.each(UNIT_MAP, function(key, value){
            if(value == 'OUNCE') return;
            if(value == 'GRAM') return;
            if(value == 'KILOGRAM') return;
            eq('5'+key, [5, value]);
        });

        eq('453.59237g', [1, 'POUND']);
        eq('.45359237kg', [1, 'POUND']);

        eq('5', [5, undefined]);
        eq('5.25', [5.25, undefined]);

    })();

    (function test_to_str(){
        var eq = function(a, b){
            chai.expect(ns.to_str(a[0], a[1])).to.equal(b);
        };

        eq([5, 'POUND'], '5 lb');
        eq([5, 'OUNCE'], '5 oz');
        eq([5, 'GRAM'], '5 g');
        eq([5, 'TEASPOON'], '5 t');
        eq([5, 'TABLESPOON'], '5 T');
        eq([5, 'GALLON'], '5 Gal');
        eq([5, 'LITER'], '5 L');

        eq([5.0, 'POUND'], '5 lb');
        eq([5.0, 'OUNCE'], '5 oz');
        eq([5.0, 'GRAM'], '5 g');
        eq([5.0, 'TEASPOON'], '5 t');
        eq([5.0, 'TABLESPOON'], '5 T');
        eq([5.0, 'GALLON'], '5 Gal');
        eq([5.0, 'LITER'], '5 L');

        eq([5.1, 'POUND'], '5.1 lb');
        eq([5.1, 'OUNCE'], '5.1 oz');
        eq([5.1, 'GRAM'], '5.1 g');
        eq([5.1, 'TEASPOON'], '5.1 t');
        eq([5.1, 'TABLESPOON'], '5.1 T');
        eq([5.1, 'GALLON'], '5.1 Gal');
        eq([5.1, 'LITER'], '5.1 L');

        eq([5.25, 'POUND'], '5 lb 4 oz');
        eq([.25, 'POUND'], '4 oz');

        eq([0, 'POUND'], '0 lb');

        eq([5, undefined], '5');
        eq([5.0, undefined], '5');
        eq([5.25, undefined], '5.25');

        eq([.0625, 'POUND'], '1 oz')
        eq([.125, 'POUND'], '2 oz')
        eq([.1875, 'POUND'], '3 oz')
        eq([.25, 'POUND'], '4 oz')
        eq([.3125, 'POUND'], '5 oz')
        eq([.375, 'POUND'], '6 oz')
        eq([.4375, 'POUND'], '7 oz')
        eq([.50, 'POUND'], '8 oz')
        eq([.5625, 'POUND'], '9 oz')
        eq([.625, 'POUND'], '10 oz')
        eq([.6875, 'POUND'], '11 oz')
        eq([.75, 'POUND'], '12 oz')
        eq([.8125, 'POUND'], '13 oz')
        eq([.875, 'POUND'], '14 oz')
        eq([.9375, 'POUND'], '15 oz')

        eq([1.0625, 'POUND'], '1 lb 1 oz')
        eq([1.125, 'POUND'], '1 lb 2 oz')
        eq([1.1875, 'POUND'], '1 lb 3 oz')
        eq([1.25, 'POUND'], '1 lb 4 oz')
        eq([1.3125, 'POUND'], '1 lb 5 oz')
        eq([1.375, 'POUND'], '1 lb 6 oz')
        eq([1.4375, 'POUND'], '1 lb 7 oz')
        eq([1.50, 'POUND'], '1 lb 8 oz')
        eq([1.5625, 'POUND'], '1 lb 9 oz')
        eq([1.625, 'POUND'], '1 lb 10 oz')
        eq([1.6875, 'POUND'], '1 lb 11 oz')
        eq([1.75, 'POUND'], '1 lb 12 oz')
        eq([1.8125, 'POUND'], '1 lb 13 oz')
        eq([1.875, 'POUND'], '1 lb 14 oz')
        eq([1.9375, 'POUND'], '1 lb 15 oz')

        eq([1.171, 'POUND'], '1.171 lb')

    })();


})($.draughtcraft = $.draughtcraft || {}, $);
