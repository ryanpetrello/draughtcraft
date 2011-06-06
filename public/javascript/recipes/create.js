/*
 * When the recipe name field is clicked on, empty its (default) contents.
 */
$.draughtcraft.recipes.create.initFormListeners = function(){
    $('input[name="name"].default').change(function(){
        $(this).removeClass('default').val('').unbind();
    }).focus();
};

$(document).ready(function(){
    $.draughtcraft.recipes.create.initFormListeners();
});
