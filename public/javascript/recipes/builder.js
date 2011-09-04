$.draughtcraft.recipes.builder._delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

$.draughtcraft.recipes.builder._first_focus = true;

/*
 * Used to fetch and redraw the current recipe via AJAX.
 */
$.draughtcraft.recipes.builder.fetchRecipe = function(){
    $.ajax({
        url: window.location.pathname+'/async/ingredients',
        cache: false,
        success: function(html){
            $.draughtcraft.recipes.builder.__injectRecipeContent__(html);
        }
    });
};

/*
 * After builder content is fetched, inject it into the appropriate
 * container.
 * @param {String} html - The HTML content to inject
 */
$.draughtcraft.recipes.builder.__injectRecipeContent__ = function(html){

    //
    // For performance reasons, we should clean up all previously 
    // rendered jQuery select widgets.
    //
    $(".step fieldset select").selectBox('destroy');

    //
    // Look for tr.addition in the DOM
    // and keep track of all unique DOM ID's.
    //
    var before = $.map($('tr.addition[id]'), function(x){
        return $(x).attr('id');
    });

    $("#builder-ajax").html(html);

    $.draughtcraft.recipes.builder.handleAnchor();

    //
    // Look for tr.additions that didn't exist *before* content injection.
    //
    var after = $.map($('tr.addition[id]'), function(x){
        return $(x).attr('id');
    });
    var difference = after.filter(function(i){
        return before.indexOf(i) < 0;
    });

    //
    // If a new row exists, focus on its first form element.
    //
    if($.draughtcraft.recipes.builder._first_focus)
        $.draughtcraft.recipes.builder._first_focus = false;
    else if(difference.length)
        $('#'+difference[0]).find('input, select').eq(0).focus();

    //
    // Visually stripe the recipe ingredients
    // 
    $('tr.addition').each(function(index){
        if(index % 2 == 0)
            $(this).addClass('even');
    });

    $.draughtcraft.recipes.builder.__afterRecipeInject();
};

/*
 * After recipe content is injected into the builder container, there are a
 * variety of listeners and state settings (e.g., current tab, last 
 * focused field) we need to persist.
 */
$.draughtcraft.recipes.builder.__afterRecipeInject = function(){

    // Re-initialize all event listeners
    $.draughtcraft.recipes.builder.initListeners();

    // Re-choose the "last chosen" tab
    $.draughtcraft.recipes.builder.selectTab(
        $.draughtcraft.recipes.builder.currentTab 
    );

    //
    // Initialize forms in the newly replaced DOM with Ajax versions
    // On successful Ajax submission, we inject the response body into
    // the DOM.
    //
    $('#builder form:not(.name)').ajaxForm({
        'success' : function(responseText){
            $.draughtcraft.recipes.builder._delay($.noop, 0);
            $.draughtcraft.recipes.builder.__injectRecipeContent__(responseText);
        },
        'error' : function(jqXHR, textStatus, errorThrown){
            $.draughtcraft.recipes.builder._delay($.noop, 0);
            $.draughtcraft.recipes.builder.__injectRecipeContent__(jqXHR.responseText);
        }
    });

    //
    // As the user is changing values, we're instantly pushing data to a
    // controller, and redrawing the editing UI again.
    //
    // If the user is moving between fields using tab or the mouse,
    // we might potentially overwrite the DOM element that they're
    // focused on, so we need to do our best to maintain the currently
    // focused field.
    //
    if($.draughtcraft.recipes.builder.lastFocus){
        var n = $.draughtcraft.recipes.builder.lastFocus;
        $('input#'+n+', select#'+n+', textarea#'+n).focus();
    }

    //
    // If error messages are embedded on the page,
    // pull them from the DOM and apply the error messages as "title"
    // attributes on the appropriate elements.
    //
    $('span.error-message').each(function(){
        $(this).prev('input, select, textarea').attr('title', $(this).html()+'.').tipTip({'delay': 200});
        $(this).remove();
    });

    $("#tiptip_holder").fadeOut();

    // Draw jQuery-powered replacements for native <select>'s.
    $(".step fieldset select").selectBox({
        'menuTransition'    : 'fade',
        'menuSpeed'         : 'fast'
    });

    // Register fancybox popups for ingredient links
    $("a[href^='/ingredients/']").fancybox();

    // Hide unnecessary verbiage helpers
    $('h3 span.step-help').remove();
};

$.draughtcraft.recipes.builder.currentTab = 0;
/*
 * Initializes listeners for the "tabs" (e.g.,
 * Mash, Boil, Ferment...)
 */
$.draughtcraft.recipes.builder.initTabs = function(){
    $('.step h2 li a').click(function(e){
        // Determine the index of the chosen tab
        var index = $('.step.active h2 li a').index(this);

        // Actually choose the tab
        $.draughtcraft.recipes.builder.selectTab(index);
    });
};

// The DOM ID of the last focused form field
$.draughtcraft.recipes.builder.lastFocus;

/*
 * Initialize event listeners for input field focus/blur
 * so that we can keep track of the "last focused field".
 */
$.draughtcraft.recipes.builder.initFocusListeners = function(){
    // When a field gains focus, store its id.
    var fields = $('input, select, textarea'); 
    fields.focus(function(){
        $.draughtcraft.recipes.builder.lastFocus = $(this).attr('id');
    });
    // When a field loses focus, unset its id.
    fields.blur(function(){
        if($(this).attr('id') && $.draughtcraft.recipes.builder.lastFocus == $(this).attr('id'))
            $.draughtcraft.recipes.builder.lastFocus = null;
    });
};

/*
 * Initializes event listeners for input field changes
 * for recipe components.
 */
$.draughtcraft.recipes.builder.initUpdateListeners = function(){

    //
    // For each text input, monitor the keyup event.
    //
    // If more than 2s passes since the last keyup, submit the changed
    // form value asynchronously.
    //
    var save = function(){
        // Stop listening for mouse movements...
        $('body').unbind('mousemove');

        // Clear any previously queued form submissions
        $.draughtcraft.recipes.builder._delay($.noop, 0);
        
        // Remove any input field `blur` listeners
        $(this).unbind('blur');

        // Find the closest form to submit
        var form = $(this).closest('form');

        // Actually submit the form.
        form.submit();

        //
        // Find any adjacent input fields (for the form) and temporarily
        // disable them (disallow edits while saving) for the duration
        // of the Ajax save.
        //
        $(form).find('input, select').attr('disabled', 'disabled');
    };

    // Any time an <input> or <textarea> triggers a `keyup`...
    $('.step input, .step textarea, .results textarea').keyup(function(e){
        // Ignore Tab or Shift-Tab keypresses...
        if(e.keyCode == 9 || e.keyCode == 16) return;

        // Start a timer to auto-save 2 seconds from now.
        $.draughtcraft.recipes.builder._delay($.proxy(save, this), 2000);

        //
        // Listen for any mouse movement. If movement occurs, go ahead and save.
        // This usually signals that the user is moving their mouse to add
        // another ingredient or change some setting.
        //
        $('body').mousemove($.proxy(function(){
            // Stop listening for mouse movements...
            $('body').unbind('mousemove');
            $.draughtcraft.recipes.builder._delay($.proxy(save, this), 0);
        }, this));

        //
        // If the object loses keyboard focus early (generally via the tab key),
        // submit the form
        //
        $(this).blur($.proxy(function(){
            $.draughtcraft.recipes.builder._delay($.proxy(save, this), 0);
        }, this));
        
    });

    // Any time a <select>'s value changes, save immediately.
    $('.step select').change(save);
};

/*
 * To enhance user experience, we should automatically
 * add sequentual `tabindex` attributes to the ingredient
 * editing fields.  This will make it so that users can
 * easily tab through form fields as they're live-editing.
 */
$.draughtcraft.recipes.builder.initTabIndexes = function(){

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
$.draughtcraft.recipes.builder.initListeners = function(){
    $.draughtcraft.recipes.builder.initTabs();
    $.draughtcraft.recipes.builder.initTabIndexes();
    $.draughtcraft.recipes.builder.initUpdateListeners();
    $.draughtcraft.recipes.builder.initFocusListeners();
};

/*
 * Used to remove an addition/ingredient from a recipe.
 * @param {Integer} model.RecipeAddition.id
 */
$.draughtcraft.recipes.builder.removeAddition = function(addition){
    if(confirm('Are you sure you want to remove this?'))
        $.ajax({
            url: window.location.pathname+'/async/ingredients/'+addition,
            type: 'DELETE',
            cache: false,
            success: function(html){
                $.draughtcraft.recipes.builder.__injectRecipeContent__(html);
            }
        });
};

/*
 * Chooses and displays a specific tab/section.
 * @param {Integer} index
 */
$.draughtcraft.recipes.builder.selectTab = function(index){
    // Hide all steps
    $('.step').removeClass('active');

    // Display the step at the correct index
    $('.step').eq(index).addClass('active');

    // Store the "current" step index for reference
    $.draughtcraft.recipes.builder.currentTab = index;

    // Force the sidebar to scroll down with the page
    $('.inventory:visible').scrollToFixed({ marginTop: 10 });

    // Safari bug: force the browser window to repaint by quickly scrolling
    var pos = $('body').scrollTop();
    window.scrollTo(0, pos+1);
    window.scrollTo(0, pos);
}; 

/*
 * Render jQuery replacements for recipe-level settings,
 * and listen on form submissions.
 */
$.draughtcraft.recipes.builder.initRecipeSettings = function(){
    // Draw jQuery-powered replacements for native <select>'s.
    $("#builder fieldset select").selectBox({
        'menuTransition'    : 'fade',
        'menuSpeed'         : 'fast'
    });
    // For each setting, monitor changes and submit the containing form
    $('#builder fieldset select').change(function(){
        var form = $(this).closest('form');
        form.submit();
    });
};

/*
 * If a specific step is specified in the page anchor
 * (e.g., #mash, #boil), select the appropriate tab.
 */
$.draughtcraft.recipes.builder.handleAnchor = function(){
    var anchor = window.location.hash;
    if(anchor){
        var tab = $('li.active a[href$='+anchor+']').closest('.step');
        $.draughtcraft.recipes.builder.selectTab($('.step').index(tab));
    }
};

/*
 * Register tooltip listeners on the name field, and cause it to autogrow
 * as text is added and removed.
 */
$.draughtcraft.recipes.builder.handleNameField = function(){
    var msg = 'Click here to edit the recipe name.';
    $('h1').tipTip({
        'delay'     : 50,
        'content'   : msg
    });
    $('h1 input').focus(function(){
        $('h1').tipTip('hide').tipTip('destroy');
    }).blur(function(){
        $('h1').tipTip({
            'delay'     : 50,
            'content'   : msg
        })
    }).autogrow({
        'minWidth'      : 150,
        'maxWidth'      : 535,
        'comfortZone'   : 25
    }).change(function(){
        $(this).closest('form').submit();   
    });

    /*
     * When the name field is changed, submit its containing form via ajax.
     */
    $('#builder div.header > form.name').ajaxForm();
};

(function($){

    $.fn.autogrow = function(o) {

        o = $.extend({
            maxWidth: 1000,
            minWidth: 0,
            comfortZone: 70
        }, o);

        this.filter('input:text').each(function(){

            var minWidth = o.minWidth || $(this).width(),
                val = '',
                input = $(this),
                testSubject = $('<tester/>').css({
                    position: 'absolute',
                    top: -9999,
                    left: -9999,
                    width: 'auto',
                    fontSize: input.css('fontSize'),
                    fontFamily: input.css('fontFamily'),
                    fontWeight: input.css('fontWeight'),
                    letterSpacing: input.css('letterSpacing'),
                    whiteSpace: 'nowrap'
                }),
                check = function() {

                    if (val === (val = input.val())) {return;}

                    // Enter new content into testSubject
                    var escaped = val.replace(/&/g, '&amp;').replace(/\s/g,'&nbsp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                    testSubject.html(escaped);

                    // Calculate new width + whether to change
                    var testerWidth = testSubject.width(),
                        newWidth = (testerWidth + o.comfortZone) >= minWidth ? testerWidth + o.comfortZone : minWidth,
                        currentWidth = input.width(),
                        isValidWidthChange = (newWidth < currentWidth && newWidth >= minWidth)
                                             || (newWidth > minWidth && newWidth < o.maxWidth);

                    // Animate width
                    if (isValidWidthChange) {
                        input.width(newWidth);
                    }

                };

            testSubject.insertAfter(input);

            $(this).bind('keyup keydown blur update', check);
            check();

        });

        return this;

    };

})(jQuery);

$(document).ready(function(){
    $.draughtcraft.recipes.builder.initRecipeSettings();
    $.draughtcraft.recipes.builder.fetchRecipe();
    $.draughtcraft.recipes.builder.handleNameField();

    // Register a JS tooltip on the author's thumbnail (if there is one).
    $('img.gravatar').tipTip({'delay': 50});
});
