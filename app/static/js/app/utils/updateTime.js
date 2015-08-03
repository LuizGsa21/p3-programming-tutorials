define(['jquery', 'momentjs'], function ($, moment) {
	function updateTime($elements) {
		// update the entire page if no arguments were given
		if (!$elements)
			$elements = $('[data-time]');

		$elements.each(function (i) {
			var $this = $(this), utcTime, localTime;
			// time format: 2015-08-03T14:59:38.803775+00:00
			utcTime = $this.data('time');
			// Convert to "YYYY-MM-DDTHH:mm:ss" so `moment` wont round up when
			// calling `fromNow()` which would sometimes change its output
			// from "a few seconds ago" to "in a few seconds"
			utcTime = utcTime.split('.')[0];
			localTime = moment.utc(utcTime);
			this.innerHTML = moment(localTime).fromNow();
		});
	}

	return updateTime;
});