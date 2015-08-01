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

	var ModalTemplates = {
		editProfile: function (data) {
			if (data.user)
				data = data.user;
			return {
				title: 'Edit Profile',
				bodyTemplate: 'template-editProfile',
				btnSubmit: 'Save Profile',
				formUsername: Model.getData('user.username'),
				formEmail: Model.getData('user.email'),
				formFirstName: Model.getData('user.firstName'),
				formLastName: Model.getData('user.lastName')
			};
		},
		addArticle: function (data) {
			if (data.article)
				data = data.article;
			return {
				title: 'Add Tutorial',
				bodyTemplate: 'template-addArticle',
				btnSubmit: 'Publish Tutorial'
			}
		},
		editArticle: function (data) {
			if (data.article)
				data = data.article;
			return {
				title: 'Edit Tutorial',
				formId: ko.unwrap(data.id),
				formTitle: ko.unwrap(data.title),
				formBody: ko.unwrap(data.body),
				formCategory: ko.unwrap(data.category.id),
				bodyTemplate: 'template-editArticle',
				btnSubmit: 'Save Changes'
			}
		},
		deleteArticle: function (data) {
			return {
				title: 'Delete Tutorial',
				formId: ko.unwrap(data.id),
				articleTitle: data.title,
				bodyTemplate: 'template-deleteArticle',
				btnSubmit: 'Delete',
				btnSubmitCSS: 'btn btn-danger'
			}
		},
		editAvatar: function (data) {

			// get the original avatar image
			var avatar = data.user.avatar();
			var lastForwardSlash = avatar.lastIndexOf('/');
			var orignalImage = avatar.substring(0, lastForwardSlash + 1) + 'original-' + avatar.substring(lastForwardSlash + 1);
			console.log(avatar);
			return {
				_afterRender: function (view, $modal) {
					// hide the images to prevent any flickering while the cropper initializes
					$modal.find('img').css('opacity', 0);

					// initialize the cropper when its container is visible
					$modal.one('shown.bs.modal', function (e) {
						var $image    = $modal.find('.avatar-wrapper > img'),
							$cropData = $modal.find('#cropData');

						$image.cropper({
							aspectRatio: 1,
							preview: '.avatar-preview',
							strict: true,
							crop: function (data) {
								var json = [
									'{"x":', data.x,
									',"y":', data.y,
									',"height":', data.height,
									',"width":', data.width, '}'
								].join('');
								$cropData.val(json);
							}
						});

						// update canvas image when a file is added
						$modal.find('input[type="file"]').on('change', function () {
							var $this = $(this);
							var files = $this.prop('files');
							if (files.length > 0) {
								var file = files[0];
								console.log(file);
								var url = URL.createObjectURL(file);
								$image.cropper('replace', url);
							}
							$modal.find('.btn-primary').html('Upload Avatar');
						});
					});
				},
				title: 'Change Avatar',
				//user: data.user,
				avatar: orignalImage,
				largeModal: true,
				bodyTemplate: 'template-editAvatar',
				btnCancel: 'Cancel',
				btnSubmit: 'Save Avatar'
			};
		}

	};

	var ModalViewModel = function () {

		this.$modal = $('#main-modal');

		// reset to default values
		this._reset = function () {
			// reset to default on config
			var defaults = {
				initialized: false, // renders the template when true
				largeModal: false,
				btnCancel: 'Cancel',
				btnCancelCSS: 'btn btn-default',
				btnSubmit: 'Submit',
				btnSubmitCSS: 'btn btn-primary'
			};
			koMapping.fromJS(defaults, {}, this);
		};

		this.loadData = function (data) {

			koMapping.fromJS(data, {}, this);
			this.initialized(true);
			if (data._afterRender) {
				data._afterRender(this, this.$modal);
			}

		}.bind(this);

		// set default config
		this._reset();

		this.modalCSS = ko.pureComputed(function () {
			return this.largeModal() ? 'modal-dialog modal-lg' : 'modal-dialog';
		}, this);

		this.show = function () {
			this.$modal.modal('show');
		}.bind(this);

		this.hide = function () {
			this.$modal.modal('hide');
		}.bind(this);

		this.submitForm = function (view, event) {
			var $form = this.$modal.find('form');
			var self = this;
			console.log($form);
			$form.ajaxSubmit({
				type: 'POST',
				dataType: 'json',
				csrfHeader: true,
				success: function (data) {
					var response = function () {
						return {
							view: self,
							data: data
						}
					}.bind(this);
					ko.postbox.publish('Modal.onSuccess', response);
					self.hide();
					Utils.remove.formErrors(self.$modal.find('form'));
				},
				error: function (data) {
					console.log(data);
					if (data.responseJSON) {
						data = data.responseJSON.result;
						var $form = self.$modal.find('form');
						// remove any previous errors
						Utils.remove.formErrors($form);
						// show form errors
						Utils.show.messages($form, data['flashed_messages']);
					} else {
						//app.display($('.alert-box'), data);
						//$mainModal.modal('hide');
						//$('body').scrollTop(0);
					}
				}
			});
		}.bind(this);

		// Reset the observable values every time the modal closes
		this.$modal.on('hidden.bs.modal', function () {
			// reset the modal when hidden
			this._reset();
		}.bind(this));

	};

	var MainViewModel = function (data) {

		this.allowedKeys = ['user', 'articles'];
		this.mapping = {
			user: {
				create: function (options) {
					return new UserViewModel(options.data)
				}
			}
		};
		this.articles = ko.observableArray([]);

		this.loadData(data);
		this.modal = new ModalViewModel();
		this.showModal = function (view, event) {
			var data = ko.dataFor(event.target);
			var templateName = $(event.target).data('method');
			var templateData = ModalTemplates[templateName](data);
			this.modal.loadData(templateData);
			this.modal.show();
		}.bind(this);

		this.onSuccess = ko.observable().subscribeTo('Modal.onSuccess');
		this.onSuccess.subscribe(function (response) {
			if (_.isFunction(response))
				response = response();
			var result = response.data.result;
			this.loadData(result);
			if (result.articles && result.articles.length) {
				Utils.updateTime();
			}

		}, this);

	};

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;

	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);
	Utils.updateTime();
});