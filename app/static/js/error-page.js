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

	var model = Model.getData();
	// Remove the login and register links from the navbar
	model.navbar = _.filter(model.navbar, function (value) {
		return ! (value.name == 'Login' || value.name == 'Register');
	});

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
	};

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;
	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);
});