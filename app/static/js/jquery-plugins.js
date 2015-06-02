/**
 * Returns true if this elements bottom y axis
 * is less than or equal to the given element's top y axis - maxRange.
 *
 * @param element - string selector
 * @param maxRange - max range to check if the object is above
 *                   Default = 0
 * @returns {boolean}
 */
$.fn.isAbove = function (element, maxRange) {
    maxRange = maxRange || 0;
    var eTop = $(element).offset().top;
    // this elements bottom y coordinate
    var bottom = this.offset().top + this.outerHeight();
    return  eTop - maxRange <= bottom;
};


$.fn.visible = function() {
    return this.css('visibility', 'visible');
};

$.fn.invisible = function() {
    return this.css('visibility', 'hidden');
};

$.fn.visibilityToggle = function() {
    return this.css('visibility', function(i, visibility) {
        return (visibility == 'visible') ? 'hidden' : 'visible';
    });
};