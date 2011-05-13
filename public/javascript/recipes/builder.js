/*
 * Used to fetch and redraw the current recipe via AJAX.
 */
$.beerparts.recipes.builder.fetchRecipe = function(){
    $.ajax({
        url: window.location.pathname+'/async',
        cache: false,
        success: function(html){
            // Inject the response from the async call
            $("#builder").html(html);

            $.beerparts.recipes.builder.__afterRecipeFetch__();
        }
    })
};

/*
 * After a recipe is fetched and the builder container is replaced
 * with new content, there are a variety of listeners and state
 * settings (e.g., current tab, last focused field) we need to persist.
 */
$.beerparts.recipes.builder.__afterRecipeFetch__ = function(){

    // Re-initialize all event listeners
    $.beerparts.recipes.builder.initListeners();

    // Re-choose the "last chosen" tab
    $.beerparts.recipes.builder.selectTab(
        $.beerparts.recipes.builder.currentTab 
    );
    
    //
    // Initialize forms in the newly replaced DOM with Ajax versions
    // On successful Ajax submissions, we should fetch and re-draw
    // the recipe.
    //
    $('#builder form').ajaxForm($.beerparts.recipes.builder.fetchRecipe);

    //
    // As the user is changing values, we're instantly pushing data to a
    // controller, and redrawing the editing UI again.
    //
    // If the user is moving between fields using tab or the mouse,
    // we might potentially overwrite the DOM element that they're
    // focused on, so we need to do our best to maintain the currently
    // focused field.
    //
    if($.beerparts.recipes.builder.lastFocus){
        var n = $.beerparts.recipes.builder.lastFocus;
        $('input[name="'+n+'"], select[name="'+n+'"]').focus();
    }
    
};

$.beerparts.recipes.builder.currentTab = 0;
/*
 * Initializes listeners for the "tabs" (e.g.,
 * Mash, Boil, Ferment...)
 */
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

// The DOM name of the last focused form field
$.beerparts.recipes.builder.lastFocus;

/*
 * Initialize event listeners for input field focus/blur
 * so that we can keep track of the "last focused field".
 */
$.beerparts.recipes.builder.initFocusListeners = function(){
    // When a field gains focus, store its name.
    var fields = $('.step tr.addition input, .step tr.addition select'); 
    fields.focus(function(){
        $.beerparts.recipes.builder.lastFocus = $(this).attr('name');
    });
    // When a field loses focus, unset its name.
    fields.blur(function(){
        if($(this).attr('name') && $.beerparts.recipes.builder.lastFocus == $(this).attr('name'))
            $.beerparts.recipes.builder.lastFocus = null;
    });
};

/*
 * Initializes event listeners for input field changes
 * for recipe components.
 */
$.beerparts.recipes.builder.initUpdateListeners = function(){
    // For each input field, monitor changes...
    $('.step tr.addition input, .step tr.addition select').change(function(){
        // When a change occurs: 
        // 1. Find any adjacent input fields (for the row) and temporarily
        //    disable them (disallow edits while saving).

        var row = $(this).closest('tr');
        $(row).find('input, select').attr('disabled', 'disabled');

        // 2. Find the containing <form> and submit it asynchronously.

        var form = $(this).closest('form');
        form.submit();

    });
};

/*
 * To enhance user experience, we should automatically
 * add sequentual `tabindex` attributes to the ingredient
 * editing fields.  This will make it so that users can
 * easily tab through form fields as they're live-editing.
 */
$.beerparts.recipes.builder.initTabIndexes = function(){

    $('.step input, .step select').each(function(index){
        $(this).attr('tabindex', index);
    });

    //
    // Links should have the lowest possible tab precedence - while
    // you're tabbing through the ingredient editing form,
    // we don't want to stop on links to ingredients, but instead
    // want to move easily from field to field.
    //
    $('.step tr.addition a').attr('tabindex', "9999");
};

/*
 * Initializes all event listeners
 */
$.beerparts.recipes.builder.initListeners = function(){
    $.beerparts.recipes.builder.initTabs();
    $.beerparts.recipes.builder.initTabIndexes();
    $.beerparts.recipes.builder.initUpdateListeners();
    $.beerparts.recipes.builder.initFocusListeners();
};

/*
 * Chooses and displays a specific tab/section.
 * @param {Integer} index
 */
$.beerparts.recipes.builder.selectTab = function(index){
    // Hide all steps
    $('.step').removeClass('active');

    // Display the step at the correct index
    $('.step').eq(index).addClass('active');

    // Store the "current" step index for reference
    $.beerparts.recipes.builder.currentTab = index;
}; 

$(document).ready(function(){
    $.beerparts.recipes.builder.fetchRecipe();
});
