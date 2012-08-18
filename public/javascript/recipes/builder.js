(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;
    ns.model = ns.model || {};

    ns.model.RecipeAddition = function(){

        var writeTimeoutInstance = null;
        this.editing = ko.observable(false);

        this.amount = ko.observable();
        this.unit = ko.observable();
        this.use = ko.observable();
        this.minutes = ko.observable();

        this.form = ko.observable();
        this.alpha_acid = ko.observable();

        this.ingredient = ko.observable();

        var write = $.proxy(function(value){
            clearTimeout(writeTimeoutInstance);
            var result = n.recipes.units.from_str(value), amount = result[0],
                unit = result[1];
            this.amount(amount);
            this.unit(unit);
        }, this);

        this.readable_amount = ko.computed({
            read: function(){
                if(this.amount())
                    return n.recipes.units.to_str(this.amount(), this.unit());
            },
            write: write,
            owner: this
        });

        this.delayedWrite = $.proxy(function(obj, evt){
            clearTimeout(writeTimeoutInstance);
            var value = evt.currentTarget.value;
            writeTimeoutInstance = setTimeout(write, 1750, value);
        }, this);

        this.removeAddition = $.proxy(function(addition) {
            this.recipe.mash.additions.remove(addition);
            this.recipe.boil.additions.remove(addition);
            this.recipe.fermentation.additions.remove(addition);
        }, ns);

        this.mash_percentage = ko.computed({
            read: function(){
                var sum = 0.0;
                $.each(ns.recipe.mash.additions(), function(_, a){
                    var type = (a.ingredient().printed_type || '').toUpperCase();
                    if(type != 'GRAIN' && type != 'EXTRACT')
                        return;
                    sum += a.amount();
                });

                return ((this.amount() / sum) * 100).toFixed(1) + '%';
            },
            owner: this
        });

    };

    ns.model.RecipeStep = function(){
        this.additions = ko.observableArray();
        this.sortedAdditions = ko.computed(function(){
            return this.additions().sort(function(a, b){
                return a.amount() > b.amount() ? -1 : 0;
            });
        }, this);

        var partition = function(cls){
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient().class == cls;
            });
        }

        this.fermentables = ko.computed($.proxy(partition, this, 'Fermentable'), this);
        this.hops = ko.computed($.proxy(partition, this, 'Hop'), this);
        this.yeast = ko.computed($.proxy(partition, this, 'Yeast'), this);
        this.extra = ko.computed($.proxy(partition, this, 'Extra'), this);

        this.addAddition = $.proxy(function(obj, evt){
            var field = evt.currentTarget;
            var id = field.value;
            // Deep copy
            var ingredient = $.extend(
                true,
                {},
                ns.recipe.inventory().map[id]
            );

            // Create the new addition
            var a = new ns.model.RecipeAddition();

            a.amount('0');
            a.unit('POUND');
            a.ingredient(ingredient);

            // Hop-specific
            if(a.ingredient().class.toUpperCase() == 'HOP'){
                a.alpha_acid(a.ingredient().alpha_acid);
                a.unit('OUNCE');
                a.form('LEAF');
            }

            // Boil-specific
            if(this == ns.recipe.boil){
                a.use('BOIL');
                a.minutes(60);
            }

            // Fermentation-specific
            if(this == ns.recipe.fermentation)
                a.use('PRIMARY');

            this.additions.push(a);
            a.editing(true);

            // Reset all of the select boxes
            field.selectedIndex = 0;
            ns.recipe.initInventoryDropDowns();
        }, this);

    };

    ns.model.Recipe = function(){
        this.name = ko.observable();
        this.volume = ko.observable();
        this.style = ko.observable();

        this.mash = new ns.model.RecipeStep();
        this.boil = new ns.model.RecipeStep();
        this.fermentation = new ns.model.RecipeStep();

        this.boil_minutes = ko.observable();

        this.efficiency = ko.observable();
        this.ibu_method = ko.observable();

        // Inventory
        this.inventory = ko.observableArray();

        this.initInventoryDropDowns = function(){
            $(".inventory select").selectBox('destroy').selectBox({
                'menuTransition'    : 'fade',
                'menuSpeed'         : 'fast'
            });
        };

        // Style attributes
        this.style_range = $.proxy(function(attr){
            var min = this.STYLE_MAP[this.style()]['min_'+attr];
            var max = this.STYLE_MAP[this.style()]['max_'+attr];

            if(min && max){
                min = min.toFixed(3);
                max = max.toFixed(3);
                if(attr == 'abv'){
                    min = parseFloat(min).toFixed(1) + '%';
                    max = parseFloat(max).toFixed(1) + '%';
                }
                if(attr == 'ibu' || attr == 'srm'){
                    min = parseFloat(min).toFixed();
                    max = parseFloat(max).toFixed();
                }

                var range = min + ' - ' + max
                if(attr == 'srm')
                    range += ' <span class="unit">&#186 SRM</span>';
                if(attr == 'ibu')
                    range += ' <span class="unit">IBU</span>';
                return range;
            }

            return '-';
        }, this);

        this.style_matches = $.proxy(function(attr){
            if(!this.style())
                return "</span>"

            var min = this.STYLE_MAP[this.style()]['min_'+attr];
            var max = this.STYLE_MAP[this.style()]['max_'+attr];

            if(min && max && this[attr]() <= max && this[attr]() >= min)
                return "<img src='/images/yes.png' />";

            return "<img src='/images/no.png' />";
        }, this);

        this.STYLE_MAP = {};
        $.each(ns.STYLES, $.proxy(function(_, style){
            this.STYLE_MAP[style.id] = style;
        }, this));

        // Calculations
        this.og = ko.computed(function(){
            var points = 0;

            $.each(
                this.mash.fermentables().concat(
                    this.boil.fermentables(),
                    this.fermentation.fermentables()
                ),
                $.proxy(function(_, a){
                    var type = (a.ingredient().printed_type || '').toUpperCase();

                    // Default to the mash efficiency specified by the recipe.
                    var efficiency = this.efficiency();

                    /*
                     * If the fermentable is extract, we don't take mash
                     * efficiency into account - instead, we just use the
                     * potential on record for the ingredient.
                     */
                    if(type == 'EXTRACT')
                        efficiency = 1.0;

                    points += (a.amount() * a.ingredient().ppg * efficiency) / this.volume();
                }, this)
            );

            return (points / 1000 + 1).toFixed(3);

        }, this);

        this.fg = ko.computed(function(){

            // Default attenuation to 75%;
            var attenuation = 0.75;

            $.each(this.fermentation.yeast(), function(_, a){
                // For more than one yeast addition, choose the highest attenuation
                attenuation = Math.max(attenuation, a.ingredient().attenuation);
            });

            var points = (this.og() - 1) * 1000;
            var fg = points - (points * attenuation);
            return (fg / 1000 + 1).toFixed(3);

        }, this);

        this.abv = ko.computed(function(){
            var abv = (this.og() - this.fg()) * 131;
            return abv;
        }, this);

        this.ibu = ko.computed(function(){
            var formulas = {};
            formulas['tinseth'] = $.proxy(function(){
                /*
                 * IBU as calculated with Glenn Tinseth's formula:
                 * http://www.realbeer.com/hops/FAQ.html
                 */
                var total = 0;

                $.each(this.boil.hops(), $.proxy(function(_, h){

                    /*
                     * Start by calculating utilization
                     * Bigness factor * Boil Time factor
                     */
                    //
                    // Calculate the bigness factor
                    var bigness = 1.65 * (Math.pow(0.000125, (this.og() - 1)));

                    // Calculate the boil time factor
                    var boiltime = (1 - Math.exp(-0.04 * h.minutes())) / 4.15;

                    // Calculate utilization
                    utilization = bigness * boiltime;

                    /*
                     * If the hops are in pellet form,
                     * increase utilization by 15%
                     */
                    if(h.form() == 'PELLET')
                        utilization *= 1.15;

                    // Convert pounds to ounces
                    var ounces = h.amount() * 16.0;

                    // IBU = Utilization * ((Ounces * AAU * 7490) / Gallons)
                    var alpha_acid = h.ingredient().alpha_acid / 100;
                    total += utilization * ((ounces * alpha_acid * 7490) / this.volume());

                }, this));

                return Math.round(total);
            }, this);

            if(this.ibu_method())
                return formulas[this.ibu_method()]()

        }, this);

        this.srm = ko.computed(function(){
            var total = 0;

            $.each(
                this.mash.fermentables().concat(
                    this.boil.fermentables(),
                    this.fermentation.fermentables()
                ),
                $.proxy(function(_, a){
                    var mcu = (a.amount() * a.ingredient().lovibond) / this.volume();
                    total += mcu;
                }, this)
            );

            return (1.4922 * Math.pow(total, 0.6859)).toFixed(1);

        }, this);

        this.srmClass = ko.computed(function(){
            return 'srm-' + Math.min(parseInt(this.srm()), 30);
        }, this);

        this.printable_srm = ko.computed(function(){
            return this.srm() + ' <span class="unit">&#186; SRM</span>';
        }, this);

        this.printable_ebc = ko.computed(function(){
            return this.srm() + ' <span class="unit">EBC</span>';
        }, this);

        this.color = ko.computed(function(){
            return this.printable_srm();
        }, this);

    };

    ns.RecipeViewModel = function(){
        ns.recipe = this.recipe = new ns.model.Recipe();

        this.STYLES = ns.STYLES;

        this.HOP_USES = [
            {'id': 'FIRST WORT', 'name': 'First Wort'},
            {'id': 'BOIL', 'name': 'Boil'},
            {'id': 'FLAME OUT', 'name': 'Flame Out'}
        ];
        this.HOP_FORMS = [
            {'id': 'LEAF', 'name': 'Leaf'},
            {'id': 'PELLET', 'name': 'Pellet'},
            {'id': 'PLUG', 'name': 'Plug'}
        ];

        this.BOIL_TIMES = $.proxy(function(){
            var minutes = this.recipe.boil_minutes() || 60;
            var times = [];
            while(minutes >= 5){
                times.push({'id': minutes, 'name': minutes + ' min'});
                minutes -= 5;
            }
            times.push({'id': 4, 'name': '4 min'});
            times.push({'id': 3, 'name': '3 min'});
            times.push({'id': 2, 'name': '2 min'});
            times.push({'id': 1, 'name': '1 min'});
            times.push({'id': 0, 'name': '0 min'});
            return times;
        }, this);

        var show = $.proxy(function(){
            // Display the UI after data has been fetched via AJAX.
            $('.builder-loading').hide();
            var last = window.location.hash.replace('#', '');
            this.activateStep(last || 'mash');
            $('.step.results').css('display', 'block');
        }, this);

        this.activateStep = function(step){
            $('.step').removeClass('active');
            $('.step.'+step).addClass('active');
            window.location = '#'+step;
        };

        this.stripe = function(table){
            var rows = $(table).find("tr:not(:empty):not(.header)")
            rows.each(function(i, row){
                if(i % 2 == 0)
                    $(row).addClass('even');
                else
                    $(row).removeClass('even');
            });
        };

        ($.proxy(function(){
            // Fetch recipe data via AJAX and render the UI
            $.getJSON(
                window.location.pathname.toString()+'index.json',
                ($.proxy(function(data){
                    show();

                    var data = data['recipe'];
                    var pop = function(obj, key){
                        var v = obj[key];
                        if(v)
                            delete obj[key]
                        return v;
                    };

                    var appendAdditions = $.proxy(function(key){
                        var additions = pop(data, key);
                        for(var i in additions){
                            var a = new ns.model.RecipeAddition();
                            for(var k in additions[i]){
                                if(a[k])
                                    a[k](additions[i][k]);
                            }
                            this.recipe[key].additions.push(a);
                        }
                    }, this);
                    appendAdditions('mash');
                    appendAdditions('boil');
                    appendAdditions('fermentation');

                    // Recipe attributes
                    for(var k in data){
                        if(this.recipe[k])
                            this.recipe[k](data[k]);
                    }

                    // For speed, build a map of ingredients indexed by ID
                    var _map = {};
                    $.each(this.recipe.inventory(), function(type, ingredients){
                        $.each(ingredients, function(_, ingredient){
                            _map[ingredient.id] = ingredient;
                        });
                    });
                    this.recipe.inventory().map = _map;

                    // Render select boxes
                    $("#header select").selectBox({
                        'menuTransition'    : 'fade',
                        'menuSpeed'         : 'fast'
                    });

                    this.recipe.initInventoryDropDowns();

                }, this))

            );

        }, this))();

        ko.bindingHandlers.stripe = {update: this.stripe};

    };

})($.draughtcraft = $.draughtcraft || {}, $);

$(function(){
    ko.applyBindings(new $.draughtcraft.recipes.builder.RecipeViewModel());
    // Register a JS tooltip on the author's thumbnail (if there is one).
    $('img.gravatar').tipTip({'delay': 50});
});
