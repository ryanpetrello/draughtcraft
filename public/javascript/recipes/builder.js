$.beerparts.recipes.builder.renderRecipe = function(){
    $.ajax({
        url: '/recipes/builder/async',
        cache: false,
        success: function(html){
            $("#builder").html(html)
            $.Cufon();
        }
    });
};

$(document).ready(function(){
    $.beerparts.recipes.builder.renderRecipe();
});
