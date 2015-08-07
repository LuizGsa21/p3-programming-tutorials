define([
	'knockout',
	'utils/Utils',
	'modals/BaseModal'
], function (ko, Utils, BaseModal) {
	'use strict';

	/**
	 * Dynamically creates a modal to perform CRUD operations on a category.
	 * Uses the following templates declared in `profile-templates.html`:
	 * 	- `template-manageCategories`
	 * @constructor
	 * @augments {BaseModal}
	 */
	var CategoryModal = function () {
		BaseModal.call(this);
		var self = this;
		// Use the categories on the navbar as the selection options
		self._navbarLinks = ko.observable().subscribeTo('Navbar.updatedLinks', true);
		self.selectedCategoryId = ko.observable();
		self.categories = ko.computed(function () {
			var categories = _.findWhere(self._navbarLinks(), {name: 'Categories'});
			if (categories)
				return categories.url;
			else return [];
		});
		self.selectedCategory = ko.computed(function () {
			var id = self.selectedCategoryId();
			return _.isNumber(id) ? _.findWhere(self.categories.peek(), {id: id}).name : '';
		});

		// setup non-observable UI variables
		self.title = 'Manage Categories';
		self.bodyTemplate = 'template-manageCategories';
		self.modalCSS = 'modal-dialog';

		/**
		 * Updates the modal's UI for adding a category then displays the modal.
		 */
		self.addCategory = function () {
			// Update UI
			self.set('btnSubmit', 'Add Category');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Close');
			self.set('btnCancelCSS', 'btn btn-default');

			// display modal
			self.show();
		};

		/**
		 * Updates the modal's UI for editing a category then displays the modal.
		 */
		self.editCategory = function () {
			// Update UI
			self.set('btnSubmit', 'Save Category');
			self.set('btnSubmitCSS', 'btn btn-primary');

			// display modal
			self.show();
		};

		/**
		 * Updates the modal's UI for deleting a category and shows the modal.
		 */
		self.deleteCategory = function () {
			// update UI
			self.set('btnSubmit', 'Delete Category');
			self.set('btnSubmitCSS', 'btn btn-danger');

			// display modal
			self.show();
		};

		/**
		 * This method is called when a form has successfully been submitted. When called it
		 * will display any alert messages received from the server and returns `false` to prevent
		 * default behavior from `BaseModal` which hides the modal after form submission.
		 *
		 * @override
		 * @param {Object} data - data received from server
		 * @param {jQuery} $form - the submitted form
		 * @returns {boolean} false
		 */
		self.onSuccess = function (data, $form) {
			Utils.remove.allMessages(function () {
				data = data.result;
				var options = {
					action: 'before'
				};
				Utils.show.messages($form, data['flashed_messages'], options);
			});
			return false; // prevent modal from hiding
		};
	};

	return CategoryModal;

});