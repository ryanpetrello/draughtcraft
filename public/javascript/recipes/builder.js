(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;

    ns.Recipe = function(){
        this.name = ko.observable();
        this.volume = ko.observable();
        this.style = ko.observable();

        this.mash = ko.observableArray();
        this.boil = ko.observableArray();
        this.fermentation = ko.observableArray();
    };

    ns.RecipeViewModel = function(){
        ns.recipe = this.recipe = new ns.Recipe();

        this.styles = ns.STYLES;

        ($.proxy(function(){
            // Fetch recipe data via AJAX
            $.getJSON(
                window.location.toString()+'index.json',
                ($.proxy(function(data){
                    var data = data['recipe'];

                    var pop = function(obj, key){
                        var v = obj[key];
                        if(v)
                            delete obj[key]
                        return v;
                    };

                    // Recipe additions
                    this.recipe.mash(pop(data, 'mash'));
                    this.recipe.boil(pop(data, 'boil'));
                    this.recipe.fermentation(pop(data, 'fermentation'));

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
    //
    // Register a JS tooltip on the author's thumbnail (if there is one).
    $('img.gravatar').tipTip({'delay': 50});
});

// Disabling Safari's annoying form warning - the builder auto-saves for you.
window.onbeforeunload=function(e){};
