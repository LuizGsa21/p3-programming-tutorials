define([
	'knockout',
	'models/Model',
	'text!./footer.html',
	'jquery',
	'enquire',
	'_'
], function (ko, Model, htmlTemplate, $, enquire, _) {

	var FooterViewModel = function (options) {

		this.user = {
			isLoggedIn: ko.observable().syncWith('User.isLoggedIn', true)
		};

		// `footer` will hold the footer container using `storeElement` custom binding
		this.footer = ko.observable();
		// `urlChunks` will contain the urls to be displayed in the footer's navigation section.
		// Each chunk will have its own `<ul>` parent.
		this.urlChunks = ko.observable();
		// Set default chunk size
		this.chunkSize = options.urlChunks || 4;

		if (options.links) { // use the provided links
			this.urlChunks(this.getChunks(options.links, this.chunkSize));
		} else {
			// use the links from the navbar
			this._links = ko.observable();
			// First subscribe to `_links` before subscribing it to the navbar `Navbar.updatedLinks`
			// in order to capture the initial value.
			this._links.subscribe(function (newValue) {
				var links = [];
				// flatten any nested urls since we wont be using a dropdown menu in the footer
				_.each(newValue, function flattenUrls(value) {
					if (_.isArray(value.url)) _.each(value.url, flattenUrls);
					else links.push(value);
				});
				// call updateURLs to filter out any hidden links and update `urlChunks`
				this.updateURLs(links);
			}, this);

			// subscribe to the navbar topic
			this._links.subscribeTo('Navbar.updatedLinks', true);

			// when the user's login state changes we must update the filtered urls
			this.user.isLoggedIn.subscribe(function () {
				// knockout notifies its subscribers synchronously and we can't guarantee
				// the links `isVisible` observables are updated before this method is called.
				// So set a timeout delay of 0 milliseconds before updating the urls.
				setTimeout(this.updateURLs.bind(this), 0);
			}, this);
		}

		// handle click event when user clicks on an url
		this.onClick = function (link, event) {
			switch (link.name) {
				case 'Login':
				case 'Register':
					// notify the login form component to display itself in a modal
					ko.postbox.publish('LoginForm.tab', link.name.toLowerCase());
					ko.postbox.publish('LoginForm.showModal', true);
					break;
				case 'Logout':
					ko.postbox.publish('Navbar.logout');
					break;
				default:
					return true; // use default link behaviour
			}

		}.bind(this);
		// wait until the this component is fully rendered before
		// initializing the sticky footer
		setTimeout(this.initStickyFooter.bind(this), 0)
	};

	FooterViewModel.prototype.updateURLs = function (links) {
		// we will be dividing the links into chunks so we need to exclude any hidden links
		// or else we will have an incorrect number of `<ul>` when rendering the template
		this.unfilteredURLs = links || this.unfilteredURLs;
		this.filteredURLs = _.filter(this.unfilteredURLs, function (value, index, list) {
			if (_.isFunction(value.isVisible))
				return value.isVisible();
			else return value.isVisible;
		});
		this.urlChunks(this.getChunks(this.filteredURLs, this.chunkSize));
	};

	FooterViewModel.prototype.getChunks = function (links, chunks) {
		var newArray = [];
		chunks = Math.max(1, chunks);
		for (var i = 0, length = links.length; i < length; i+=chunks) {
			newArray.push(links.slice(i, i + chunks));
		}
		return newArray;
	};
	FooterViewModel.prototype.initStickyFooter = function () {
		var $footer      = $(this.footer.elements),
			$body        = $('body'),
			$html        = $('html'),
			footerHeight = null; // Gets set on first footerSticky() call

		var footerSticky = function () {
			var newFooterHeight = $footer.outerHeight(true); // account for margin and padding
			var offset = footerHeight || 0;

			// Only update if the footer height has changed
			if (footerHeight === newFooterHeight) return;

			footerHeight = newFooterHeight; // update new height

			// remove non digits from padding-bottom
			var paddingBottom = $body.css('padding-bottom').replace(/[^-\d\.]/g, '') - offset;

			// add the new padding to body including the new footer height
			$body.css({
				position: 'static',
				paddingBottom: (paddingBottom + newFooterHeight) + 'px'
			});

			$html.css({
				position: 'relative',
				minHeight: '100%'
			});

			$footer.css({
				visibility: 'visible'
			});
		};

		// default bootstrap media queries
		var mediaQueries = [
			'screen and (min-width: 768px)',
			'screen and (min-width: 992px)',
			'screen and (min-width: 1200px)',
			'screen and (max-width: 480px)',
			'screen and (max-width: 767px)',
			'screen and (max-width: 991px)',
			'screen and (max-width: 1199px)'
		];

		// call footerSticky() when a new media query is triggered
		$.each(mediaQueries, function (i, query) {
			enquire.register(query, {
				match: footerSticky
			});
		});
	};


	return {
		viewModel: FooterViewModel,
		template: htmlTemplate
	}
});