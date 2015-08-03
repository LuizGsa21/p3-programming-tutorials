define(['knockout', 'ko-postbox'], function (ko) {

	return function (data, topic, sender) {
		data = {
			sender: sender,
			data: data,
			preventDefault: false
		};

		var response = function () {
			return data;
		};
		ko.postbox.publish(topic, response);

		return data;
	};
});