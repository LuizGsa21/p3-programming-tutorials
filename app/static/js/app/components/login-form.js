define([
	'jquery',
	'knockout',
	'helpers/LoginManager',
	'utils/Utils',
	'text!./login-form.html',
	'ko-postbox',
	'ko-custom-bindings'
], function ($, ko, LoginManager, Utils, htmlTemplate) {
	'use strict';

	var LoginFormViewModel = function () {
		// subscribe to and publish on `User-isLoggedIn`, and use
		// the last published value to initialize the observable
		this.user = {
			isLoggedIn: ko.observable().syncWith('User.isLoggedIn', true)
		};
		// keep track of where the form is located
		this.isInsideModal = false;

		// allow other views to set visibility state
		this.isVisible = ko.observable().subscribeTo('LoginForm.visible', true);

		// add a sub-observable to be updated after animation is complete
		this.isVisible.extend({ afterAnimation: 'fadeVisible' });

		// notify other views when the form is hidden or shown
		this.isVisible.afterAnimation.publishOn('LoginForm.visibleAA');

		// allow other views to show/hide this component inside a modal
		this._showModal = ko.observable().extend({notify: 'always'}).subscribeTo('LoginForm.showModal', true);
		this._showModal.subscribe(function (showModal) {
			(showModal) ? this.showModal() : this.hideModal();
		}, this);

		// allow other views to change form tabs
		this._focusTab = ko.observable().extend({notify: 'always'}).subscribeTo('LoginForm.tab', true);
		this._focusTab.subscribe(function (tabName) {
			var tab = this.$container.find('a[href="#tab-' + tabName + '"]');
			if (tab.length)
				tab.click();
		}, this);


		this.oAuthLogin = function (view, event) {
			var provider = $(event.currentTarget).data('provider');
			LoginManager.getInstance().login(provider, {
				beforeSubmit: this._beforeSubmit,
				onSuccess: this._onSuccess,
				onFail: this._onFail
			}, this);
		};
	};

	// call this method before moving the component
	// so we can restore its previous position
	LoginFormViewModel.prototype.savePosition = function () {
		var action;
		this._$markerElement = this.$container.prev();
		if (this._$markerElement.length) {
			action = 'insertAfter'
		} else {
			this._$markerElement = this.$container.parent();
			action = 'append'
		}
		this._restorePosition = function () {
			this.$container[action](this._$markerElement);
			this.$container.append(this.$modal); // bring the modal with it
			this.isInsideModal = false;
		}.bind(this);
	};

	LoginFormViewModel.prototype.restorePosition = function () {
		if ( ! this._restorePosition)
			throw Error('LoginFormViewModel: No position was saved.');
		this._restorePosition();
	};

	LoginFormViewModel.prototype.showModal = function () {
		// save this component's position so we can restore it when the modal is hidden
		this.savePosition();
		// hide any popovers being displayed
		this.hidePopovers();

		if (!this.$modal) { // initialize modal on first call
			// get the modal located inside this component
			this.$modal = this.$container.find('.login-form-modal');
			// move the component back to its original position when the modal is hidden
			this.$modal.on('hidden.bs.modal', function () {
				if (this.isInsideModal)
					this.restorePosition();
			}.bind(this));
			this.$modal.on('hide.bs.modal', function () {
				this.hidePopovers();
			}.bind(this));
		}
		// move the empty modal to the body
		this.$modal.appendTo('body');
		// place this component inside the modal
		this.$container.appendTo(this.$modal.find('.modal-dialog'));
		// update `isInsideModal` then show the modal
		this.isInsideModal = true;
		this.$modal.modal('show');
	};

	LoginFormViewModel.prototype.hideModal = function () {
		if (this.$modal && this.$modal.hasClass('in')) {
			this.$modal.modal('hide');
		}

	};

	LoginFormViewModel.prototype._beforeSubmit = function (data, $form, options) {
		var response = function () {
			return {
				view: this,
				data: data,
				form: $form,
				options: options,
				preventDefault: false
			}
		}.bind(this);
		ko.postbox.publish('LoginForm.beforeSubmit', response);

		if (response.preventDefault)
			return false; // prevent form submission

		// when logging in using oauth, notify the user that we're verifying login
		if ($form == null) {
			Utils.remove.allMessages(function () {
				Utils.show.messages('#general-alert', 'Verifying login...', 'info');
			});
		}
	};

	LoginFormViewModel.prototype._onSuccess = function (data, textStatus, jqXHR) {
		console.log('LoginForm onSuccess:', arguments);
		this.hideModal();
		// update user login status
		this.user.isLoggedIn(true);
		var response = function () {
			return {
				view: this,
				data: data,
				preventDefault: false
			}
		}.bind(this);

		ko.postbox.publish('LoginForm.onSuccess', response);

		if (response.preventDefault) // do nothing
			return;

		// clear form input fields
		this.$container.find('form').find(':input').val('');
		data = data.result;

		Utils.remove.allMessages(function () {
			Utils.show.messages('#general-alert', data['flashed_messages']);
		});
	};

	LoginFormViewModel.prototype._onFail = function (data, textStatus, errorThrown, form) {
		console.log('LoginForm onFail:', arguments);
		var response = function () {
			return {
				view: this,
				data: data,
				preventDefault: false
			}
		}.bind(this);
		ko.postbox.publish('LoginForm.onFail', response);

		if (response.preventDefault) // do nothing
			return;

		if ( ! data.responseJSON) {
			Utils.show.messages('#general-alert', textStatus, 'danger');
			return;
		}
		data = data.responseJSON.result;
		if (form) { // display error message in a popover
			var options = {
				popover: {
					// control the order of how the mobile popover content
					// is displayed
					orderedKeys: ['username', 'email', 'password']
				},
				// if we get errors that are not form errors
				// display them in `#general-alert`
				formFallbackContainer: $('#general-alert')
			};
			Utils.remove.allMessages(function () {
				Utils.show.messages(form, data['flashed_messages'], options);
			});

		} else {
			_.each(data['flashed_messages'], function (obj) {
				// notify the main view that the page needs a refresh
				if (obj.message.indexOf('You are already logged in') > -1) {
					ko.postbox.publish('Global.pageRefresh', 'out of sync');
				}
			}, this);

			Utils.remove.allMessages(function () {
				Utils.show.messages('#general-alert', data['flashed_messages']);
			});

		}
	};

	LoginFormViewModel.prototype.hidePopovers = function () {
		Utils.remove.popovers(this.$container, null, ':input');
	};

	return {
		viewModel: {
			createViewModel: function (params, componentInfo) {
				var component = new LoginFormViewModel(params);

				component.$container = $(componentInfo.element);

				component.$container.on('click', '[data-toggle="tab"]', function (e) {
					Utils.remove.popovers(component.$container, null, ':input');
				});

				component.$container.on('click', 'form', function (e) {
					if ( ! component.serializeForm) {
						component.serializeForm = true;
						LoginManager.getInstance().setLoginRegisterForm('#login-form-container', {
							onSuccess: component._onSuccess,
							onFail: component._onFail
						}, component);
					}
				});
				return component;
			}
		},
		template: htmlTemplate
	}
});