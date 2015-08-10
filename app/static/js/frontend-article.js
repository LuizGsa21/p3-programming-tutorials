requirejs([
	'common',
	'helpers/LoginManager',
	'view-models/UserViewModel',
	'view-models/CommentViewModel',
	'view-models/BaseViewModel',
	'components/sidebar',
	'components/footer',
	'components/navbar-links'
], function (common, LoginManager, UserViewModel, CommentViewModel, BaseViewModel) {
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

	var addComment = new CommentViewModel({
		articleId: Model.getData('article.id'),
		formName: 'AddCommentForm'
	});
	addComment.selector = '#add-comment-media';

	addComment.user = {
		avatar: ko.observable().subscribeTo('User.avatar', true)
	};

	addComment.hideForm = function (callback) {
		console.log(this);
		// Hide the form
		$(this.isFormVisible.elements).slideUp(200, function () {
			this.isFormVisible(false);
			this.formSubject('');
			this.formMessage('');
			if (_.isFunction(callback)) {
				callback();
			}
		}.bind(this))
	};

	var MainViewModel = function (data) {

		this.allowedKeys = ['user', 'comments', 'article'];
		this.mapping = {
			comments: {
				create: function (options) {
					return new CommentViewModel(options.data)
				},
				key: function (comment) {
					var id = ko.utils.unwrapObservable(comment.id);
					var lastModified = ko.utils.unwrapObservable(comment.lastModified);
					return id + 'timestamp' + lastModified + comment.action;
				}
			},
			user: {
				create: function (options) {
					return new UserViewModel(options.data)
				}
			}
		};

		this.loadData(data);

		this.addComment = addComment;

		// Refresh the page using ajax
		this.updatePage = function () {
			var self = this;
			$.ajax({
				url: window.location.href,
				success: function (data) {
					data = data.result;
					self.loadData(data);
					Utils.show.messages('#general-alert', data['flashed_messages']);
				},
				error: function (data) {
					if (data.responseJSON) {
						data = data.responseJSON.result;
						Utils.show.messages('#general-alert', data['flashed_messages']);
					}
				}
			});
		}.bind(this);

		// Update page when the user is logged in AND doesnt need to register a username.
		this.registerUsernameMode = ko.observable().subscribeTo('LoginForm.registerUsernameMode', true);
		this.isRegistered = ko.pureComputed(function () {
			return this.user.isLoggedIn() && ! this.registerUsernameMode();
		}, this);
		this.isRegistered.subscribe(function (isRegister) {
			// update the page
			if (isRegister)
				this.updatePage();
		}, this);

		// Update the page when the user logs out
		this.user.isLoggedIn.subscribe(function (isLoggedIn) {
			if (isLoggedIn == false) { // update the page
				this.updatePage();
			}
		}, this);

		// update comments after the user submits a comment or reply
		this.onSuccess = ko.observable().subscribeTo('Comment.onSuccess');
		this.onSuccess.subscribe(function (response) {
			if (_.isFunction(response)) // unwrap the response
				response = response();
			var self = this;
			Utils.remove.allMessages(function () {
				self.loadData(response.data.result);
			});
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

	MainViewModel.prototype = Object.create(BaseViewModel.prototype);
	MainViewModel.prototype.constructor = MainViewModel;

	var mainViewModel = new MainViewModel(Model.getData());
	ko.applyBindings(mainViewModel);
	Utils.updateTime();
});


