(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;
    ns.model = ns.model || {};

    ns.model.RecipeAddition = function(){

        var writeTimeoutInstance = null;

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

    };

    ns.model.Recipe = function(){
        this.name = ko.observable();
        this.volume = ko.observable();
        this.style = ko.observable();

        this.mash = new ns.model.RecipeStep();
        this.boil = new ns.model.RecipeStep();
        this.fermentation = new ns.model.RecipeStep();

        this.boil_minutes = ko.observable();

        // Inventory
        this.inventory = ko.observableArray();
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

                    // Render select boxes
                    $("#header select, .inventory select").selectBox({
                        'menuTransition'    : 'fade',
                        'menuSpeed'         : 'fast'
                    });

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
