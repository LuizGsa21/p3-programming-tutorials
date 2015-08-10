define([
	'utils/showMessages',
	'utils/removeMessages',
	'utils/shareResponse'
], function (showMessages, removeMessages, shareResponse) {
	return {
		show: showMessages,
		remove: removeMessages,
		shareResponse: shareResponse
	}
});