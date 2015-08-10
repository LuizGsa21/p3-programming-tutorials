define([
	'knockout',
	'ko-mapping',
	'helpers/LoginManager',
	'ko-postbox'
], function (ko, koMapping) {
	"use strict";

	var mapping = {};

	function UserViewModel(user) {

		var self = this;
		// map the user data to this view model
		self.loadData = function (user) {
			// extract the user if we passed in a data containing the user key
			if (user.hasOwnProperty('user'))
				user = user.user;
			koMapping.fromJS(user, mapping, self);

			// Publish observables
			for (var key in self.__ko_mapping__.mappedProperties) if (self.hasOwnProperty(key)) {
				self[key].syncWith('User.' + key);
			}
		};

		self.loadData(user);

		ko.postbox.subscribe('User.loadData', function (data) {
			if ( ! data) return;
			self.loadData(data)
		});
	}

	return UserViewModel;
});