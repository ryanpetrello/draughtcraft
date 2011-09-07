$.draughtcraft.recipes.browse.__injectRecipes__ = function(html){
    /*
     * Inject search results into the page.
     */
    $('#results').html(html);
    $.draughtcraft.recipes.browse.initPageCount();
    $.draughtcraft.recipes.browse.initColumnOrdering();
};

$.draughtcraft.recipes.browse.restoreLastFormValues = function(){
    /*
     * Load a cookie representing the "last form values", and reconfigure
     * the form to match.
     */
    var values = $.cookie('searchbar');
    if(values){
        $('#searchbar > form').deserialize(decodeURIComponent(values).replace(/\+/g, ' '));

        // Store the "last state" for on/off toggle buttons
        $('#searchbar > form li.btn input').each(function(){
            var li = $(this).closest('li');
            var enabled = $(this).val() == 'true';
            li.addClass(enabled ? 'enabled' : 'disabled');
            li.removeClass(enabled ? 'disabled' : 'enabled');
        });

        // Store the "last chosen value" for dropdowns
        $('#searchbar > form ul.primary > li input').each(function(){
            var value = $(this).val();
            var li = $(this).closest('li');
            var selected = li.find('ul.secondary li a[rel="'+value+'"]').closest('li');
            selected.addClass('selected');
            li.closest('ul.primary > li').children('span.placeholder').html(selected.html());
        });

    }
};

$.draughtcraft.recipes.browse.saveFormValues = function(){
    /*
     * Store the most recent form values in a cookie so that they're
     * automatically used on page load.
    */
    var values = $('#searchbar > form').serialize();
    $.cookie('searchbar', values, {expires: 7});
    $('#searchbar > form').submit();
};

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

    $.draughtcraft.recipes.browse.saveFormValues();
};

$.draughtcraft.recipes.browse.initMenuListeners = function(){

    /*
     * If any <a href="#"> is clicked on, silence the event.
     */
    $('#searchbar ul li a').click(function(e){ e.preventDefault(); });

    /*
     * If the user clicks on an on/off button, toggle it.
     */
    $('#searchbar ul.primary li.btn').click(function(){
        var enabled = $(this).hasClass('enabled');
        $(this).removeClass(enabled ? 'enabled' : 'disabled');
        $(this).addClass(enabled ? 'disabled' : 'enabled');

        // Reset to the first page of results
        $('#searchbar > form input[name="page"]').val(1);

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
        // Reset to the first page of results
        $('#searchbar > form input[name="page"]').val(1);

        $.draughtcraft.recipes.browse.prepareFormValues();
    });

    // When the search bar changes, save its value
    $('#searchbar .search input').change($.draughtcraft.recipes.browse.prepareFormValues);

};

$.draughtcraft.recipes.browse.initPageCount = function(){
    $('.pages a').click(function(e){
        e.preventDefault();
        $('#searchbar > form input[name="page"]').val($(this).text());
        $.draughtcraft.recipes.browse.saveFormValues();
    });
    $('.pages span.selected').each(function(){
        $('#searchbar > form input[name="page"]').val($(this).text());
    });
};

$.draughtcraft.recipes.browse.initColumnOrdering = function(){
    $('th a').click(function(e){
        e.preventDefault();
        $('#searchbar > form input[name="order_by"]').val($(this).closest('th').attr('rel'));
        if($(this).closest('th').hasClass('asc'))
            $('#searchbar > form input[name="direction"]').val('DESC');
        else if($(this).closest('th').hasClass('desc'))
            $('#searchbar > form input[name="direction"]').val('ASC');
        else
            $('#searchbar > form input[name="direction"]').val('ASC');
        $.draughtcraft.recipes.browse.saveFormValues();
    });

    $('th.asc, th.desc').each(function(){
        $('#searchbar > form input[name="order_by"]').val($(this).attr('rel'));
        if($(this).hasClass('asc'))
            $('#searchbar > form input[name="direction"]').val('ASC');
        if($(this).hasClass('desc'))
            $('#searchbar > form input[name="direction"]').val('DESC');
    });
};

$(document).ready(function(){
    $('#searchbar > form').ajaxForm({
        'success' : function(responseText){
            $.draughtcraft.recipes.browse.__injectRecipes__(responseText);
        }
    });

    $.draughtcraft.recipes.browse.restoreLastFormValues();
    $.draughtcraft.recipes.browse.initMenuListeners();
    $.draughtcraft.recipes.browse.prepareFormValues();

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
