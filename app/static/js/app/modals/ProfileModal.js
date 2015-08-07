define([
	'knockout',
	'modals/BaseModal'
], function (ko, BaseModal) {
	'use strict';

	/**
	 * Dynamically creates a modal to edit the users profile.
	 * Uses the following templates declared in `profile-templates.html`:
	 * 	- `template-editProfile`
	 * @constructor
	 * @augments {BaseModal}
	 */
	var ProfileModal = function () {
		BaseModal.call(this);
		var self = this;

		/**
		 * Updates the modals UI and shows the modal using `template-editProfile`
		 * Uses `getTargetData` to grab the `event.target` data to populate the form.
		 * @param view {Object} - knockout view
		 * @param event {event} - event
		 */
		self.editProfile = function (view, event) {
			var data = self.getTargetData.apply(self, arguments);
			if (data.user) // unwrap user data
				data = data.user;
			// update UI
			self.set('title', 'Profile');
			self.set('modalCSS', 'modal-dialog');
			self.set('btnSubmit', 'Save Profile');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			// Update form observables
			self.set('formId', ko.unwrap(data.id));
			self.set('formUsername', ko.unwrap(data.username));
			self.set('formEmail', ko.unwrap(data.email));
			self.set('formFirstName', ko.unwrap(data.firstName));
			self.set('formLastName', ko.unwrap(data.lastName));

			// update template and display the modal
			self.set('bodyTemplate', 'template-editProfile');
			self.show();
		};
	};

	return ProfileModal;
});