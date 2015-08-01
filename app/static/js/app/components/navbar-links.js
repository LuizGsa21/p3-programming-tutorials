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
				// `name` and `url`. We will iterate through each item and add a isVisible observable
				// if the url is flagged.
				var link = options.data;
				var view = options.parent;
				//console.log(options);
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
			}
		}
	};

	var NavbarViewModel = function () {
		this.user = {
			isLoggedIn: ko.observable().syncWith('User.isLoggedIn', true)
		};
		this.useLoginManager = ko.observable();
		this.useLoginManager.subscribe(function (useLoginManager) {
			if (useLoginManager) {
				this.loginManager = LoginManager.getInstance();
			} else {
				this.loginManager = null;
			}
		}, this);
		this.useLoginManager.subscribeTo('Navbar.useLoginManager', true);


		// Flagged urls that change according to the current login state
		this.registeredUserLinks = ['Profile', 'Logout'];
		this.anonymousUserLinks = ['Register', 'Login'];

		this.onClick = function (link, event) {
			switch (link.name) {
				case 'Login':
				case 'Register':
					console.log('clicked');
					// notify the login form component to display itself in a modal
					ko.postbox.publish('LoginForm.tab', link.name.toLowerCase());
					ko.postbox.publish('LoginForm.showModal', true);
					break;
				case 'Logout':
					if (this.useLoginManager()) {
						this.logout();
					} else {
						return true; // use default link behaviour
					}

					break;
				default:
					return true; // use default link behaviour
			}

		}.bind(this);

		// load data from the model
		this.loadData();
		// notify other views the the navbar has been updated
		this.links.publishOn('Navbar.updatedLinks');

		ko.postbox.subscribe('Navbar.logout', function () {
			this.logout();
		}.bind(this));
	};

	NavbarViewModel.prototype.logout = function () {
		// logout user
		this.loginManager.logout({
			onSuccess: function (data, textStatus, jqXHR) {
				this.user.isLoggedIn(false); // update user login status
				var response = function () {
					return {
						view: this,
						data: data,
						preventDefault: false
					}
				}.bind(this);

				ko.postbox.publish('Navbar.onLogoutSuccess', response);

				if (response.preventDefault) // do nothing
					return;

				data = data.result;
				// clear all messages on page
				Utils.remove.allMessages(function () {
					// display new messages
					Utils.show.messages('#general-alert', data['flashed_messages']);
				});
			},
			onFail: function (data) {
				var response = function () {
					return {
						view: this,
						data: data,
						preventDefault: false
					}
				}.bind(this);

				ko.postbox.publish('Navbar.onLogoutFail', response);

				if (response.preventDefault) // do nothing
					return;

				// clear all messages on page
				Utils.remove.allMessages(function () {
					// display new messages
					Utils.show.messages('#general-alert', data['flashed_messages']);
				});
				// notify global topic in-case any subscribers want to handle the response
				ko.postbox.publish('Navbar.onLogoutFail', arguments);
			}

		}, this); // pass the current context
	};

	NavbarViewModel.prototype.loadData = function (navbar) {
		if (!navbar) {
			// load from Model
			navbar = { links: Model.getData('navbar') };
		} else {
			// unwrap navbar key
			if (navbar.hasOwnProperty('navbar'))
				navbar = navbar.navbar;
			navbar = { links: navbar };
		}
		koMapping.fromJS(navbar, mapping, this);
	};

	return {
		viewModel: NavbarViewModel,
		template: htmlTemplate
	};
});