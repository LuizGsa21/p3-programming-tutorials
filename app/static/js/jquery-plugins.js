$.fn.isAbove = function (element) {
    var eTop = element.getBoundingClientRect().top;
    // this elements bottom y coordinate
    var bottom = this[0].getBoundingClientRect().bottom;
    return  eTop <= bottom;
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