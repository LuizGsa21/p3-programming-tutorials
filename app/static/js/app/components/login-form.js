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
			isLoggedIn: ko.observable().syncWith('User.isLoggedIn', true),
			username: ko.observable().syncWith('User.username', true)
		};

		// keep track of where the form is located
		this.isInsideModal = false;

		// allow other views to set visibility state
		this.isVisible = ko.observable().subscribeTo('LoginForm.visible', true);

		// add a sub-observable to be updated after animation is complete
		this.isVisible.extend({ afterAnimation: 'fadeVisible' });

		// notify other views when the form is hidden or shown
		this.isVisible.afterAnimation.publishOn('LoginForm.visibleAA'); // visibleAA = visibleAfterAnimation

		// allow other views to show/hide this component inside a modal
		this._showModal = ko.observable().extend({notify: 'always'}).subscribeTo('LoginForm.showModal', true);
		this._showModal.subscribe(function (showModal) {
			(showModal) ? this.showModal() : this.hideModal();
		}, this);

		// allow other views to switch form tabs
		this._focusTab = ko.observable().extend({notify: 'always'}).subscribeTo('LoginForm.tab', true);
		this._focusTab.subscribe(function focusTab(tabName) {
			var self = this;
			// If container isn't set, wait until the login form is rendered.
			if ( ! self.$container)
				return setTimeout(function () {
					self._focusTab(tabName);
				}, 0);

			var tab = this.$container.find('a[href="#tab-' + tabName + '"]');
			if (tab.length)
				tab.click();
		}, this);

		// Login form has 4 tabs but only 2 are visible at the same time.
		// when `registerUsernameMode` is set to true `#tab-complete-registration` and `#tab-logout` are visible.
		// otherwise they will remain hidden while `#tab-register` and `#tab-login` are visible
		this.registerUsernameMode = ko.observable().syncWith('LoginForm.registerUsernameMode', true);
		// Make sure the form is focused on the right tab when `registerUsernameMode` changes
		this.registerUsernameMode.subscribe(function (registerUsernameMode) {
			if (registerUsernameMode) {
				this._focusTab('complete-registration');
			} else {
				this._focusTab('register');
			}
		}, this);
		this.registerUsernameMode.valueHasMutated();
		// when submitting the register username form, we have the option to tell the server to
		// delay flash messages from being sent. This makes it convenient if we plan on redirecting
		// after `onSuccess` and dont want to populate the url with GET parameters
		this._delayFlashMessages = ko.observable('').subscribeTo('LoginForm.delayFlashMessages', true);
		this.delayFlashMessages = ko.pureComputed(function () {
			// use a blank string for false
			return (this._delayFlashMessages()) ? 'true' : '';
		}, this);
		// Ensure `registerUsernameMode` resets when user logs out
		this.user.isLoggedIn.subscribe(function (isLoggedIn) {
			if ( ! isLoggedIn) {
				this.registerUsernameMode(false);
			}
		}, this);

		// login with oauth using `LoginManager`
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

	// restores this component's position.
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

		if ( ! this.$modal) { // initialize modal on first call
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
		var additionalData = {
			form: $form,
			options: options
		};
		var response = Utils.shareResponse(data, 'LoginForm.beforeSubmit', this, additionalData);

		if (response.preventDefault)
			return false; // prevent form submission

		// when logging in using oauth, notify the user that we're verifying login
		if ($form == null) {
			Utils.remove.allMessages(function () {
				Utils.show.messages('#general-alert', 'Verifying login...', 'info');
			});
		}
	};

	LoginFormViewModel.prototype._onSuccess = function (data, textStatus, jqXHR, $form) {
		console.log('LoginForm onSuccess:', arguments);

		var response = Utils.shareResponse(data, 'LoginForm.onSuccess', this);
		if (response.preventDefault) // do nothing
			return;

		// If a username contains a `@`, set `registerUsernameMode` to true
		var username = data.result.user.username;
		if (username.indexOf('@') > -1) {
			this.registerUsernameMode(true);
		} else {
			if (this.user.username() != username) { // update UserViewModel
				ko.postbox.publish('User.loadData', data.result);
			}
			this.hideModal();
			this.registerUsernameMode(false);
		}
		this.user.isLoggedIn(true);

		// clear form input fields
		if ($form) {
			this.$container.find('form').find(':input').val('');
		}
		data = data.result;

		Utils.remove.allMessages(function () {
			Utils.show.messages('#general-alert', data['flashed_messages']);
		});
	};

	LoginFormViewModel.prototype._onFail = function (data, textStatus, errorThrown, form) {
		console.log('LoginForm onFail:', arguments);

		var response = Utils.shareResponse(data, 'LoginForm.onFail', this);
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

				// Set this components container
				component.$container = $(componentInfo.element);

				// clear any popovers messages before switching tabs
				component.$container.on('click', '[data-toggle="tab"]', function (e) {
					Utils.remove.popovers(component.$container, null, ':input');
				});

				// When the user clicks on the logout tab, notify the navbar component to logout user
				component.$container.on('click', 'a[href="#tab-logout"]', function (e) {
					ko.postbox.publish('Navbar.logout', true);
				});

				component.$container.on('click', 'form', function (e) {
					// Serialize login form to use ajax on submit
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