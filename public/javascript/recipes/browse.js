$.draughtcraft.recipes.browse.initMenuBars = function(){
    /*
     * Initializes the "search bar" dropdowns for style, srm, etc...
     */
    $('#searchbar ul.primary li').click(function(){
        $(this).children('ul.secondary').addClass('visible'); 
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

};

$(document).ready(function(){
    $.draughtcraft.recipes.browse.initMenuBars();
});
