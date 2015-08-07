define([
	'knockout',
	'modals/BaseModal'
], function (ko, BaseModal) {
	'use strict';

	/**
	 * Dynamically creates a modal to edit or delete users.
	 * Uses the following templates declared in `profile-templates.html`:
	 * 	- `template-editProfile`
	 * 	- `template-deleteUser`
	 * @constructor
	 * @augments {BaseModal}
	 */
	var UserModal = function () {
		BaseModal.call(this);
		var self = this;

		/**
		 * Updates the modals UI and shows the modal using `template-editProfile`
		 * Uses `getTargetData` to grab the `event.target` data to populate the form.
		 * @param {Object} view - knockout view
		 * @param {event} event  - event
		 */
		self.editUser = function (view, event) {
			// update UI
			self.set('title', 'Edit User');
			self.set('modalCSS', 'modal-dialog');
			self.set('btnSubmit', 'Save Changes');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			// Update form observables
			var data = self.getTargetData.apply(self, arguments);
			self.set('formId', ko.unwrap(data.id));
			self.set('formUsername', ko.unwrap(data.username));
			self.set('formEmail', ko.unwrap(data.email));
			self.set('formFirstName', ko.unwrap(data.firstName));
			self.set('formLastName', ko.unwrap(data.lastName));

			// update template and display the modal
			self.set('bodyTemplate', 'template-editProfile');
			self.show();
		};

		/**
		 * Updates the modals UI and shows the modal using `template-deleteUser`
		 * Uses `getTargetData` to grab the `event.target` data to populate the form.
		 * @param {Object} view - knockout view
		 * @param {event} event  - event
		 */
		self.deleteUser = function (view, event) {
			// update UI
			self.set('title', 'Delete User');
			self.set('btnSubmit', 'Delete User');
			self.set('btnSubmitCSS', 'btn btn-danger');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-default');

			// Update form observables
			var data = self.getTargetData.apply(self, arguments);
			self.set('username', ko.unwrap(data.username));
			self.set('formId', ko.unwrap(data.id));

			// update template and display the modal
			self.set('bodyTemplate', 'template-deleteUser');
			self.show();
		};
	};

	return UserModal;
});