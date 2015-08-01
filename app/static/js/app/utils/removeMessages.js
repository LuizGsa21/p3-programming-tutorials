define(['jquery', 'lib/bootstrap-custom-popover'], function ($) {

	/**
	 * Clears all popover messages in container and
	 * invokes callback after animation is complete
	 * @param $container
	 * @param callback
	 */
	function popovers($container, callback, selector) {
		selector = selector || '.popover';
		var $popovers = $container.find(selector),
			length = $popovers.length;

		if (length == 0)
			return callback && callback();

		// pass `_callback` to each popover to later invoke the main
		// callback after the last popover is hidden
		var _callback = function _callback() {
			_callback.counter = _callback.counter || 0;
			 // only call the callback after all popovers are hidden
			++_callback.counter == length && callback && callback()
		};
		$popovers.popover('hide', _callback);
	}


	/**
	 * Clears all alert messages in container and
	 * invokes callback after animation is complete.
	 * @param $container
	 * @param callback
	 */
	function alertMessages($container, callback) {
		$container.find('.alert-messages').slideUp(200)
			.promise()
			.done(function (e) {
				$container.find('.alert-messages').remove();
				callback && callback();
			});
	}

	/**
	 * Clears all form error messages in container
	 * @param $container
	 */
	function formErrors($container) {
		$container.find('.help-block').remove();
		$container.find('.form-group').removeClass('has-error');
	}

	/**
	 * Removes all types of messages in container
	 * and invokes callback after animation is complete.
	 * @param $container
	 * @param callback
	 */
	function all($container, callback) {
		console.log('Removing messages', arguments);
		if (arguments.length == 1) {
			callback = $container;
			$container = $('body');
		}

		var _callback = function _callback() {
			_callback.count = _callback.count || 0;
			++_callback.count == 2 && callback && callback();
		};
		formErrors($container);
		alertMessages($container, _callback);
		popovers($container, _callback);
	}
	return {
		alertMessages: alertMessages,
		popovers: popovers,
		formErrors: formErrors,
		allMessages: all
	};
});