define([
	'jquery',
	'knockout',
	'ko-mapping',
	'helpers/LoginManager',
	'models/Model',
	'text!./navbar-links.html',
	'_',
	'utils/Utils',
	'ko-postbox',
	'ko-custom-bindings'], function ($, ko, koMapping, LoginManager, Model, htmlTemplate, _, Utils) {


	var mapping = {
		links: {
			create: function (options) {
				// The navbar data is an array of objects that contain 2 properties
				// `name` and `url`. We will iterate through each item and add a isVisible observable.
				var link = options.data;
				var view = options.parent;
				if (_.contains(view.registeredUserLinks, link.name)) {
					// only visible when user is logged in
					link.isVisible = view.user.isLoggedIn;
				} else if (_.contains(view.anonymousUserLinks, link.name)) {
					// only visible when user is logged out
					link.isVisible = ko.pureComputed(function () { return !view.user.isLoggedIn(); }, view);
				} else {
					link.isVisible = true;
				}
				// if the link url is an array then we are dealing with a dropdown menu
				if (_.isArray(link.url)) {
					// currently there is only one dropdown menu and none of the links are flagged.
					// so set them all to true.
					_.each(link.url, function (value) {
						value.isVisible = true;
					});
				}
				return link;
			},
			key: function (link) {
				link = ko.unwrap(link);
				if (_.isArray(link.url)) {
					// join all the link names
					return _.map(link.url, function (link) {
						return ko.unwrap(link.name);
					}).join('');

				} else return ko.unwrap(link.name);
			}
		}
	};

	var NavbarViewModel = function () {
		var self = this;
		self.user = {
			isLoggedIn: ko.observable().syncWith('User.isLoggedIn', true)
		};
		self.useLoginManager = ko.observable();
		self.useLoginManager.subscribe(function (useLoginManager) {
			if (useLoginManager) {
				self.loginManager = LoginManager.getInstance();
			} else {
				self.loginManager = null;
			}
		}, self);
		self.useLoginManager.subscribeTo('Navbar.useLoginManager', true);

		// Flagged urls that change according to the current login state
		self.registeredUserLinks = ['Profile', 'Logout'];
		self.anonymousUserLinks = ['Register', 'Login'];

		self.onClick = function (link, event) {
			switch (link.name) {
				case 'Login':
				case 'Register':
					// notify the login form component to display itself in a modal
					ko.postbox.publish('LoginForm.tab', link.name.toLowerCase());
					ko.postbox.publish('LoginForm.showModal', true);
					break;
				case 'Logout':
					if (self.useLoginManager()) {
						self.logout();
					} else {
						return true; // use default link behaviour
					}
					break;
				default:
					return true; // use default link behaviour
			}

		};

		// load data from the model
		self.loadData();
		// let other views load data by publishing to `Navbar.loadData` topic
		ko.postbox.subscribe('Navbar.loadData', function (navbar) { self.loadData(navbar); });
		// notify other views that the navbar has been updated
		self.links.publishOn('Navbar.updatedLinks');
		// Allow other views to log user out by publishing to topic `Navbar.logout`
		ko.postbox.subscribe('Navbar.logout', function () { self.logout(); });
	};

	NavbarViewModel.prototype.logout = function () {
		// logout user
		this.loginManager.logout({
			onSuccess: function (data, textStatus, jqXHR) {
				this.user.isLoggedIn(false); // update user login status
				// notify topic in-case any subscribers want to handle the response
				var response = Utils.shareResponse(data, 'Navbar.onLogoutSuccess', this);
				if (response.preventDefault) // do nothing
					return;
				data = data.result;
				// clear all messages on page
				Utils.remove.allMessages(function () {
					// display new messages
					Utils.show.messages('#general-alert', data['flashed_messages']);
				});
			},
			onFail: function (data, textStatus) {
				// notify topic in-case any subscribers want to handle the response
				var response = Utils.shareResponse(data, 'Navbar.onLogoutFail', this);
				if (response.preventDefault) // do nothing
					return;

				if ( ! data.responseJSON) { // unknown error
					// display textStatus in an alert box
					Utils.show.messages('#general-alert', textStatus, 'danger');
				} else {
					data = data.responseJSON.result;

					var isResyncing = false;
					_.each(data['flashed_messages'], function (obj) {
						// notify the main view that the page needs a refresh
						if (obj.message.indexOf('You must be logged in to logout') > -1) {
							ko.postbox.publish('Global.pageRefresh', 'out of sync');
							isResyncing = true;
						}
					}, this);

					// clear all messages on page
					Utils.remove.allMessages(function () {
						// Dont display the alert message if we are re-syncing the page
						if (isResyncing) return;
						// display new messages
						Utils.show.messages('#general-alert', data['flashed_messages']);
					});
				}
			}

		}, this); // pass the current context
	};

	NavbarViewModel.prototype.loadData = function (navbar) {
		var links = { links: navbar || Model.getData('navbar') };
		koMapping.fromJS(links, mapping, this);
	};

	return {
		viewModel: NavbarViewModel,
		template: htmlTemplate
	};
});