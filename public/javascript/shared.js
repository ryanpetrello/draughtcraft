/*
 * Define a few namespaces
 */
if($.beerparts == undefined){
    $.beerparts = {};
    $.beerparts.recipes = {};
    $.beerparts.recipes.builder = {};
}

/*
 * Load custom fonts
 */
WebFont.load({
    custom: {
        families: ['CabinSketch'],
        urls: ['/css/type/chalk.css']
    }
});
