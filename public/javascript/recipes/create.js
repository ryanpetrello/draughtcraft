/*
 * When the recipe name field is clicked on, empty its (default) contents.
 */
$.draughtcraft.recipes.create.initFormListeners = function(){
    $('input[name="name"].default').focus(function(){
        $(this).removeClass('default').val('').unbind('focus');
    }).change(function(){
        $(this).removeClass('error')   
    });

    // Before submitting the creation form, remove the default value.
    // This will prevent people from mistakenly making a recipe with the
    // default placeholder name text.
    $('form').submit(function(){
        $('input[name="name"].default').val('');
    });
};

$(document).ready(function(){
    $.draughtcraft.recipes.create.initFormListeners();
    $("a.question").fancybox({
        'autoSize'          : false,
        'width'             : 600,
        'height'            : 425,
        'helpers'           : {
            'overlay' : {
                'css' : {
                    'background' : 'rgba(0, 0, 0, 0.60)'
                }
            }
        }
    });
});
