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
		// make the form visible
		ko.postbox.publish('LoginForm.visible', true);
		// Set the form in register username mode
		ko.postbox.publish('LoginForm.registerUsernameMode', true);
		// Tell the server to delay flash messages because we will be redirecting upon success
		ko.postbox.publish('LoginForm.delayFlashMessages', true);
		// redirect back to homepage
		ko.postbox.subscribe('LoginForm.onSuccess', function (response) {
			window.location.href = '/';
		});
		ko.postbox.subscribe('Global.pageRefresh', function (reason) {
			if (reason == 'out of sync') {
				location.reload();
			}
		});
	};

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;
	var mainViewModel = new MainViewModel(Model.getData());

	ko.applyBindings(mainViewModel);
});