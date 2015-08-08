requirejs([
	'common',
	'modals/BaseModal',
	'modals/ArticleModal',
	'modals/AvatarModal',
	'modals/CategoryModal',
	'modals/ProfileModal',
	'modals/UserModal',
	'cropper'
], function (common, BaseModal, ArticleModal, AvatarModal, CategoryModal, ProfileModal, UserModal) {
	'use strict';
	var $         = common.jquery,
		BaseViewModel = common.BaseViewModel,
		UserViewModel = common.UserViewModel,
		ko        = common.ko,
		Model     = common.Model;

	// register navbar component
	ko.components.register('navbar-links', {require: 'components/navbar-links'});
	ko.components.register('app-footer', {require: 'components/footer'});

	/**
	 * Base table class
	 *
	 * @constructor
	 * @borrows {BaseViewModel.loadData}
	 */
	var BaseTable = function () {
		var self = this;
		self.isVisible = ko.observable(true);

		self.allowedKeys = []; // keys to filter when using koMapping
		self.mapping = {};
		self.loadData = BaseViewModel.prototype.loadData;

		// Message to display when the table is empty
		self.emptyTableText = ko.observable('Empty table');


		// url used to fetch table data
		self.fetchURL = '';
		/**
		 * Displays this table. If useCache is false it will fetch the table data by call `fetch()`
		 *
		 * @param {boolean} [useCache=false]
		 */
		self.show = function (useCache) {
			self.isVisible(true);
			// use `===` comparison in case this method is called by a knockout event
			if (useCache === true) return;
			self.fetch();
		};

		/**
		 * Hides this table.
		 */
		self.hide = function () { self.isVisible(false); };

		/**
		 * Toggles this table visibility state.
		 */
		self.toggle = function () { self.isVisible() ? self.hide() : self.show(); };

		/**
		 * Called by `fetch()` upon success.
		 * Maps the server response to this table using `loadData()`.
		 *
		 * @param {Object} data - response from server
		 */
		self.onSuccess = function (data) { self.loadData(data.result); };

		/**
		 * Called by `fetch()` upon fail.
		 *
		 * @abstract
		 * @param {Object} data - response from server
		 */
		self.onFail = function (data) {};

		/**
		 *	Fetches the table data. If 0 arguments are provided it will use
		 *	this tables `fetchURL` `onSuccess` and `onFail`.
		 *
		 * @param {string} [url] - URL to use on request
		 * @param {Function} [onSuccess] - called if request was successful
		 * @param {Function} [onFail] - called if request failed
		 */
		self.fetch = function (url, onSuccess, onFail) {
			if (arguments.length == 0) {
				url = self.fetchURL;
				onSuccess = self.onSuccess;
				onFail = self.onFail;
			}
			$.ajax({
				url: url,
				type: 'GET',
				success: onSuccess,
				error: onFail
			});
		};
	};

	/**
	 * Creates an article table.
	 * Uses `/api/articles/author/<int:id>` and overrides `modal.onSuccess()` to automatically update the table content.
	 *
	 * @param {observableArray} [articles] - articles to display on this table
	 * @param {ArticleModal} [modal] - the modal used to perform CRUD operations in the article.
	 * @param {number} [userID] - user id to use when fetching user articles
	 * @constructor
	 * @augments {BaseTable}
	 */
	var ArticleTable = function (articles, modal, userID) {
		BaseTable.call(this);
		var self = this;
		self.articles = articles || ko.observableArray();
		self.modal = modal || new ArticleModal();
		// override the modals onSuccess to update this table
		self.modal.onSuccess = function () { self.fetch(); };


		// set keys to filter when mapping server response
		self.allowedKeys = ['articles'];
		self.fetchURL = '/api/articles/author/' + userID;
		self.emptyTableText = ko.observable('No published tutorials');

		/**
		 * Updates the `fetchURL` to use the given `userID`
		 * @param {number} userID
		 */
		self.updateFetchURL = function (userID) {
			self.fetchURL = '/api/articles/author/' + userID;
		};

		// Update `emptyTableText` prior to calling `BaseTable.fetch()`
		self.fetch = _.wrap(self.fetch, function (fetch, data) {
			self.emptyTableText('Fetching user articles...');
			fetch.apply(self, Array.prototype.slice.call(arguments, 1));
		});

		// Update `emptyTableText` prior to calling `BaseTable.onSuccess()`
		self.onSuccess = _.wrap(self.onSuccess, function (onSuccess) {
			self.emptyTableText('No published articles');
			onSuccess.apply(self, Array.prototype.slice.call(arguments, 1))
		});

		/**
		 * Called by `fetch()` upon fail.
		 * Handle on fail response by emptying this table and updating `emptyTableText`
		 * @overrides
		 */
		self.onFail = function (data) {
			self.articles([]);
			self.emptyTableText('Failed to fetch user articles.');
		};
	};

	/**
	 * Creates a user table.
	 * Uses `/api/users/all` and overrides `modal.onSuccess()` to automatically update the table content.
	 *
	 * @param {observableArray} [users] - users to display on this table
	 * @param {UserModal} [modal] - the modal used to edit and delete user
	 * @constructor
	 * @augments {BaseTable}
	 */
	var UserTable = function (users, modal) {
		BaseTable.call(this);
		var self = this;
		self.users = users || ko.observableArray();
		self.modal = modal || new UserModal();
		// override the modals onSuccess to update this table
		self.modal.onSuccess = function () { self.fetch(); };

		// set keys to filter when mapping server response
		self.allowedKeys = ['users'];
		self.fetchURL = '/api/users/all';
		self.emptyTableText = ko.observable('No registered users found other than yourself ;)');


		// Update `emptyTableText` prior to calling `BaseTable.fetch()`
		self.fetch = _.wrap(self.fetch, function (fetch) {
			self.emptyTableText('Fetching registered users...');
			fetch.apply(self, Array.prototype.slice.call(arguments, 1));
		});

		// Update `emptyTableText` prior to calling `BaseTable.fetch()`
		self.onSuccess = _.wrap(self.onSuccess, function (onSuccess) {
			self.emptyTableText('No registered users found other than yourself ;)');
			onSuccess.apply(self, Array.prototype.slice.call(arguments, 1))
		});

		/**
		 * Called by `fetch()` upon fail.
		 * Handle on fail response by emptying this table and updating empty table text.
		 * @overrides
		 */
		self.onFail = _.wrap(self.onFail, function (onFail) {
			self.emptyTableText('Failed to fetch registered users.');
			self.users([]); // empty out the table
			onFail.apply(self, Array.prototype.slice.call(arguments, 1))
		});

	};

	/**
	 * Create a profile table
	 * Uses `/users/<int:id>` and overrides `modal.onSuccess()` to automatically update the table content.
	 *
	 * @param {observable} user - user to display on this table
	 * @param {ProfileModal} [modal] - modal used to edit user
	 * @constructor
	 */
	var ProfileTable = function (user, modal) {
		var self = this;
		BaseTable.call(this);
		self.user = user;
		// set keys to filter when mapping server response
		self.allowedKeys = ['user'];
		self.fetchURL = '/api/users/' + ko.unwrap(user.id);

		self.modal = modal || new ProfileModal();
		// override the modals onSuccess to update this table
		self.modal.onSuccess = function () { self.fetch(); };
	};

	/**
	 * Creates an admin view.
	 *
	 * @constructor
	 */
	var AdminViewModel = function () {
		var self = this;
		// create user and article table for the admin section
		self.userTable = new UserTable();
		self.articleTable = new ArticleTable();

		// hide both tables by default
		self.userTable.isVisible(false);
		self.articleTable.isVisible(false);

		// Create category modal
		self.categoryModal = new CategoryModal();

		// Configure the admin options buttons
		self.btnCategoryText = ko.observable('Manage Categories');
		self.btnUserTableText = ko.pureComputed(function () {
			return self.userTable.isVisible() ? 'Hide Users' : 'Show Users';
		});

		self.articleTableTitle = ko.observable();
		// This method should be called by a knockout event providing the
		// `event.target` to get the user id to fetch the articles
		// and username to update table title
		self.showArticlesByUserID = function (view, event) {
			var data = ko.dataFor(event.target);
			// update the table url to fetch the user articles
			self.articleTable.updateFetchURL(data.id());
			// update the table title to contain this user's username
			self.articleTableTitle('Articles by ' + data.username());
			// hide the user table prior to showing the article table
			self.userTable.hide();
			self.articleTable.show();
		};

		self.hideUserTable = function () { self.userTable.hide(); };

		/**
		 * Show the user table while ensuring the article table is hidden.
		 *
		 * @param {boolean} [useCache=false] - if set to true the table will not call `fetch()` after it is shown.
		 */
		self.showUserTable = function (useCache) {
			// make sure the article table is hidden
			// before displaying the user table
			if (self.articleTable.isVisible()) {
				self.articleTable.hide();
			}
			self.userTable.show(useCache === true)
		};

		/**
		 * Toggles the user table while ensuring the article table is hidden.
		 *
		 * @param {boolean} [useCache=false] - if set to true the table will not call `fetch()` after it is shown.
		 */
		self.toggleUserTable = function (useCache) {
			if (self.userTable.isVisible())
				self.hideUserTable();
			else self.showUserTable(useCache === true);
		};

	};

	/**
	 * Creates the main view.
	 *
	 * @param {Object} data - object used to initialize main view.
	 * @constructor
	 * @augments {BaseViewModel}
	 */
	var MainViewModel = function (data) {
		var self = this;
		// set filtered keys used in `loadData()`
		self.allowedKeys = ['user', 'articles'];
		// set mapping used in `loadData()`
		self.mapping = {
			user: {
				create: function (options) {
					return new UserViewModel(options.data)
				}
			}
		};

		self.loadData(data);

		// set the global modal observable
		self.modal = BaseModal.modal;

		// Add avatarModal to main view to edit users avatar
		self.avatarModal = new AvatarModal();
		// we will create an instance of `ArticleModal` in the main view to "add" new articles
		// and share it with the Article table to perform "edit" and "delete" actions.
		self.articleModal = new ArticleModal();
		self.articleTable = new ArticleTable(self.articles, self.articleModal, self.user.id());

		self.profileTable = new ProfileTable(self.user);

		// setup admin view
		if (self.user.isAdmin()) {
			self.admin = new AdminViewModel();
		} else {
			self.admin = {};
		}

		self.onSuccess = ko.observable().subscribeTo('Modal.onSuccess');
		// Listen in to all modal's `onSuccess` response. if we get a response that contains
		// an updated `navbar` we will notify the navbar component to update itself
		self.onSuccess.subscribe(function (response) {
			if (_.isFunction(response))
				response = response();
			var result = response.data.result;
			if (result.navbar) { // Update the navbar component
				ko.postbox.publish('Navbar.loadData', result.navbar);
			}

		});
	};
	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;

	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);

	// Prevent the users from submitting the form when pressing the enter key on an input field.
	$(document).on('submit', 'form', function (e) {
		e.preventDefault();
	});
});