$.beerparts.recipes.builder.fetchRecipe = function(){
    $.ajax({
        url: window.location.pathname+'/async',
        cache: false,
        success: function(html){
            // Inject the response from the async call
            $("#builder").html(html);

            // Re-initialize event listeners
            $.beerparts.recipes.builder.initListeners();

            // Choose the "last" tab
            $.beerparts.recipes.builder.selectTab(
                $.beerparts.recipes.builder.currentTab 
            );
        }
    });
};

$.beerparts.recipes.builder.currentTab = 0;
$.beerparts.recipes.builder.initTabs = function(){
    $('.step h2 li a').click(function(e){

        // Determine the index of the chosen tab
        var index = $('.step.active h2 li a').index(this);

        // Actually choose the tab
        $.beerparts.recipes.builder.selectTab(index);

        // Prevent the default <a href> behavior
        e.preventDefault();
    });
};

$.beerparts.recipes.builder.selectTab = function(index){
    // Hide all steps
    $('.step').removeClass('active');

    // Display the step at the correct index
    $('.step').eq(index).addClass('active');

    // Store the "current" step index for reference
    $.beerparts.recipes.builder.currentTab = index;
}; 

$.beerparts.recipes.builder.initListeners = function(){
    $.beerparts.recipes.builder.initTabs();
};

$(document).ready(function(){
    $.beerparts.recipes.builder.fetchRecipe();
});
