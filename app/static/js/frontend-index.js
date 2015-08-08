requirejs([
	'common',
	'helpers/LoginManager',
	'view-models/BaseViewModel',
	'view-models/UserViewModel',
	'components/login-form',
	'components/navbar-links'
], function (common, LoginManager, BaseViewModel, UserViewModel) {
	var $         = common.jquery,
		ko        = common.ko,
		koMapping = common.koMapping,
		Model     = common.Model,
		Utils     = common.Utils;

	// register navbar and login form components
	ko.components.register('navbar-links', {require: 'components/navbar-links'});
	ko.components.register('login-form', {require: 'components/login-form'});
	ko.components.register('app-footer', {require: 'components/footer'});

	// Load Google/Facebook OAuth scripts
	LoginManager.loadOAuth(Model.getData('loginManager'));
	ko.postbox.publish('Navbar.useLoginManager', true);

	var MainViewModel = function (data) {
		this.allowedKeys = ['user'];
		this.mapping = {
			user: {
				create: function (options) {
					return new UserViewModel(options.data)
				}
			}
		};

		this.loadData(data);

		// We only want to make the login form visible for anonymous users.
		// The login form component uses knockout's fadeVisible binding when fading in/out.
		// However we want it to stay in sync with the main logo animation and
		// trying to keep 2 animations in sync using knockout has become a tedious task.
		// So we will fallback to using jquery when dealing with more than one element.

		// set its initial value to true (visible)
		this.showLoginForm = ko.observable(true).publishOn('LoginForm.visible');

		// show/hide the form using jquery when the user's login state changes
		this.user.isLoggedIn.subscribe(function (isLoggedIn) {
			if (isLoggedIn) {
				// hide the login/registration form using the parent container
				$('#login-form-container').parent().fadeOut(500, function () {
					// center the main website logo
					$('#main-logo-container').animate({width: '100%'}, 500, function () {
						$(this).attr('class', 'col-xs-12');
					});
				});
			} else {
				// make room for login/register form
				$('#main-logo-container').animate({width: '50%'}, 500, function () {
					$(this).attr('class', 'col-sm-6 hidden-xs');
					// display login/register form
					var $formContainer = $('#login-form-container');
					//$formContainer.attr('style', '');
					$formContainer.parent().fadeIn(500);
				});
			}
		}, this);

		var self = this;
		ko.postbox.subscribe('Global.pageRefresh', function (reason) {
			if (reason == 'out of sync') {
				$.ajax(window.location.href, {
					success: function (data) {
						self.loadData(data.result)
					}
				});
			}
		});
	};

	// Scroll to the 2nd section on the page when clicking the `Learn More` link
	$('a[href^="#community"]').on('click', function (e) {
		e.preventDefault();
		var selector = this.getAttribute('href');
		var $target = $(selector);
		if ($target.length) {
			$('html, body').stop().animate({
				scrollTop: $target.offset().top
			}, 900, 'swing');
		}
	});

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;
	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);
});