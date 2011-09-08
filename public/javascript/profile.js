$.draughtcraft.profile.initToolTips = function(){
    // Register a JS tooltip on recipe SRM images
    $('.recipe .srm').each(function(){
        $(this).tipTip({'delay': 50});
    })
    // Register a JS tooltip on recipe view counts
    $('.recipe ul.badge li').each(function(){
        $(this).tipTip({
            'delay': 0, 
            'defaultPosition': 'top', 
            'edgeOffset': -5
        });
    })
};

$.draughtcraft.profile.initRecipeButtons = function(){
    // Register submit events on form submission buttons
    $('.recipe a.submit, .recipe li.submit').click(function(e){
        e.preventDefault();
        if($(this).hasClass('confirm') && !confirm("Are you sure you want to delete this recipe?  This can't be reversed!"))
            return;
        $(this).closest('form').submit();
    });
};

$(document).ready(function(){
    $.draughtcraft.profile.initToolTips();
    $.draughtcraft.profile.initRecipeButtons();
});
