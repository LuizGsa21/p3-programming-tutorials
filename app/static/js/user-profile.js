requirejs([
	'common',
	'helpers/LoginManager',
	'view-models/BaseViewModel',
	'view-models/UserViewModel',
	'components/login-form',
	'components/navbar-links',
	'jquery.form',
	'cropper'
], function (common, LoginManager, BaseViewModel, UserViewModel) {
	'use strict';
	var $         = common.jquery,
		ko        = common.ko,
		koMapping = common.koMapping,
		Model     = common.Model,
		Utils     = common.Utils;

	// register navbar component
	ko.components.register('navbar-links', {require: 'components/navbar-links'});
	ko.components.register('app-footer', {require: 'components/footer'});

	var BaseModal = function ($modal) {
		var self = this;
		self.$modal = $modal;
		self.set = function (attribute, value) {
			if (self.hasOwnProperty(attribute))
				this[attribute](value);
			else this[attribute] = ko.observable(value);
		};

		self.show = function () {
			self.$modal.modal('show');
			self.$modal.focus()
		};

		self.hide = function () {
			self.$modal.modal('hide');
		};

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
	var ProfileModal = function ($modal) {
		BaseModal.call(this, $modal);
		var self = this;
		self.avatar = ko.observable().syncWith('User.avatar', true);
		self.originalImage = ko.pureComputed(function () {
			var avatar = self.avatar();
			// add `original-` prefix to the file name to get the original image url
			var lastForwardSlash = avatar.lastIndexOf('/') + 1;
			return avatar.slice(0, lastForwardSlash) + 'original-' + avatar.slice(lastForwardSlash);
		});

		self.editProfile = function (target) {
			var data = ko.dataFor(target).user;
			self.set('title', 'Profile');
			self.set('modalCSS', 'modal-dialog');
			self.set('bodyTemplate', 'template-editProfile');
			self.set('btnSubmit', 'Save Profile');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			self.set('formUsername', ko.unwrap(data.username));
			self.set('formEmail', ko.unwrap(data.email));
			self.set('formFirstName', ko.unwrap(data.firstName));
			self.set('formLastName', ko.unwrap(data.lastName));
			self.onSuccess = function () {};
		};

		self.editAvatar = function (target) {
			self.setupCropper();
			self.set('title', 'Change Avatar');
			self.set('modalCSS', 'modal-dialog modal-lg');
			self.set('bodyTemplate', 'template-editAvatar');
			self.set('btnSubmit', 'Save Avatar');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');
			self.onSuccess = function (data) {
				self.avatar(data.result.user.avatar + '?timestamp=' + new Date().getTime());
			};
		};

		self.setupCropper = function () {
			var $modal = self.$modal;
			$modal.one('show.bs.modal', function (e) {
				// hide the images to prevent any flickering while the cropper initializes
				$modal.find('img').css('opacity', 0);
			});
			// initialize the cropper when its container is visible
			$modal.one('shown.bs.modal', function (e) {
				var $image    = $modal.find('.avatar-wrapper > img'),
					$cropData = $modal.find('#cropData');
				// check if cropper is initialized
				if ( ! $image.data('cropper') ) {
					$image.cropper({
						aspectRatio: 1,
						preview: '.avatar-preview',
						strict: true,
						crop: function (data) {
							$cropData.val([
								'{"x":', data.x,
								',"y":', data.y,
								',"height":', data.height,
								',"width":', data.width, '}'
							].join(''));
						}
					});
				}
				// update canvas image when a file is added
				$modal.find('input[type="file"]').off('change').on('change', function () {
					var $this = $(this);
					var files = $this.prop('files');
					if (files.length > 0) {
						var file = files[0];
						var url = URL.createObjectURL(file);
						$image.cropper('replace', url);
					}
					// update submit button text
					self.btnSubmit('Upload Avatar');
				});
			});
		}

	};

	var ArticleModal = function ($modal) {
		BaseModal.call(this, $modal);
		var self = this;
		self.modalCSS = 'modal-dialog';
		self._navbarLinks = ko.observable().subscribeTo('Navbar.updatedLinks', true);
		self.selectedCategoryId = ko.observable();
		self.categories = ko.computed(function () {
			return _.findWhere(self._navbarLinks(), {name: 'Categories'}).url;
		});
		self.selectedCategory = ko.computed(function () {
			var id = self.selectedCategoryId();
			return _.isNumber(id) ? _.findWhere(self.categories.peek(), {id: id}).name : '';
		});

		self.addArticle = function (target) {
			self.set('title', 'Add Tutorial');
			self.set('bodyTemplate', 'template-addArticle');
			self.set('btnSubmit', 'Publish Tutorial');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');
		};

		self.editArticle = function (target) {
			var data = ko.dataFor(target);
			self.set('title', 'Edit Tutorial');
			self.set('bodyTemplate', 'template-editArticle');
			self.set('btnSubmit', 'Save Changes');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			self.set('formId', ko.unwrap(data.id));
			self.set('formTitle', ko.unwrap(data.title));
			self.set('formBody', ko.unwrap(data.body));
			self.selectedCategoryId(ko.unwrap(data.category.id))
		};

		self.deleteArticle = function (target) {
			var data = ko.dataFor(target);
			self.set('title', 'Delete Tutorial');
			self.set('bodyTemplate', 'template-deleteArticle');
			self.set('btnSubmit', 'Delete Tutorial');
			self.set('btnSubmitCSS', 'btn btn-danger');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-default');

			self.set('articleTitle', ko.unwrap(data.title));
			self.set('formId', ko.unwrap(data.id));
		};

	};

	var CategoriesModal = function ($modal) {
		BaseModal.call(this, $modal);
		var self = this;
		self.title = 'Manage Categories';
		self.bodyTemplate = 'template-manageCategories';
		self._navbarLinks = ko.observable().subscribeTo('Navbar.updatedLinks', true);
		self.selectedCategoryId = ko.observable();
		self.categories = ko.computed(function () {
			return _.findWhere(self._navbarLinks(), {name: 'Categories'}).url;
		});

		self.selectedCategory = ko.computed(function () {
			var id = self.selectedCategoryId();
			return _.isNumber(id) ? _.findWhere(self.categories.peek(), {id: id}).name : '';
		});

		self.modalCSS = 'modal-dialog';
		self.addCategory = function () {
			self.set('btnSubmit', 'Add Category');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Close');
			self.set('btnCancelCSS', 'btn btn-default');
		};
		self.editCategory = function () {
			self.set('btnSubmit', 'Save Category');
			self.set('btnSubmitCSS', 'btn btn-primary');
		};
		self.deleteCategory = function () {
			self.set('btnSubmit', 'Delete Category');
			self.set('btnSubmitCSS', 'btn btn-danger');
		};

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

		self.onFail = function (data, $form) {
			var options = {
				action: 'before'
			};
			Utils.remove.allMessages(function () {
				if ( ! data.responseJSON ) {
					return Utils.show.messages($form, textStatus, options)
				}
				data = data.responseJSON.result;
				Utils.show.messages($form, data['flashed_messages'], options );
			});

			return false; // prevent default
		};
	};

	var modals = {};
	modals['CategoriesModal'] = CategoriesModal;
	modals['ProfileModal'] = ProfileModal;
	modals['ArticleModal'] = ArticleModal;

	var MainViewModel = function (data) {
		var self = this;
		self.allowedKeys = ['user', 'articles'];
		self.mapping = {
			user: {
				create: function (options) {
					return new UserViewModel(options.data)
				}
			}
		};
		// Articles to display in tutorials table
		self.articles = ko.observableArray();
		self.loadData(data);

		self.modal = ko.observable();
		self.initialized = ko.observable(false);

		self.showModal = function (view, event) {
			self.initialized(false);
			var $target = $(event.target);
			var className = $target.data('classname');
			var modal = (self[className]) ? self[className] : self[className] = new modals[className]($('#main-modal'));
			var method = $target.data('method');

			// Check if modal requires any preparation before displaying
			if (method)
				modal[method](event.target);

			self.modal(self[className]);
			self.initialized(true);
			modal.show();
		};

		self.onSuccess = ko.observable().subscribeTo('Modal.onSuccess');
		self.onSuccess.subscribe(function (response) {
			if (_.isFunction(response))
				response = response();
			var result = response.data.result;
			self.loadData(result);
			if (result.navbar) {
				console.log('CALLING LOAD DATA');
				ko.postbox.publish('Navbar.loadData', result.navbar);
			}

			if (result.articles && result.articles.length) {
				Utils.updateTime();
			}
		});

	};

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;

	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);
	window.mainViewModel = mainViewModel;
	Utils.updateTime();

	// Even though our submit buttons aren't inside the form
	// the user can still submit by pressing enter.
	// So use a global event listener to stop any default form submissions
	$(document).on('submit', 'form', function (e) {
		e.preventDefault();
	});
});