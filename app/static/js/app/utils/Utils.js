define([
	'utils/showMessages',
	'utils/removeMessages',
	'utils/updateTime'
], function (showMessages, removeMessages, updateTime) {
	return {
		show: showMessages,
		remove: removeMessages,
		updateTime: updateTime
	}
});