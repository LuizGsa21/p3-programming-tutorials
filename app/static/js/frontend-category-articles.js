requirejs([
	'common',
	'helpers/LoginManager',
	'view-models/UserViewModel',
	'view-models/BaseViewModel',
	'components/sidebar',
	'components/navbar-links'
], function (common, LoginManager, UserViewModel, BaseViewModel) {
	var $         = common.jquery,
		ko        = common.ko,
		koMapping = common.koMapping,
		Model     = common.Model,
		Utils     = common.Utils;

	// register navbar and login form components
	ko.components.register('navbar-links', {require: 'components/navbar-links'});
	ko.components.register('sidebar', {require: 'components/sidebar'});
	ko.components.register('app-footer', {require: 'components/footer'});

	// Load Google/Facebook OAuth scripts
	LoginManager.loadOAuth(Model.getData('loginManager'));
	ko.postbox.publish('Navbar.useLoginManager', true);


	var MainViewModel = function (data) {

		this.allowedKeys = ['user', 'articles', 'category'];
		console.log(this);
		this.mapping = {
			user: {
				create: function (options) {
					return new UserViewModel(options.data)
				}
			}
		};
		// call `updateTemplate()` to dynamically chose which template to render
		this.template = ko.observable();
		this.updateTemplate = function () {
			if (this.articles().length) {
				this.template({name: 'template-articles', foreach: this.articles});
			} else {
				this.template({name: 'template-empty'});
			}
		};

		this.loadData(data);
		this.updateTemplate();

		// fetch page data when user login state changes
		this.user.isLoggedIn.subscribe(function () {
			var self = this;
			$.ajax({
				url: window.location.href,
				success: function (data) {
					data = data.result;
					console.log(data);
					self.loadData(data);
					self.updateTemplate();
					Utils.updateTime();
					Utils.show.messages('#general-alert', data['flashed_messages']);
				},
				error: function (data) {
					if (data.responseJSON) {
						data = data.responseJSON.result;
						Utils.show.messages('#general-alert', data['flashed_messages']);
					}
				}
			});
		}, this);
	};

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;

	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);
	Utils.updateTime();

});


