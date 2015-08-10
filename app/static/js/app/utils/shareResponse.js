define(['knockout', 'jquery', 'ko-postbox'], function (ko, $) {

	return function (data, topic, sender, additionalData) {
		data = {
			sender: sender,
			data: data,
			preventDefault: false
		};
		data = $.extend({}, data, additionalData || {});

		// When postbox serializes a DOM element it will throw an error saying:
		//   Uncaught SecurityError: Blocked a frame with origin "http://localhost:8000" from accessing
		//   a frame with origin "http://static.ak.facebook.com".....
		// to avoid this problem we will wrap the response in a function.
		var response = function () {
			return data;
		};
		ko.postbox.publish(topic, response);

		return data;
	};
});