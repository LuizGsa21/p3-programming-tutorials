define([
	'knockout',
	'modals/BaseModal'
], function (ko, BaseModal) {
	'use strict';

	/**
	 * Dynamically creates a modal to perform CRUD operations on an article.
	 * Uses the following templates declared in `profile-templates.html`:
	 * 	- `template-addArticle`
	 * 	- `template-editArticle`
	 * 	- `template-deleteArticle`
	 * @constructor
	 * @augments {BaseModal}
	 */
	var ArticleModal = function ArticleModal() {
		BaseModal.call(this);
		var self = this;
		self.modalCSS = 'modal-dialog';
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

		/**
		 * Updates the modals UI and shows the modal using `template-addArticle`.
		 */
		self.addArticle = function () {
			// update CSS
			self.set('title', 'Add Tutorial');
			self.set('btnSubmit', 'Publish Tutorial');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			// update template and display the modal
			self.set('bodyTemplate', 'template-addArticle');
			self.show();
		};

		/**
		 * Updates the modals UI and shows the modal using `template-editArticle`
		 * Uses `getTargetData` to grab the `event.target` data to populate the form.
		 * @param {Object} view - knockout view
		 * @param {event} event  - event
		 */
		self.editArticle = function (view, event) {
			// update UI
			self.set('title', 'Edit Tutorial');
			self.set('btnSubmit', 'Save Changes');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			// Update form observables
			var data = self.getTargetData.apply(self, arguments);
			self.set('formId', ko.unwrap(data.id));
			self.set('formTitle', ko.unwrap(data.title));
			self.set('formBody', ko.unwrap(data.body));
			self.selectedCategoryId(ko.unwrap(data.category.id));

			// update template and display the modal
			self.set('bodyTemplate', 'template-editArticle');
			self.show();
		};

		/**
		 * Updates the modals UI and shows the modal using `template-deleteArticle`
		 * Uses `getTargetData` to grab the `event.target` data to populate the form.
		 * @param {Object} view - knockout view
		 * @param {event} event  - event
		 */
		self.deleteArticle = function (view, event) {
			// update UI
			self.set('title', 'Delete Tutorial');
			self.set('btnSubmit', 'Delete Tutorial');
			self.set('btnSubmitCSS', 'btn btn-danger');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-default');

			// Update form and observables
			var data = self.getTargetData.apply(self, arguments);
			self.set('articleTitle', ko.unwrap(data.title));
			self.set('formId', ko.unwrap(data.id));

			// update template and display the modal
			self.set('bodyTemplate', 'template-deleteArticle');
			self.show();
		};
	};

	return ArticleModal;
});