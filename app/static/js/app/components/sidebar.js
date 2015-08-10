define([
	'knockout',
	'text!./sidebar.html',
	'ko-postbox',
	'components/login-form'
],function (ko, htmlTemplate) {

	ko.components.register('login-form', { require: 'components/login-form' });

	var SidebarViewModel = function () {
		this.user = {
			isLoggedIn: ko.observable().subscribeTo('User.isLoggedIn', true),
			firstName: ko.observable().subscribeTo('User.firstName', true),
			lastName: ko.observable().subscribeTo('User.lastName', true),
			username: ko.observable().subscribeTo('User.username', true),
			avatar: ko.observable().subscribeTo('User.avatar', true),
			fullname: ko.pureComputed(function () {
				// display the user's username if first and last name aren't set
				if (this.user.firstName() == null || this.user.lastName()) {
					return this.user.username();
				} else {
					return this.user.firstName() + ' ' + this.user.lastName();
				}

			}, this),
			profile: '/user/profile/'
		};
		// Get notified if the form is visible after animation
		this.formVisibleAA = ko.observable().subscribeTo('LoginForm.visibleAA', true);

		this.registerUsernameMode = ko.observable().subscribeTo('LoginForm.registerUsernameMode', true);

		// set a condition for when to show or hide the profile
		this.profile = {
			isVisible: ko.computed(function () {
				return this.user.isLoggedIn() && !this.formVisibleAA() && ! this.registerUsernameMode();
				// add a sub-observable to be updated after animation is complete
			}, this).extend({ afterAnimation: 'fadeVisible' })
		};

		// set a condition of when to show or hide the login form
		this.formVisible = ko.computed(function () {
				// always show the form when its in registerUsernameMode
			return this.registerUsernameMode() ||
				// make sure the profile is hidden and that the user is logged out
				(!this.profile.isVisible.afterAnimation() && !this.user.isLoggedIn());
		}, this);
		// notify the LoginForm when to show/hide itself
		this.formVisible.publishOn('LoginForm.visible');
	};


	return {
		viewModel: SidebarViewModel,
		template: htmlTemplate
	}
});