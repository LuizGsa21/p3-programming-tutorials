define([
	'knockout',
	'ko-mapping',
	'helpers/LoginManager',
	'ko-postbox'
], function (ko, koMapping) {
	"use strict";

	var mapping = {};

	function UserViewModel(user) {

		// map the user data to this view model
		this.loadData = function (user) {
			// extract the user if we passed in a data containing the user key
			if (user.hasOwnProperty('user'))
				user = user.user;
			koMapping.fromJS(user, mapping, this);

			// Publish observables
			for (var key in this.__ko_mapping__.mappedProperties) if (this.hasOwnProperty(key)) {
				// TODO: only publish required keys
				this[key].syncWith('User.' + key);
			}
		}.bind(this);

		this.loadData(user);
	}

	return UserViewModel;
});