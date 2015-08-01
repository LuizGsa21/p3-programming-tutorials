define(['jquery', 'bootstrap'], function ($) {
	// Save the original plugin
	var oldPlugin = $.fn.popover;
	// Add the option to invoke a callback after the popover is hidden.
	$.fn.popover = function Plugin(option, callback) {
		return this.each(function () {
			var $this = $(this);
			var data = $this.data('bs.popover');
			var options = typeof option == 'object' && option;
			if (!data && /destroy|hide/.test(option)) return;
			if (!data) $this.data('bs.popover', (data = new oldPlugin.Constructor(this, options)));
			if (typeof option == 'string') {
				// add a callback option when hiding popovers
				(callback && option == 'hide') ? data[option](callback) : data[option]()
			}
		})
	};
});