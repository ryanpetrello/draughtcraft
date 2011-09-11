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
    $('#builder input:visible').replaceWith(function(){
        return '<span>'+$(this).val()+'</span>';
    });
    $('#builder textarea').replaceWith(function(){
        return '<span>'+$(this).val().split("\n").join("<br />")+'</span>';
    });
    // Hide empty text areas
    $('#builder textarea:empty').remove();
    $('#builder select').replaceWith(function(){
        return '<span>'+$(this).find('option:selected').text()+'</span>';
    });

    // Remove editing components from the DOM
    $('td.close img, img.close, li.add-step').remove();
    $('#inventories form, #builder form').filter(function(){
        return !$(this).parents('div#actions').length;
    }).attr('method', 'GET').removeAttr('action');

    // Cause the recipe actions (print, copy, etc...) to move down the page.
    $('div#actions').scrollToFixed({ marginTop: 10 });

    // Register tooltips for the recipe actions
    $('div#actions li').each(function(){
        $(this).tipTip({
            'delay'     : 25,
            'edgeOffset': 20
        });
    });

    // Register click listeners for the recipe actions
    $('div#actions li.submit').click(function(e){
        $(this).closest('form').submit();
    });
    
    // Register fancybox popups for ingredient links
    $("a[href^='/ingredients/']").fancybox();
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
