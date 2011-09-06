$.draughtcraft.recipes.browse.initMenuBars = function(){

    /*
     * If the user clicks on an on/off button, toggle it.
     */
    $('#searchbar ul.primary li.btn').click(function(){
        var enabled = $(this).hasClass('enabled');
        $(this).removeClass(enabled ? 'enabled' : 'disabled');
        $(this).addClass(enabled ? 'disabled' : 'enabled');
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

};

$(document).ready(function(){
    $.draughtcraft.recipes.browse.initMenuBars();

    $('ul.primary li ul.secondary img.glass').each(function(){
        $(this).closest('li').tipTip({
            'content'           : $(this).attr('title'),
            'offset'            : 0,
            'defaultPosition'   : 'right', 
            'delay'             : 25,
            'cssClass'          : 'srmTip'
        });
    });
});
