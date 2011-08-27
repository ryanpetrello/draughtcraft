/*
 * Used to fetch and redraw the current recipe via AJAX.
 */
$.draughtcraft.recipes.viewer.fetchRecipe = function(){
    $('form#async').ajaxForm({
        success: function(html){
            $.draughtcraft.recipes.viewer.__injectRecipeContent__(html);
        }
    }).submit();
};

/*
 * After content is fetched, inject it into the appropriate
 * container.
 * @param {String} html - The HTML content to inject
 */
$.draughtcraft.recipes.viewer.__injectRecipeContent__ = function(html){
    $("#builder-ajax").html(html);

    //
    // Visually stripe the recipe ingredients
    // 
    $('tr.addition').each(function(index){
        if(index % 2 == 0)
            $(this).addClass('even');
    });

    // Replace all fields with static <span>'s
    $('#builder input:visible, #builder textarea').replaceWith(function(){
        return '<span>'+$(this).val()+'</span>';
    });
    $('#builder select').replaceWith(function(){
        return '<span>'+$(this).find('option:selected').text()+'</span>';
    });

    // Remove editing components from the DOM
    $('td.close img, img.close, li.add-step').remove();
    $('#builder form').attr('method', 'GET').removeAttr('action');
};

$(document).ready(function(){
    $.draughtcraft.recipes.viewer.fetchRecipe();

    // Replace all fields with static <span>'s
    $('#builder input:visible, #builder textarea').replaceWith(function(){
        return '<span>'+$(this).val()+'</span>';
    });
    $('#builder select').replaceWith(function(){
        return '<span>'+$(this).find('option:selected').text()+'</span>';
    });

    // Register a JS tooltip on the author's thumbnail (if there is one).
    $('img.gravatar').tipTip({'delay': 50});
});
