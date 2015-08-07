define([
	'jquery',
	'knockout',
	'modals/BaseModal',
	'cropper'
], function ($, ko, BaseModal) {
	'use strict';

	/**
	 * Dynamically creates a modal to edit the users avatar.
	 * Uses the following templates declared in `profile-templates.html`:
	 * 	- `template-editAvatar`
	 * @constructor
	 * @augments {BaseModal}
	 */
	var AvatarModal = function () {
		BaseModal.call(this);
		var self = this;
		// Sync with `User.avatar` so that all subscribers get alerted when the avatar url is changed.
		self.avatar = ko.observable().syncWith('User.avatar', true);
		// To access the original (uncropped) image from the server we must add `original-` prefix to the avatar filename.
		// Always use the original image inside the cropper so if the user doesn't upload an image he may still crop his avatar.
		self.originalImage = ko.pureComputed(function () {
			var avatar = self.avatar();
			// add `original-` prefix to the file name to get the original image url
			var index = avatar.lastIndexOf('/') + 1;
			return avatar.slice(0, index) + 'original-' + avatar.slice(index);
		});

		/**
		 * Initializes the cropper, updates the modals UI and
		 * shows the modal using `template-editAvatar`
		 */
		self.editAvatar = function () {
			// initialize cropper
			self._setupCropper();

			// update UI
			self.set('title', 'Change Avatar');
			self.set('modalCSS', 'modal-dialog modal-lg');
			self.set('btnSubmit', 'Save Avatar');
			self.set('btnSubmitCSS', 'btn btn-primary');
			self.set('btnCancel', 'Cancel');
			self.set('btnCancelCSS', 'btn btn-danger');

			// update template and display the modal
			self.set('bodyTemplate', 'template-editAvatar');
			self.show();
		};

		/**
		 * Adds a timestamp to `avatar` so that all images using the avatar url are updated.
		 * @override
		 * @param data - ajax response
		 */
		self.onSuccess = function (data) {
			self.avatar(data.result.user.avatar + '?timestamp=' + new Date().getTime());
		};

		/**
		 * Initializes the cropper.
		 * The cropper is initialized when `shown.bs.modal` is triggered because the
		 * cropper needs its container to be visible during initialization.
		 * @private
		 */
		self._setupCropper = function () {
			var $modal = self.$modal;
			$modal.one('show.bs.modal', function (e) {
				// hide the images to prevent any flickering while the cropper initializes
				$modal.find('img').css('opacity', 0);
			});
			// initialize the cropper when its container is visible
			$modal.one('shown.bs.modal', function (e) {
				var $image    = $modal.find('.avatar-wrapper > img'),
					$cropData = $modal.find('#cropData');
				// check if cropper is already initialized
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

	return AvatarModal;
});