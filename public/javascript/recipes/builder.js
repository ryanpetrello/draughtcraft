$.beerparts.recipes.builder.renderRecipe = function(){
    $.ajax({
        url: window.location.pathname+'/async',
        cache: false,
        success: function(html){
            $("#builder").html(html)
            $('select').selectBox({
                'menuTransition': 'fade'
            }).change($.Cufon);
            $.Cufon();
        }
    });
};

$(document).ready(function(){
    $.beerparts.recipes.builder.renderRecipe();
});
