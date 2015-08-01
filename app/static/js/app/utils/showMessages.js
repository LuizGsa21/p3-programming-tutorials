define(['jquery', '_', 'bootstrap'], function ($, _) {

	function createAlertBox(message, category) {
		var $outerDiv = $('<div>', {'class': 'alert-messages'}),
			$innerDiv = $('<div>', {'class': 'alert alert-' + category}),
			$a        = $('<a href="#" class="close" data-dismiss="alert">&times;</a>');
		return $outerDiv.append($innerDiv.append($a).append(message))
	}

	function alertMessage($container, message, category, method) {
		if (method == undefined) method = 'append';
		var $msg = createAlertBox(message, category).hide();
		$container[method]($msg);
		$msg.slideDown();
	}

	function formErrors($form, errors, prefix) {
		var $field, messages,
			msg,
			$element; // a help-block gets appended after this element
		for (var labelID in errors) if (errors.hasOwnProperty(labelID)) {
			// get the current field
			$field = $form.find(prefix + labelID);
			// get all the errors for this field and add a line break between each error message
			messages = errors[labelID];
			msg = messages[0];
			for (var i = 1; i < messages.length; i++)
				msg += '<br>'+ messages[i]
			$field.closest('.form-group').addClass('has-error');

			// if this is an input-group append the message after this field's container
			var $parent = $field.parent();
			$element = $parent.hasClass('input-group') ? $parent : $field;
			$element.after($('<p></p>').addClass('help-block').html(msg));
		}
	}

	function formPopovers($form, errors, options) {
		var prefix = $form.data('prefix');
		var popoverOptions = {
			container: 'body',
			selector: null,
			placement: options.popover.placement || 'left',
			html: 'true',
			content: '',
			trigger: 'manual',
			template: '<div class="popover" role="tooltip">' +
				'<div class="arrow"></div>' +
				'<button type="button" class="close" onclick="$(this).closest(\'.popover\').popover(\'destroy\');">&times;</button>' +
				'<div class="popover-content"></div>' +
			'</div>'
		};

		// we can't call `$form.popover('show')` to show the popovers because
		// the form might have other popovers that are hidden and not meant to be displayed.
		// So we will create a filtered array to later display the popovers.
		var filteredPopovers = [];

		// while creating the popover messages we will build
		// a mobile version popover by adding all the content
		// into a single popover
		var mobileContent = '';

		var orderedKeys;
		// use the ordered keys if provided.
		if (_.isObject(options.popover) && _.isArray(options.popover.orderedKeys)) {
			// The ordered keys will only effect the order
			// how the mobile popover is built.
			orderedKeys = options.popover.orderedKeys;
		} else {
			// no ordered keys were provided so use the default keys
			orderedKeys = Object.keys(errors);
		}

		_.each(orderedKeys, function (key) {
			// ignore invalid keys
			if ( ! errors.hasOwnProperty(key)) return;

			var selector = prefix + key, // create the selector using the provided prefix
				$input   = $form.find(selector),
				popover  = $input.data('bs.popover');

			// customize the error message
			var message = errors[key][0];
			var labelName = key[0].toUpperCase() + key.substring(1);
			if (message.indexOf('This') == 0) {
				message = message.replace('This', labelName);
			}

			if ( ! popover) { // Initialize the popover
				console.log('initializing')
				var options = $.extend({}, popoverOptions);
				options.selector = selector;
				options.content = message;
				$input.popover(options);
			} else { // update content
				console.log(message);
				popover.options.content = message;
			}
			mobileContent += message + '<br>';
			// save this element to the filtered array
			filteredPopovers.push($input[0]);

		});
		// check if this form supports a mobile version popover
		var $mPopover = $form.find('.mobile-popover');

		if ($mPopover.length) {
			var popover = $mPopover.data('bs.popover');
			if ( ! popover) { // initialize the popover
				var mobileOptions = $.extend({}, popoverOptions);
				mobileOptions.selector = '.mobile-popover';
				mobileOptions.placement = 'top';
				mobileOptions.content = mobileContent;
				$mPopover.popover(mobileOptions);
			} else {
				// update content
				popover.options.content = mobileContent;
			}

			if ($(window).width() <= 720) { // display mobile version
				$mPopover.popover('show');
			} else {
				// display desktop version
				$(filteredPopovers).popover('show');
			}

		} else {
			// no mobile version found so display the desktop version
			$(filteredPopovers).popover('show');
		}

	}

	function messages($container, flashedMessages, options) {
		//console.log('Showing messages', arguments);
		// convert to jquery object
		if (typeof $container == 'string') $container = $($container);

		// make it compatible to display an alert message
		if (typeof flashedMessages == 'string' && typeof options == 'string') {
			flashedMessages = [{message: flashedMessages, category: options}];
		}
		if (flashedMessages.length == 0) return;

		var defaults = {
			action: 'append',
			prefix: '#',
			popover: false,
			formFallbackContainer: null
		};

		options = (typeof options == 'object') ? $.extend(defaults, options) : defaults;

		if (options.useFormFallback) {
			options.fallbackContainer = $(options.fallbackContainer);
		}

		flashedMessages.forEach(function (message) {
			if (message.category == 'form-error') {
				if (options.popover)
					formPopovers($container, message.message, options);
				else
					formErrors($container, message.message, options.prefix);
			} else {
				// display the message in an alert
				// if a formFallbackContainer was set use it.
				// this scenario happens when we want to display the error messages in a form
				if (options.formFallbackContainer) {
					alertMessage(options.formFallbackContainer, message.message, message.category, options.action);
				} else {
					alertMessage($container, message.message, message.category, options.action);
				}
			}
		});

	}

	return {
		formErrors: formErrors,
		formPopovers: formPopovers,
		alertMessage: alertMessage,
		messages: messages
	};


});