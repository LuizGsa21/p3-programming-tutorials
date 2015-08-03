define([
	'utils/showMessages',
	'utils/removeMessages',
	'utils/updateTime',
	'utils/shareResponse'
], function (showMessages, removeMessages, updateTime, shareResponse) {
	return {
		show: showMessages,
		remove: removeMessages,
		updateTime: updateTime,
		shareResponse: shareResponse
	}
});