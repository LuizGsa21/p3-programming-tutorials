define(['knockout', 'jquery', '_', 'ko-postbox', 'momentjs'], function (ko, $, _) {

	/**
	 * Attaches a sub-observable to `target.afterAnimation`
	 * When used in conjunction with `fadeVisible` of `slideVisible` bindingHandlers,
	 * the sub-observable will be updated after animation is complete.
	 *
	 * @param {observable} target - a ko observable
	 * @param {string} bindingHandler - either 'fadeVisible' or 'slideVisible'
	 * @returns target
	 */
	ko.extenders.afterAnimation = function (target, bindingHandler) {
		// ensure the binding handler supports afterAnmation callback
		if (!_.contains(['fadeVisible', 'slideVisible'], bindingHandler))
			throw Error('Binding handler ' + bindingHandler + ' does not have an animation callback');
		if ( ! target.afterAnimation) {
			// add a sub-observable
			target.afterAnimation = ko.observable();
		}
		return target;
	};

	/**
	 * Adds DOM element to `target.elements` array.
	 * @param {observable} target - a ko observable
	 * @param {Element} element - DOM element
	 */
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
			ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
				var elements = observable.elements;
				var index = elements.indexOf(element);
				observable.elements[index] = null;
			})
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

	ko.bindingHandlers.timeFromNow = {
		update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
			var utcTime, localTime;
			// time format: 2015-08-03T14:59:38.803775+00:00
			utcTime = ko.unwrap(valueAccessor());
			// Convert to "YYYY-MM-DDTHH:mm:ss"
			utcTime = utcTime.split('.')[0];
			localTime = moment.utc(utcTime, 'YYYY-MM-DDTHH:mm:ss');
			var text = moment(localTime).fromNow();
			// in very rare occasions momentjs will convert value to
			// "in a few seconds" instead of "a few seconds ago". I am
			// assuming the localtime is getting converted a few seconds into the future.
			// I don't know how to fix it so for now just do a brute force check
			if (text == 'in a few seconds')
				text = 'a few seconds ago';
			element.innerHTML = text;
		}
	};

	// table sorter
	// http://jsfiddle.net/norepro/bVB96/
	ko.bindingHandlers.sortTable = {
		init: function (element, valueAccessor) {
			var asc = false;

			ko.utils.registerEventHandler(element, 'click', function (event) {
				var value = ko.utils.unwrapObservable(valueAccessor()),
					sortBy = event.target.getAttribute('data-sort-by'),
					list = value.list;
				if ( ! sortBy) return;

				asc = !asc;
				// remove previous glyph
				var $column = $(event.target);
				$column.parent().find('.glyphicon').remove();
				// add asc or desc glyph
				$column.append($('<i></i>', {
					'class': 'glyphicon glyphicon-chevron-' + ((asc) ? 'up' : 'down'),
					'style': 'margin-left: 5px'
				}));

				list.sort(function (left, right) {
					var leftValue = ko.unwrap(eval('left' + '.' + sortBy)),
						rightValue = ko.unwrap(eval('right' + '.' + sortBy));
					if (typeof leftValue === 'string' && typeof rightValue === 'string') {
						leftValue = leftValue.toLowerCase();
						rightValue = rightValue.toLowerCase();
					}
					var _asc = (asc) ? 1 : -1;
					if (leftValue == rightValue) return 0;
					if (leftValue < rightValue) return -1 * _asc;
					if (leftValue > rightValue) return _asc;
				});
			});
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