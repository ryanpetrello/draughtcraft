(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;

    ns.RecipeAddition = function(){
        this.amount = ko.observable();
        this.unit = ko.observable();
        this.use = ko.observable();
        this.minutes = ko.observable();

        this.form = ko.observable();
        this.alpha_acid = ko.observable();

        this.ingredient = ko.observable();
    };

    ns.RecipeStep = function(){
        this.additions = ko.observableArray();

        this.fermentables = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient().class == 'Fermentable';
            });
        }, this);

        this.hops = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient().class == 'Hop';
            });
        }, this);

        this.yeast = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient().class == 'Yeast';
            });
        }, this);

        this.extras = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient().class == 'Extra';
            });
        }, this);

    };

    ns.Recipe = function(){
        this.name = ko.observable();
        this.volume = ko.observable();
        this.style = ko.observable();

        this.mash = new ns.RecipeStep();
        this.boil = new ns.RecipeStep();
        this.fermentation = new ns.RecipeStep();

        this.boil_minutes = new ko.observable();
    };

    ns.RecipeViewModel = function(){
        ns.recipe = this.recipe = new ns.Recipe();

        this.styles = ns.STYLES;
        this.hop_forms = [
            {'id': 'LEAF', 'name': 'Leaf'},
            {'id': 'PELLET', 'name': 'Pellet'},
            {'id': 'PLUG', 'name': 'Plug'},
        ];

        this.boil_times = $.proxy(function(){
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

        var show = function(){
            // Display the UI after data has been fetched via AJAX.
            $('.builder-loading').hide();
            $('.step').addClass('active');
        };

        ($.proxy(function(){
            // Fetch recipe data via AJAX and render the UI
            $.getJSON(
                window.location.toString()+'index.json',
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
                            var a = new ns.RecipeAddition();
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

                }, this))
            );

        }, this))();
    };

})($.draughtcraft = $.draughtcraft || {}, $);

$(function(){
    ko.applyBindings(new $.draughtcraft.recipes.builder.RecipeViewModel());
    // Register a JS tooltip on the author's thumbnail (if there is one).
    $('img.gravatar').tipTip({'delay': 50});
});

// Disabling Safari's annoying form warning - the builder auto-saves for you.
window.onbeforeunload=function(e){};
