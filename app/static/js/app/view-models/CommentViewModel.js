define([
	'jquery',
	'knockout',
	'ko-mapping',
	'utils/Utils',
	'ko-postbox',
	'jquery.form'
], function ($, ko, koMapping, Utils) {

	var _mapping = {
		copy: ['formName','action','id','parentId','articleId','dateCreated']
	};

	var CommentViewModel = function (comment, mapping) {

		CommentViewModel.usernameByCommentId[comment.id] = comment.username;

		// Is this a comment or a reply ?
		this.isComment = comment.parentId == null;
		this.editable = comment.action == 'Edit';
		this.selector = '#comment-' + comment.id;

		this.recipientUsername = (this.isComment) ? null : CommentViewModel.usernameByCommentId[comment.parentId];

		// don't render the form template until the user decides to edit or reply
		this.renderForm = ko.observable(false);

		this.isFormVisible = ko.observable(false);

		this.isEditing = ko.observable(false);

		if (mapping == undefined) // use default mapping
			mapping = _mapping;

		// set observables
		koMapping.fromJS(comment, mapping, this);
		//console.log(this);
		this.deletedUser = ko.observable((comment.username == 'Deleted User'));
		this.btnTriggerText = ko.pureComputed(function () {
			if (this.isFormVisible())
				return this.editable ? 'Save' : 'Submit';
			else
				return this.action;
		}, this);

		this.btnTriggerCSS = ko.pureComputed(function () {
			if (this.editable && ! this.isFormVisible())
				return 'btn btn-warning';
			else
				return 'btn btn-primary';
		}, this);
	};

	CommentViewModel.usernameByCommentId = {};

	CommentViewModel.prototype.lazyInit = function() {
		// initialize form fields
		if ( ! this.editable) {
			this.formParentId = this.id;
		} else {
			this.formId = this.id;
		}
		this.formSubject = ko.observable('');
		this.formMessage = ko.observable('');
		this.formArticleId = this.articleId;
		// render the form template
		this.renderForm(true);
	};

	CommentViewModel.prototype.deletedUserMessage = function () {
		var $mediaBody = $(this.isFormVisible.elements).closest('.media-body');
		console.log($mediaBody);
		Utils.remove.allMessages($mediaBody, function () {
			Utils.show.messages($mediaBody, 'This user no longer exists', 'danger');
		});

	};
	CommentViewModel.prototype.showForm = function(view, event) {

		if (this.deletedUser())
			return this.deletedUserMessage();

		if ( ! this.renderForm()) {
			this.lazyInit();
		}
		console.log(this);
		console.log(arguments);
		if (this.editable) {
			// prepopulate the form fields
			this.formSubject(this.subject());
			this.formMessage(this.message());

			// start form animation.
			// Since we are editing we will hide the content first
			$(this.isEditing.elements).fadeOut(200, function () {
				$(this.isFormVisible.elements).fadeIn(200, function () {
					this.isEditing(true);
				}.bind(this));
				this.isFormVisible(true);
			}.bind(this));

		} else {
			// start form animation
			$(this.isFormVisible.elements).slideDown(200, function () {
				this.isFormVisible(true);
			}.bind(this));
		}
	};
	CommentViewModel.prototype.hideForm = function(callback) {
		if (this.editable) {
			// Hide the form then show the content
			$(this.isFormVisible.elements).fadeOut(200, function () {
				this.isFormVisible(false);
				$(this.isEditing.elements).fadeIn(200, function () {
					this.isEditing(false);
					if (_.isFunction(callback)) {
						callback();
					}
				}.bind(this));
			}.bind(this));
		} else {
			// Hide the form
			$(this.isFormVisible.elements).fadeOut(200, function () {
				this.isFormVisible(false);
				if (_.isFunction(callback)) {
					callback();
				}
			}.bind(this))
		}
	};

	CommentViewModel.prototype.getContainerAttributes = function() {
		return {
			'id': this.selector.substring(1),
			'class': (this.isComment) ? 'media' : 'reply media depth-1'
		};
	};

	CommentViewModel.prototype.submitForm = function(view, event) {

		if ( ! this.$form) { // setup form before submission
			this.$container = $(event.currentTarget).closest('.media');
			this.$form = this.$container.find('form');
			this.$form.ajaxForm({
				csrfHeader: true, // csrf protection
				dataType: 'json',
				beforeSubmit: this._beforeSubmit.bind(this),
				success: this._onSuccess.bind(this),
				error: this._onFail.bind(this)
			});
		}

		this.$form.submit();
	};

	CommentViewModel.prototype._beforeSubmit = function (data, form, options) {
		// When postbox serializes a DOM element it will throw an error saying:
		//   Uncaught SecurityError: Blocked a frame with origin "http://localhost:8000" from accessing
		//   a frame with origin "http://static.ak.facebook.com".....
		// to avoid this problem we will wrap the response in a function.
		var response = function () {
			return {
				view: this,
				data: data,
				form: form,
				options: options,
				preventDefault: false
			}
		}.bind(this);
		ko.postbox.publish('Comment.beforeSubmit', response);

		if (response.preventDefault)
			return false; // prevent form submission
	};

	CommentViewModel.prototype._onSuccess = function (data) {
		var response = function () {
			return {
				view: this,
				data: data
			}
		}.bind(this);
		// hide the form and pass the response to the main view model
		// to update the page
		this.hideForm(function () {
			ko.postbox.publish('Comment.onSuccess', response);
		});

	};

	CommentViewModel.prototype._onFail = function (data) {
		//console.log(data);
		if (data.responseJSON) {
			data = data.responseJSON.result;
			Utils.remove.allMessages(function () {
				Utils.show.messages(this.$form, data['flashed_messages'], { action: 'before' });
			}.bind(this));
		}
	};

	return CommentViewModel;
});