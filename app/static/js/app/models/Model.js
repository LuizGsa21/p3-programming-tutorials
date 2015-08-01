define(['jquery'], function ($) {

	var model = {};

	var traverse = function traverse(keys, obj, index) {
		var key = keys[index++];
		if (!obj.hasOwnProperty(key))
			throw Error('Model.traverse: could not find key: ' + key);

		if (index == keys.length)
			return {
				parent: obj,
				key: key,
				value: obj[key]
			};
		return traverse(keys, obj[key], index);
	};

	return {
		getData: function (key, delimiter) {
			// set default delimiter
			if (typeof delimiter != 'string')
				delimiter = '.';

			if (arguments.length == 0)
				return model;

			var data = traverse(key.split(delimiter), model, 0);
			return data.value;
		},
		initData: function initData(data) {
			model = data;
		},
		updateData: function (key, data, delimiter) {
			if (arguments.length == 1) // the key is the data
				return $.extend(model, key) && true;

			// set default delimiter
			if (typeof delimiter != 'string')
				delimiter = '.';

			var obj = traverse(key.split(delimiter), model, 0);
			return obj.parent[obj.key] = data;
		},
		hasKey: function () {
			try {
				this.getData.apply(this, arguments);
				return true;
			} catch (error) {
				return false;
			}
		}
	};
});