/*
 * Define a few namespaces
 */
if($.draughtcraft == undefined){
    $.draughtcraft = {};
    $.draughtcraft.profile = {};
    $.draughtcraft.recipes = {};
    $.draughtcraft.recipes.create = {};
    $.draughtcraft.recipes.browse = {};
    $.draughtcraft.recipes.builder = {};
    $.draughtcraft.recipes.viewer = {};
}

$.draughtcraft.apply_gravatar = function(){
    /*
     * Replace 404'd gravatars with a default image
     */
    $('img.gravatar').each(function(){
      var orig = $(this);
      var img = new Image();
      img.onerror = function(){
        var width = orig.attr('src').split('&s=')[1];
        orig.attr('src', '/images/glass-square.png');
        orig.attr('height', width);
      }
      img.src = orig.attr('src'); 
    });
};
$($.draughtcraft.apply_gravatar);

$(function(){
    /*
     * Fancybox popup for "About" links
     */
    $("a[href^='#about-box']").fancybox({
        'autoSize'          : false,
        'closeBtn'          : true,
        'closeClick'        : true,
        'width'             : 425,
        'height'            : 415
    });

    /*
     * Handle obfuscated mailto: links
     */
    $('a.email').click(function(e){
        e.preventDefault();
        var html = $(this).attr('rel');
        var reversed = html.split("").reverse().join("");
        window.location = 'mailto:'+reversed;
    });
});

/*
 * Lock out IE users.
 */
if($.browser.msie && window.location.pathname != '/browser')
    window.location = '/browser';

/*
 * Used to toggle US/metric units
 */
$.draughtcraft.toggleUnits = function(key, token){
    var data = {};
    data[key] = token;
    $.ajax({
        url: '/units',
        type: 'POST',
        cache: false,
        data: data,
        success: function(){
            window.location.reload();
        }
    });
};

/**
 * jQuery Cookie plugin
 *
 * Copyright (c) 2010 Klaus Hartl (stilbuero.de)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */
jQuery.cookie = function (key, value, options) {

    // key and at least value given, set cookie...
    if (arguments.length > 1 && String(value) !== "[object Object]") {
        options = jQuery.extend({}, options);

        if (value === null || value === undefined) {
            options.expires = -1;
        }

        if (typeof options.expires === 'number') {
            var days = options.expires, t = options.expires = new Date();
            t.setDate(t.getDate() + days);
        }

        value = String(value);

        return (document.cookie = [
            encodeURIComponent(key), '=',
            options.raw ? value : encodeURIComponent(value),
            options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
            options.path ? '; path=' + options.path : '',
            options.domain ? '; domain=' + options.domain : '',
            options.secure ? '; secure' : ''
        ].join(''));
    }

    // key and possibly options given, get cookie...
    options = value || {};
    var result, decode = options.raw ? function (s) { return s; } : decodeURIComponent;
    return (result = new RegExp('(?:^|; )' + encodeURIComponent(key) + '=([^;]*)').exec(document.cookie)) ? decode(result[1]) : null;
};

/**
 * @author Kyle Florence <kyle[dot]florence[at]gmail[dot]com>
 * @website https://github.com/kflorence/jquery-deserialize/
 * @version 1.1.0
 *
 * Dual licensed under the MIT and GPLv2 licenses.
 */

(function( jQuery ) {

var push = Array.prototype.push,
	rcheck = /^(radio|checkbox)$/i,
	rselect = /^(option|select-one|select-multiple)$/i,
	rvalue = /^(hidden|text|search|tel|url|email|password|datetime|date|month|week|time|datetime-local|number|range|color|submit|image|reset|button|textarea)$/i;

jQuery.fn.extend({
	deserialize: function( data, callback ) {
		if ( !this.length || !data ) {
			return this;
		}

		var i, length,
			elements = this[ 0 ].elements || this.find( ":input" ).get(),
			normalized = [];

		if ( !elements ) {
			return this;
		}

		if ( jQuery.isArray( data ) ) {
			normalized = data;
		} else if ( jQuery.isPlainObject( data ) ) {
			var key, value;

			for ( key in data ) {
				jQuery.isArray( value = data[ key ] ) ?
					push.apply( normalized, jQuery.map( value, function( v ) {
						return { name: key, value: v };
					})) : push.call( normalized, { name: key, value: value } );
			}
		} else if ( typeof data === "string" ) {
			var parts;

			data = decodeURIComponent( data ).split( "&" );

			for ( i = 0, length = data.length; i < length; i++ ) {
				parts = data[ i ].split( "=" );
				push.call( normalized, { name: parts[ 0 ], value: parts[ 1 ] } );
			}
		}

		if ( !( length = normalized.length ) ) {
			return this;
		}

		var current, element, item, j, len, property, type;

		for ( i = 0; i < length; i++ ) {
			current = normalized[ i ];

			if ( !( element = elements[ current.name ] ) ) {
				continue;
			}

			type = ( len = element.length ) ? element[ 0 ] : element;
			type = type.type || type.nodeName;
			property = null;

			if ( rvalue.test( type ) ) {
				property = "value";
			} else if ( rcheck.test( type ) ) {
				property = "checked";
			} else if ( rselect.test( type ) ) {
				property = "selected";
			}

			// Handle element group
			if ( len ) {
				for ( j = 0; j < len; j++ ) {
					item = element [ j ];

					if ( item.value == current.value ) {
						item[ property ] = true;
					}
				}
			} else {
				element[ property ] = current.value;
			}
		}

		if ( jQuery.isFunction( callback ) ) {
			callback.call( this );
		}

		return this;
	}
});

})( jQuery );
