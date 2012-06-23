(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;

    ns.RecipeStep = function(){
        this.additions = ko.observableArray();

        this.fermentables = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient.class == 'Fermentable';
            });
        }, this);

        this.hops = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient.class == 'Hop';
            });
        }, this);

        this.yeast = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient.class == 'Yeast';
            });
        }, this);

        this.extras = ko.computed(function() {
            return ko.utils.arrayFilter(this.additions(), function(item) {
                return item.ingredient.class == 'Extra';
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
    };

    ns.RecipeViewModel = function(){
        ns.recipe = this.recipe = new ns.Recipe();

        this.styles = ns.STYLES;
        this.hop_forms = [
            {'id': 'LEAF', 'name': 'Leaf'},
            {'id': 'PELLET', 'name': 'Pellet'},
            {'id': 'PLUG', 'name': 'Plug'},
        ];

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

                    // Recipe additions
                    this.recipe.mash.additions(
                        pop(data, 'mash')
                    );
                    this.recipe.boil.additions(
                        pop(data, 'boil')
                    );
                    this.recipe.fermentation.additions(
                        pop(data, 'fermentation')
                    );

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
