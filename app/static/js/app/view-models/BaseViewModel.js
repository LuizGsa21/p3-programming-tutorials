define([
	'jquery',
	'knockout',
	'ko-mapping',
	'utils/Utils',
	'_',
	'ko-postbox',
	'jquery.form'
], function ($, ko, koMapping, Utils, _) {

	var BaseViewModel = function (data) {
		// keys to filter when calling `loadData()`
		this.allowedKeys = [];
		this.mapping = {};
	};

	BaseViewModel.prototype.loadData = function (data) {
		if ( ! _.isObject(data))
			throw Error('BaseMainViewModel loadData: data argument must be an object.');

		var filteredData = {};
		if (this.allowedKeys.length == 0) {
			// if no allowed keys are set assume there's no restrictions
			filteredData = data;
		} else {
			_.each(this.allowedKeys, function (key) {
				if (data[key])
					this[key] = data[key];
			}, filteredData);
		}

		koMapping.fromJS(filteredData, this.mapping, this);
	};

	return BaseViewModel;
});