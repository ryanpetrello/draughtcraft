$.draughtcraft.profile.initToolTips = function(){
    // Register a JS tooltip on recipe SRM images
    $('.recipe .srm').each(function(){
        $(this).tipTip({'delay': 50});
    })
    // Register a JS tooltip on recipe view counts
    $('.recipe ul.badge li').each(function(){
        $(this).tipTip({'delay': 50});
    })
};

$(document).ready(function(){
    $.draughtcraft.profile.initToolTips();
    $.draughtcraft.profile.initRecipeButtons();
});
