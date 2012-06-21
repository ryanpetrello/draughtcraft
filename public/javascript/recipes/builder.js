(function(n, $){

    n.recipes = n.recipes || {}, n.recipes.builder = n.recipes.builder || {};
    ns = n.recipes.builder;

    ns.Recipe = function(){
        this.name = ko.observable();
        this.volume = ko.observable();
        this.style = ko.observable();
    };

    ns.RecipeViewModel = function(){
        ns.recipe = this.recipe = new ns.Recipe();

        this.styles = ko.observableArray([]);

        ($.proxy(function(){
            // Fetch recipe data via AJAX
            this.styles.push({id: null, name: 'No Target Style Chosen'});
            this.styles.push({id: 34, name: 'American Amber Ale'});
            this.styles.push({id: 55, name: 'Witbier'});

            this.recipe.name("Summer's End");
            this.recipe.volume(5);
            this.recipe.style(55);
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
