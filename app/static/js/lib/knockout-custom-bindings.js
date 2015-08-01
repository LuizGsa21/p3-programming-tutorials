define(['knockout', 'jquery', '_', 'ko-postbox'], function (ko, $, _) {

	ko.extenders.afterAnimation = function (target, bindingHandler) {
		if (!_.contains(['fadeVisible', 'slideVisible'], bindingHandler))
			throw Error('Binding handler ' + bindingHandler + ' does not have an animation callback');
		if (!target.afterAnimation) {
			// add a sub-observable
			target.afterAnimation = ko.observable();
		}
		return target;
	};

	ko.extenders.storeElement = function (target, element) {
		target.elements = target.elements || [];
		target.elements.push(element);
	};

	ko.bindingHandlers.storeElement = {
		// turns: storeElement: fadeVisible !isEditing()
		// into: fadeVisible: !isEditing(), storeElement: isEditing
		preprocess: function (value, name, addBindingCallback) {
			var options = value.split(' ');
			var length = options.length;
			// return default value
			if (length == 0 || length == 1)
				return value;
			// use the first value as a binding handler
			// and the second value as the expression
			addBindingCallback(options[0], options[1]);

			return options[1].replace(/[!()]/g, '');
		},
		init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
			var observable = valueAccessor();
			observable.extend({storeElement: element});
		}
	};

	ko.bindingHandlers.fadeVisible = {
		// turns: fadeVisible: isVisible callback
		// into: fadeVisible: isVisible, afterAnimationCallback: callback
		preprocess: function (value, name, addBindingCallback) {
			var options = value.split(' ');
			var length = options.length;
			// return default value
			if (length == 0 || length == 1)
				return value;
			// use the second value as the callback
			addBindingCallback('afterAnimationCallback', options[1]);

			return options[0];
		},
		init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
			$(element).toggle(false);
		},
		update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
			var observable = valueAccessor(),
				$element   = $(element),
				callback;

			if (typeof observable == 'function' && observable.afterAnimation) {
				callback = observable.afterAnimation;
			} else {
				callback = allBindings.get('afterAnimationCallback');
			}
			var value = ko.unwrap(observable);

			if (!callback)
				return value ? $element.fadeIn() : $element.fadeOut();

			if (value) {
				$element.fadeIn(function () { callback(true, element); });
			} else {
				$element.fadeOut(function () { callback(false, element); });
			}
		}
	};

	ko.bindingHandlers.slideVisible = {
		init: function (element, valueAccessor) {
			return $(element).toggle(false);
		},
		update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
			ko.unwrap(valueAccessor()) ? $(element).slideDown() : $(element).slideUp();
		}
	};

	// debug
	(function () {
		var existing = ko.bindingProvider.instance;
		ko.bindingProvider.instance = {
			nodeHasBindings: existing.nodeHasBindings,
			getBindings: function (node, bindingContext) {
				var bindings;
				try {
					bindings = existing.getBindings(node, bindingContext);
				}
				catch (ex) {
					if (window.console && console.log) {
						console.log("binding error", ex.message, node, bindingContext);
					}
				}
				return bindings;
			}
		};
	})();
});