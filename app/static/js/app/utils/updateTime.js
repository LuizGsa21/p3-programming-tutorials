define(['jquery', 'momentjs'], function ($, moment) {
	function updateTime($elements) {
		// update the entire page if no arguments were given
		if (!$elements)
			$elements = $('[data-time]');

		$elements.each(function (i) {
			var $this = $(this), localTime;
			// parse utc time to local time
			localTime = moment.utc($this.data('time'));
			this.innerHTML = moment(localTime).fromNow();
		});
	}

	return updateTime;
});