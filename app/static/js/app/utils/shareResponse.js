define(['knockout', 'jquery', 'ko-postbox'], function (ko, $) {

	return function (data, topic, sender, additionalData) {
		data = {
			sender: sender,
			data: data,
			preventDefault: false
		};
		data = $.extend({}, data, additionalData || {});
		var response = function () {
			return data;
		};
		ko.postbox.publish(topic, response);

		return data;
	};
});