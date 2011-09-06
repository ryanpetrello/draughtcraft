$.draughtcraft.recipes.browse.prepareFormValues = function(){
    /*
     * Used to duplicate the current state of the search bar settings
     * to the underlying form fields.
     */

    // For each "toggle" button...
    $('#searchbar ul.primary li.btn').each(function(){
        // Store true/false in the hidden input field
        $(this).children('input').val($(this).hasClass('enabled'));
    });

    // For each "dropdown"
    $('#searchbar ul.secondary li.selected a').each(function(){
        // Store the value in the hidden input field
        $(this).closest('ul.primary > li').children('input').val($(this).attr('rel'));
    });

};

$.draughtcraft.recipes.browse.initMenuListeners = function(){

    /*
     * If the user clicks on an on/off button, toggle it.
     */
    $('#searchbar ul.primary li.btn').click(function(){
        var enabled = $(this).hasClass('enabled');
        $(this).removeClass(enabled ? 'enabled' : 'disabled');
        $(this).addClass(enabled ? 'disabled' : 'enabled');

        $.draughtcraft.recipes.browse.prepareFormValues();
    });

    /*
     * Initializes the "search bar" dropdowns for style, srm, etc...
     */
    $('#searchbar ul.primary > li').click(function(){
        var li = this;
        $('ul.secondary').filter(function(){
            return $(this).closest('li')[0] != li;
        }).removeClass('visible'); 
        $(li).children('ul.secondary').toggleClass('visible'); 
    });

    /*
     * If the user clicks anywhere other than the primary/secondary menu,
     * hide the submenu.
     */
    $("body").click(function(e){
        var parents = $(e.target).closest('ul.primary').length;
        if(!parents)
            $('ul.secondary').removeClass('visible');
    });

    /*
     * If `escape` is pressed, hide all secondary menus.
     */
    $(document).keyup(function(e) {
        if(e.keyCode == 27){ // ESC
            $('ul.secondary').removeClass('visible');
        }
    });

    // When a secondary menu option is chosen, mark it as `selected`.
    $('#searchbar ul.secondary li').click(function(){
        $(this).siblings('li').removeClass('selected');
        $(this).addClass('selected');

        $(this).closest('ul.primary > li').children('span.placeholder').html(
            $(this).html()
        );
        $.draughtcraft.recipes.browse.prepareFormValues();
    });

};

$(document).ready(function(){
    $.draughtcraft.recipes.browse.initMenuListeners();

    $('ul.primary li ul.secondary img.glass').each(function(){
        $(this).closest('li').tipTip({
            'content'           : $(this).attr('title'),
            'offset'            : 0,
            'defaultPosition'   : 'right', 
            'delay'             : 25,
            'cssClass'          : 'srmTip'
        });
    });

    $.draughtcraft.recipes.browse.prepareFormValues();

});
