define([
	'jquery',
	'knockout',
	'utils/Utils',
	'text!./modal.html'
], function ($, ko, Utils, htmlTemplate) {
	'use strict';

	var BaseModal = function () {
		var self = this;
		// All modals will share a single `modal` observable and `$modal` element

		// save a reference to `BaseModal.modal` and BaseModal.$modal for convenience.
		self.modal = BaseModal.modal;
		self.$modal = BaseModal.$modal;
		self.isVisible = false;

		/**
		 * Sets the value of the observable. If the observable hasn't yet been initialized
		 * it will initialize the observable with the given value.
		 *
		 * @param observableName {string} - an attribute name
		 * @param value {*} - any value supported by `ko.observable`
		 */
		self.set = function (observableName, value) {
			if (self.hasOwnProperty(observableName))
				this[observableName](value);
			else this[observableName] = ko.observable(value);
		};

		/**
		 * Displays the current modal and keeps `isVisble` status in sync.
		 */
		self.show = function () {
			if (self.isVisible) return;
			// add this modal to the main modal observable
			self.modal(self); // this is the same as `BaseModal.modal(self)`

			// render the template
			self.modal.initialized(true);
			// Setup on hidden events
			self.$modal.one('hidden.bs.modal', function () {
				// prevent the template from being rendered
				// so knockout doesn't complain about uninitialized variables
				// when switching modals
				self.isVisible = false;
				self.modal.initialized(false);
			});
			self.isVisible = true;
			self.$modal.modal('show');
		};

		self.hide = function () {
			self.$modal.modal('hide');
		};

		/**
		 * Returns the target data from a knockout event.
		 * If only one argument is given, it will be treated as the event target
		 *
		 * @param view {object} - knockout view
		 * @param event {event} - event
		 */
		self.getTargetData = function (view, event) {
			var target;
			if (arguments.length == 1)
				target = view;
			else
				target = event.target;
			return ko.dataFor(target);
		};

		/**
		 * Submits the current "visible" form inside the modal
		 * and shares the response on `Modal.onSuccess` or `Modal.onFail` prior
		 * to calling `onSuccess` on `onFail`.
		 */
		self.submit = function () {
			var $form = self.$modal.find('form:visible');
			$form.ajaxSubmit({
				csrfHeader: true,
				success: function (data) {
					console.log(arguments);

					var response = Utils.shareResponse(data, 'Modal.onSuccess', self);

					if (response.preventDefault || self.onSuccess(data, $form) === false)
						return;

					self.hide();
				},
				error: function (data, textStatus, errorThrown, form) {
					console.log(arguments);

					var response = Utils.shareResponse(data, 'Modal.onFail', self);

					if (response.preventDefault || self.onFail(data, $form) === false)
						return;
					// display form errors
					Utils.remove.allMessages(function () {
						if (!data.responseJSON) {
							return Utils.show.messages($form, textStatus)
						}
						data = data.responseJSON.result;
						Utils.show.messages($form, data['flashed_messages']);
					});
				}
			});
		};
		self.onSuccess = function () {};
		self.onFail = function () {};
	};
	BaseModal.modal = ko.observable();
	BaseModal.$modal = $(htmlTemplate);
	BaseModal.$modal.appendTo(document.body);

	BaseModal.modal.initialized = ko.observable(false);
	// prevent the modal template from being rendered until `BaseModal.modal` is initialized
	// This will prevent knockout from throwing errors when switching between modals
	return BaseModal;
});