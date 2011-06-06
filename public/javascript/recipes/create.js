/*
 * When the recipe name field is clicked on, empty its (default) contents.
 */
$.draughtcraft.recipes.create.initFormListeners = function(){
    $('input[name="name"].default').focus(function(){
        $(this).removeClass('default').val('').unbind();
    });
};

$(document).ready(function(){
    $.draughtcraft.recipes.create.initFormListeners();
});
