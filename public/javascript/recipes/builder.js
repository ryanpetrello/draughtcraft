$.beerparts.recipes.builder.fetchRecipe = function(){
    $.ajax({
        url: window.location.pathname+'/async',
        cache: false,
        success: function(html){
            $("#builder").html(html)
            $.beerparts.recipes.builder.initListeners()
            $.Cufon();
        }
    });
};

$.beerparts.recipes.builder.initTabs = function(){
    $('.step h2 li a').click(function(e){

        // Determine the index of the chosen tab
        var index = $('.step.active h2 li a').index(this);
        
        // Hide all steps
        $('.step').removeClass('active');

        // Display the step at the correct index
        $('.step').eq(index).addClass('active');

        // Prevent the default <a href> behavior
        e.preventDefault();
    });
};

$.beerparts.recipes.builder.initListeners = function(){
    $.beerparts.recipes.builder.initTabs();
};

$(document).ready(function(){
    $.beerparts.recipes.builder.fetchRecipe();
});
