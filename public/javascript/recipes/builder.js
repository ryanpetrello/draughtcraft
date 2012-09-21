String.prototype.toTitleCase = function () {
    return this.replace(
        /\w\S*/g,
        function(txt){
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
};

(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;
    ns.model = ns.model || {};

    var roundTo = function(number, to) {
        to = Math.pow(10, to);
        return Math.round(number * to) / to;
    };

    ns.model.FermentationStep = function(){
        this.step = ko.observable();
        this.days = ko.observable();
        this.fahrenheit = ko.observable();

        this.celsius = ko.computed({
            read: function(){
                return Math.round((this.fahrenheit() - 32) / 1.8);
            },
            write: function(celsius){
                this.fahrenheit(Math.round((celsius * 1.8) + 32));
            },
            owner: this
        });

    };

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
            var amount = 0, unit = 'POUND';

            var result = n.recipes.units.from_str(value);
            if(result && !isNaN(result[0]))
                amount = result[0], unit = result[1];

            this.amount(amount);
            this.unit(unit);
        }, this);

        this.readable_amount = ko.computed({
            read: function(){
                if(this.amount()){
                    var amount = this.amount();
                    var unit = this.unit()
                    if(ns.recipe.metric() == true){
                        var pair = n.recipes.units.to_metric(amount, unit);
                        amount = pair[0];
                        unit = pair[1];
                    }
                    return n.recipes.units.to_str(amount, unit);
                }
            },
            write: write,
            owner: this
        });

        this.pounds = ko.computed(function(){
            if(this.unit() == 'POUND')
                return this.amount();
            if(this.unit() == 'OUNCE')
                return this.amount() / 16.0;
            return 0;
        }, this);

        this.sortable_minutes = ko.computed(function(){
            if(this.use() == 'FIRST WORT')
                return 60 * 60;
            if(this.use() == 'POST BOIL' || this.use() == 'FLAME-OUT')
                return -1;
            return this.minutes();
        }, this);

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
                    sum += a.pounds();
                });

                if(isNaN(this.pounds() / sum))
                    return '0%'; // Avoid zero division

                return roundTo((this.pounds() / sum) * 100, 1) + '%';
            },
            owner: this
        });

    };

    ns.model.RecipeAddition.prototype.toJSON = function() {
        return {
            amount: this.amount,
            unit: this.unit,
            use: this.use,
            duration: this.minutes,

            form: this.form,
            alpha_acid: this.alpha_acid,

            ingredient: this.ingredient
        };
    };

    ns.model.RecipeStep = function(){
        this.additions = ko.observableArray();
        this.sortedAdditions = ko.computed(function(){
            return this.additions().sort(function(a, b){
                if (
                    a.ingredient().class.toUpperCase() == 'HOP' &&
                    b.ingredient().class.toUpperCase() == 'HOP'
                )
                    return a.sortable_minutes() > b.sortable_minutes() ? -1 : 0;

                return a.pounds() > b.pounds() ? -1 : 0;
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
            a.unit(ingredient.default_unit || 'POUND');
            a.ingredient(ingredient);

            // Hop-specific
            if(a.ingredient().class.toUpperCase() == 'HOP'){
                a.alpha_acid(a.ingredient().alpha_acid);
                a.unit('OUNCE');
                a.form('LEAF');
            }

            if(this == ns.recipe.mash)
                a.use('MASH');
            else if(this == ns.recipe.boil){
                a.use('BOIL');
                a.minutes(60);
            }else if(this == ns.recipe.fermentation)
                a.use('PRIMARY');

            // Fermentation-specific
            if(this == ns.recipe.fermentation)
                a.use('PRIMARY');

            this.additions.push(a);
            a.editing(true);

            // Reset all of the select boxes
            field.selectedIndex = 0;
            ns.recipe.initDropDowns();
        }, this);

    };

    ns.model.RecipeStep.prototype.toJSON = function() {
        return {
            additions: this.additions
        };
    };

    ns.model.Recipe = function(){

        // Set up auto-save bindings
        this.dirtyFlag = new ko.dirtyFlag(this, false);
        ko.computed({
            read: function(){
                if(this.dirtyFlag.dirty()){
                    this.dirtyFlag.reset();
                    ns.save(ko.toJSON(this));
                }
            },
            owner: this,
            deferEvaluation: true
        }).extend({throttle: 500});

        this.editable = ko.observable();
        this.metric = ko.observable();

        this.name = ko.observable();
        this.author = ko.observable();
        this.gallons = ko.observable();
        this.style = ko.observable();

        this.mash = new ns.model.RecipeStep();
        this.boil = new ns.model.RecipeStep();
        this.fermentation = new ns.model.RecipeStep();

        this.efficiency = ko.observable();
        this.ibu_method = ko.observable();

        // Inventory
        this.inventory = ko.observableArray();

        // Extra
        this.mash_method = ko.observable();
        this.mash_instructions = ko.observable();
        this.boil_minutes = ko.observable();
        this.fermentation_steps = ko.observableArray();
        this.notes = ko.observable();

        this.initDropDowns = function(){
            var selects = $(".inventory select");
            selects.selectBox('destroy').selectBox({
                'menuTransition'    : 'fade',
                'menuSpeed'         : 'fast'
            });
        };

        this.initReadOnly = function(){
            $('.step').addClass('active');

            // Replace all fields with static <span>'s
            $('input, textarea').replaceWith(function(){
                return '<span>'+$(this).val().replace(
                    /([^>\r\n]?)(\r\n|\n\r|\r|\n)/g,
                    '$1<br />$2'
                )+'</span>';
            });
            $('select').replaceWith(function(){
                return '<span>'+$(this).find('option:selected').text()+'</span>';
            });
        };

        // Style attributes
        this.style_range = $.proxy(function(attr){

            if(!this.style())
                return '-';

            if(this.metric() && attr == 'srm')
                attr = 'ebc';

            var min = this.STYLE_MAP[this.style()]['min_'+attr];
            var max = this.STYLE_MAP[this.style()]['max_'+attr];

            if(min && max){
                if(attr == 'abv'){
                    min = roundTo(min, 1) + '%';
                    max = roundTo(max, 1) + '%';
                } else if (attr == 'ibu' || attr == 'srm'){
                    min = Math.round(min);
                    max = Math.round(max);
                } else {
                    min = roundTo(min, 3);
                    max = roundTo(max, 3);
                }

                var range = min + ' - ' + max
                if(attr == 'srm')
                    range += ' <span class="unit">&#186 SRM</span>';
                if(attr == 'ebc')
                    range += ' <span class="unit">EBC</span>';
                if(attr == 'ibu')
                    range += ' <span class="unit">IBU</span>';
                return range;
            }

            return '-';
        }, this);

        this.style_matches = $.proxy(function(attr){
            if(!this.style())
                return "</span>";

            if(this.metric() && attr == 'srm')
                attr = 'ebc';

            var min = this.STYLE_MAP[this.style()]['min_'+attr];
            var max = this.STYLE_MAP[this.style()]['max_'+attr];

            if(!min || !max)
                return "</span>";

            if(min && max && this[attr]() <= max && this[attr]() >= min)
                return "<img src='/images/yes.png' />";

            return "<img src='/images/no.png' />";
        }, this);

        this.STYLE_MAP = {};
        $.each(ns.STYLES, $.proxy(function(_, style){
            this.STYLE_MAP[style.id] = style;
        }, this));

        this.volume = ko.computed({
            read: function(){
                amount = this.gallons();
                if(!amount) return '';

                if(this.metric() == true)
                    amount *= 3.78541178;

                // Thanks, floating point math...
                if(Math.ceil(amount) - amount <= .00001)
                    amount = Math.ceil(amount);

                return roundTo(amount, 2);
            },
            write: function(amount){
                if(this.metric() == true)
                    amount *= .264172052637296;
                this.gallons(amount);
            },
            owner: this
        });

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

                    points += (a.pounds() * a.ingredient().ppg * efficiency) / this.gallons();
                }, this)
            );

            return roundTo((points / 1000 + 1), 3);

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
            return roundTo(fg / 1000 + 1, 3);

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

                    var ounces = h.pounds() * 16.0;

                    // IBU = Utilization * ((Ounces * AAU * 7490) / Gallons)
                    var alpha_acid = h.alpha_acid() / 100;
                    total += utilization * ((ounces * alpha_acid * 7490) / this.gallons());

                }, this));

                return Math.round(total);
            }, this);

            formulas['rager'] = $.proxy(function(){
                /*
                 * IBU as calculated with Jakie Rager's formula:
                 * http://www.realbeer.com/hops/FAQ.html
                 */

                var total = 0;
                var gallons = this.gallons();

                $.each(this.boil.hops(), $.proxy(function(_, h){
                    var minutes = h.minutes();

                    function tanh(arg) {
                        // Returns the hyperbolic tangent of the number,
                        // defined as sinh(number)/cosh(number)
                        return (
                            (Math.exp(arg) - Math.exp(-arg)) /
                            (Math.exp(arg) + Math.exp(-arg))
                        );
                    };

                    // Calculate utilization as a decimal
                    var utilization = 18.11 + 13.86 * tanh(
                        (minutes - 31.32) / 18.27
                    );
                    utilization /= 100;

                    /*
                     * If the hops are in pellet form,
                     * increase utilization by 15%
                     */
                    if(h.form() == 'PELLET')
                        utilization *= 1.15;

                    // If the estimated OG exceeds 1.050, make an adjustment
                    var gravity_adjustment = 1;
                    if(this.og() > 1.050)
                        gravity_adjustment += ((this.og() - 1.050) / 0.2);

                    var ounces = h.pounds() * 16.0;

                    // Convert AA rating to a decimal
                    var alpha_acid = h.alpha_acid() / 100;

                    total += (ounces * utilization * alpha_acid *
                              7462) / (gallons * gravity_adjustment);
                }, this));

                return Math.round(total);
            }, this);

            formulas['daniels'] = $.proxy(function(){
                /*
                 * IBU as calculated with Ray Daniels' formula in
                 * "Designing Great Beers".
                 */
                var total = 0;
                var gallons = this.gallons();

                $.each(this.boil.hops(), $.proxy(function(_, h){
                    var minutes = h.minutes();

                    var utilization = .05;

                    // Generic utilization values for hops
                    var utilization_table;
                    if(h.form() == 'PELLET')
                        utilization_table = [
                            [75, .34],
                            [60, .30],
                            [45, .27],
                            [30, .24],
                            [20, .19],
                            [10, .15],
                            [0, .06]
                        ];
                    else
                        utilization_table = [
                            [75, .27],
                            [60, .24],
                            [45, .22],
                            [30, .19],
                            [20, .15],
                            [10, .12],
                            [0, .05]
                        ];

                    /*
                     * From the highest time range in the list working down,
                     * loop through until we find a range the recipe's boil duration
                     * fits into.  Once we've found the highest matched range,
                     * we know the utilization value.
                     */
                    $.each(utilization_table, function(_, i){
                        var time = i[0];
                        var ratio = i[1];
                        if(minutes > time){
                            utilization = ratio;
                            return false;
                        }
                    });

                    var ounces = h.pounds() * 16.0;

                    // Convert AA rating to a decimal
                    var alpha_acid = h.alpha_acid() / 100;

                    // If the estimated OG exceeds 1.050, make an adjustment
                    var gravity_adjustment = 1;
                    if(this.og() > 1.050)
                        gravity_adjustment += ((this.og() - 1.050) / 0.2);

                    total += (ounces * utilization * alpha_acid *
                              7462) / (gallons * gravity_adjustment);

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
                    var mcu = (a.pounds() * a.ingredient().lovibond) / this.gallons();
                    total += mcu;
                }, this)
            );

            return roundTo(1.4922 * Math.pow(total, 0.6859), 1)

        }, this);

        this.ebc = ko.computed(function(){
            return roundTo(this.srm() * 1.97, 1);
        }, this);

        this.srmClass = ko.computed(function(){
            return 'srm-' + Math.min(parseInt(this.srm()), 30);
        }, this);

        this.color = ko.computed(function(){
            if(this.metric() == true)
                return this.printable_ebc();
            return this.srm() + ' <span class="unit">&#186; SRM</span>';
        }, this);

        this.printable_ebc = ko.computed(function(){
            return this.ebc() + ' <span class="unit">EBC</span>';
        }, this);

        this.addFermentationStep = function(){
            var step = [
                'PRIMARY',
                'SECONDARY',
                'TERTIARY'
            ][ns.recipe.fermentation_steps().length];

            var e = new ns.model.FermentationStep();
            e.step(step);
            e.days(7);
            e.fahrenheit(70);
            ns.recipe.fermentation_steps.push(e);
            ns.recipe.initDropDowns();
        };

        this.removeFermentationStep = function(step){
            ns.recipe.fermentation_steps.remove(step);
        };

    };

    ns.model.Recipe.prototype.toJSON = function() {
        return {
            name: this.name,
            gallons: this.gallons,
            style: this.style,

            mash: this.mash,
            boil: this.boil,
            fermentation: this.fermentation,

            boil_minutes: this.boil_minutes,
            mash_method: this.mash_method,
            mash_instructions: this.mash_instructions,
            fermentation_steps: this.fermentation_steps,
            notes: this.notes,

            metric: this.metric
        };
    };

    ns.RecipeViewModel = function(){
        ns.recipe = this.recipe = new ns.model.Recipe();

        this.STYLES = ns.STYLES;
        this.MASH_METHODS = [
            {'id': 'SINGLESTEP', 'name': 'Single Step Infusion'},
            {'id': 'TEMPERATURE', 'name': 'Temperature'},
            {'id': 'DECOCTION', 'name': 'Decoction'},
            {'id': 'MULTISTEP', 'name': 'Multi-Step'}
        ];

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


        this.FERMENTATION_DATE_RANGE = function(){
            var temps = [];
            var i = 1;
            while(i <= 90){
                temps.push(i);
                i++;
            }
            return temps;
        }();
        this.FAHRENHEIT_RANGE = function(){
            var temps = [];
            var i = 100;
            while(i >= 32){
                temps.push(i);
                i--;
            }
            return temps;
        }();
        this.CELSIUS_RANGE = function(){
            var temps = [];
            var i = 35;
            while(i >= 0){
                temps.push(i);
                i--
            }
            return temps;
        }();

        var show = $.proxy(function(){
            // Display the UI after data has been fetched via AJAX.
            $('.builder-loading').hide();
            var last = window.location.hash.replace('#', '');
            this.activateStep(last || $('.step h2 a').html().toLowerCase());
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
            $.post(
                n.recipes.builder.callback,
                {},
                ($.proxy(function(data){
                    show();

                    var editable = data['editable'];
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

                    // Fermentation steps
                    var steps = pop(data, 'fermentation_steps');
                    for(var i in steps){
                        var s = new ns.model.FermentationStep();
                        s['step'](steps[i]['step']);
                        s['days'](steps[i]['days']);
                        s['fahrenheit'](steps[i]['fahrenheit']);
                        this.recipe.fermentation_steps.push(s);
                    }

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

                    this.recipe.editable(editable);
                    if(editable)
                        $("#header select").selectBox({
                            'menuTransition'    : 'fade',
                            'menuSpeed'         : 'fast'
                        });
                    else
                        this.recipe.initReadOnly();

                    this.recipe.initDropDowns();
                    this.recipe.dirtyFlag.reset();
                    $('h1 input').trigger('update');

                    // Register a JS tooltip on the author's thumbnail (if there is one).
                    $('img.gravatar').tipTip({'delay': 50});

                    // Register tooltips for the recipe actions
                    $('div#actions li').each(function(){
                        $(this).tipTip({
                            'delay'     : 25,
                            'edgeOffset': 20
                        });
                    });

                    // Register tooltips for each of the `results` settings buttons
                    $('div.results a.recipe-setting img').each(function(){
                        $(this).tipTip({
                            'delay'     : 25,
                            'edgeOffset': 20,
                            'content'   : $(this).closest('a').attr('title')
                        });
                        $(this).closest('a').removeAttr('title');
                    });


                    // Register submit events on form submission buttons
                    $('#actions li.submit').click(function(e){
                        e.preventDefault();
                        $(this).closest('form').submit();
                    });

                }, this))

            );

        }, this))();

        ko.bindingHandlers.stripe = {update: this.stripe};

    };

    ns.xhr = ns.xhr || {};
    ns.xhr.semaphore = false;
    ns.xhr.callback;

    ns.save = function(json){
        if(ns.xhr.semaphore == true)
            return ns.xhr.callback = $.proxy(ns.save, this, [json]);
        ns.xhr.semaphore = true;

        $('.publish-btn').attr('disabled', true).text('Saving...');
        $.ajax({
            type: 'POST',
            url: window.location.pathname.toString() + '?_method=PUT',
            data: {
                recipe: json
            },
            complete: function(){
                $('.publish-btn').attr('disabled', false).text('Publish Changes');
                ns.xhr.semaphore = false;
                if(ns.xhr.callback){
                    ns.xhr.callback();
                    ns.xhr.callback = undefined;
                }
            }
        });
    };

})($.draughtcraft = $.draughtcraft || {}, $);

$(function(){

    /*
     * An observable "dirty flag".
     * http://www.knockmeout.net/2011/05/creating-smart-dirty-flag-in-knockoutjs.html
     */
    ko.dirtyFlag = function(root, isInitiallyDirty) {
        var result = function() {},
            _initialState = ko.observable(ko.toJSON(root)),
            _isInitiallyDirty = ko.observable(isInitiallyDirty);

        result.dirty = ko.computed(function() {
            return _isInitiallyDirty() || _initialState() !== ko.toJSON(root);
        }).extend({throttle: 500});

        result.reset = function() {
            _initialState(ko.toJSON(root));
            _isInitiallyDirty(false);
        };

        return result;
    };

    ko.applyBindings(new $.draughtcraft.recipes.builder.RecipeViewModel());

    // Apply a "fancybox" popup
    ko.bindingHandlers.popup = {
        init: function(el, v, accessor){
            if(el)
                $(el).fancybox({
                    'closeBtn'      : true,
                    'closeClick'    : true,
                    'maxWidth'      : 425,
                    'type'          : 'ajax',
                    'href'          : accessor().attr.href,
                    'helpers'       : {
                        'overlay' : {
                            'css' : {
                                'background' : 'rgba(0, 0, 0, 0.60)'
                            }
                        }
                    }
                });
        }
    };
    ko.bindingHandlers.titleUpdate = {
        update: function(el){
            var ns = $.draughtcraft.recipes.builder.recipe;
            document.title = 'DraughtCraft - ' + ns.name();
            if(ns.author())
                document.title += ' - ' + ns.author();
        }
    };
    ko.bindingHandlers.hasfocus['update'] = function(element, valueAccessor) {
        if (!element['__ko_hasfocusUpdating']) {
            var value = ko.utils.unwrapObservable(valueAccessor());
            value ? element.focus() : element.blur();
            if(value)
                $(element).select();
        }
    };

    // Make the recipe name grow as the user types
    $('h1 input').autogrow({
        'minWidth'      : 150,
        'maxWidth'      : 535,
        'comfortZone'   : 25
    });
});

(function($){

    $.fn.autogrow = function(o) {

        o = $.extend({
            maxWidth: 1000,
            minWidth: 0,
            comfortZone: 70
        }, o);

        this.filter('input:text').each(function(){

            var minWidth = o.minWidth || $(this).width(),
                val = '',
                input = $(this),
                testSubject = $('<tester/>').css({
                    position: 'absolute',
                    top: -9999,
                    left: -9999,
                    width: 'auto',
                    fontSize: input.css('fontSize'),
                    fontFamily: input.css('fontFamily'),
                    fontWeight: input.css('fontWeight'),
                    letterSpacing: input.css('letterSpacing'),
                    whiteSpace: 'nowrap'
                }),
                check = function() {

                    if (val === (val = input.val())) {return;}

                    // Enter new content into testSubject
                    var escaped = val.replace(/&/g, '&amp;').replace(/\s/g,'&nbsp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    testSubject.html(escaped);

                    // Calculate new width + whether to change
                    var testerWidth = testSubject.width(),
                        newWidth = (testerWidth + o.comfortZone) >= minWidth ? testerWidth + o.comfortZone : minWidth,
                        currentWidth = input.width(),
                        isValidWidthChange = (newWidth < currentWidth && newWidth >= minWidth)
                                             || (newWidth > minWidth && newWidth < o.maxWidth);

                    // Animate width
                    if (isValidWidthChange) {
                        input.width(newWidth);
                    }

                };

            testSubject.insertAfter(input);

            $(this).bind('keyup keydown blur update', check);
            check();

        });

        return this;

    };

})(jQuery);
