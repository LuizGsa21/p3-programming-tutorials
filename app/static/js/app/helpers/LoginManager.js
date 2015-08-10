define(['jquery', 'jquery.form'], function () {

	function LoginManager(data) {
		if (LoginManager.prototype._singletonInstance) // return singleton instance
			return LoginManager.prototype._singletonInstance;

		if (!data)
			throw new Error("LoginManager: data parameter is required.");

		// set and verify that all required data was given
		this._setData(data);

		// Load google SDK
		this._googleInit();

		// Load facebook SDK
		this._facebookInit();

		// set singleton
		LoginManager.prototype._singletonInstance = this;

	}

	/**
	 * Verifies that all required properties were provided by `data`.
	 * Throws an Error if a key is missing from the `requiredKeys`.
	 *
	 * @param {Object} data - the object containing the oauth data
	 * @private
	 */
	LoginManager.prototype._setData = function _setData(data) {
		var requiredKeys = [
			'googleClientId', 'googleLoginUrl', 'facebookClientId',
			'facebookLoginUrl', 'githubLoginUrl', 'logoutUrl', 'loginUrl', 'csrfToken'
		];
		for (var i = 0; i < requiredKeys.length; i++) {
			var key = requiredKeys[i];
			if (data[key])
				this['_' + key] = data[key]; // add _ prefix to resemble a private variable
			else
				throw new Error("LoginManager: key - " + key + " is missing");
		}
	};

	/**
	 * Logs in user with the given `provider`.
	 *
	 * @param {string} provider - options "google", "facebook", "github"
	 * @param {Object} callbacks - an object to be invoked `beforeSubmit`, `onSuccess`, `onFail`
	 * @param {Object} thisArg - the context to use when invoking `callbacks`
	 */
	LoginManager.prototype.login = function login(provider, callbacks, thisArg) {

		// Set the `thisArg` context and empty placeholders
		// if not all 3 callbacks were provided (`beforeSubmit`, `onSuccess`, `onFail`)
		this._configureCallbacks(callbacks, thisArg);

		// find out the oauth provider
		if (provider.indexOf('google') > -1)
			provider = this._googleLogin(callbacks);
		else if (provider.indexOf('facebook') > -1)
			provider = this._facebookLogin(callbacks);
		else if (provider.indexOf('github') > -1)
			provider = this._githubLogin(callbacks);

		else throw new Error('Unknown login provider');
	};

	/**
	 * Logs out user
	 *
	 * @param {Object} callbacks - an object to be invoked `onSuccess`, `onFail`
	 * @param {Object} thisArg - the context to use when invoking `callbacks`
	 */
	LoginManager.prototype.logout = function logout(callbacks, thisArg) {
		this._configureCallbacks(callbacks, thisArg);
		$.ajax({
			url: this._logoutUrl,
			csrfHeader: true,
			type: 'POST',
			success: callbacks.onSuccess,
			error: callbacks.onFail
		});
	};

	/**
	 * Initializes google oauth login.
	 * Sets `window.googleAsyncInit` callback function and dynamically loads google api client.
	 * @private
	 */
	LoginManager.prototype._googleInit = function _googleInit() {

		if (window.googleAsyncInit)
			throw new Error("LoginManager: googleAsyncInit is already initialized.");

		window.googleAsyncInit = function () {

			gapi.load('auth2', function () {
				// Retrieve the singleton from the GoogleAuth library
				this.auth2 = gapi.auth2.init({
					// client_id <- note the underscore. This is for Google Sign-In depend
					client_id: this._googleClientId,
					cookiepolicy: 'single_host_origin',
					fetch_basic_profile: false,
					scope: 'openid email'
				});

			}.bind(this));

		}.bind(this);

		this._loadScriptAsync('https://apis.google.com/js/api:client.js?onload=googleAsyncInit', 'google-script');
	};

	/**
	 * Logs in user using googles api
	 * @param {Object} callbacks - an object to be invoked `beforeSubmit`, `onSuccess`, `onFail`
	 * @private
	 */
	LoginManager.prototype._googleLogin = function _googleLogin(callbacks) {
		this.auth2.grantOfflineAccess({'redirect_uri': 'postmessage'})
			.then(function (result) {
				if (result['code']) {
					this._oAuthAjax(this._googleLoginUrl, result['code'], callbacks);
				} else {
					callbacks.onFail(result);
				}
			}.bind(this), callbacks.onFail);
	};

	/**
	 * Initializes facebook oauth login.
	 * Sets `window.fbAsyncInit` callback function and dynamically loads facebook SDK
	 * @private
	 */
	LoginManager.prototype._facebookInit = function _facebookInit() {
		if (window.fbAsyncInit)
			throw new Error("LoginManager: fbAsyncInit is already initialized.");

		window.fbAsyncInit = function () {
			this.FB = FB;
			FB.init({
				appId: this._facebookClientId,
				xfbml: true,
				version: 'v2.3'
			});
		}.bind(this);
		this._loadScriptAsync('https://connect.facebook.net/en_US/sdk.js', 'facebook-jssdk');
	};

	/**
	 * Logs in user using facebook SDK
	 * @param {Object} callbacks - an object to be invoked `beforeSubmit`, `onSuccess`, `onFail`
	 * @private
	 */
	LoginManager.prototype._facebookLogin = function _facebookLogin(callbacks) {
		this.FB.login(function (response) {

			if (response.authResponse) {
				var accessToken = FB.getAuthResponse()['accessToken'];
				this.FB.api('/me', function () {
					this._oAuthAjax(this._facebookLoginUrl, accessToken, callbacks);
				}.bind(this));
			} else {
				callbacks.onFail(response);
			}
		}.bind(this), {scope: 'public_profile,email'});

	};

	// LoginManager.prototype._githubInit = function _githubInit() {};
	// NOTE:
	// 	Github doesn't have a init method like facebook and google. This is because github
	// 	doesn't have a javascript SDK so we will implement a full server-side flow when logging
	// 	in with github accounts.

	/**
	 * Dynamically creates a form and inserts in a popup to be submitted to the server
	 * which will redirect the user to github's website to authorize access.
	 *
	 * @param {Object} callbacks - an object to be invoked `beforeSubmit`, `onSuccess`, `onFail`
	 * @private
	 */
	LoginManager.prototype._githubLogin = function _githubLogin(callbacks) {
		var popupWindow = window.open('', 'githubLogin', 'location=0,status=0,width=800,height=400');
		// dynamically create a form and insert it in the popup
		var $form = $('<form></form>', { method: 'post', action: this._githubLoginUrl });
		// don't forget csrf token
		$form.append($('<input></input>', {type: 'hidden', name: 'csrf_token', value: this._csrfToken}));
		$('body', popupWindow.document).append($form);
		// submit the form
		$($form, popupWindow.document).submit();

		// keeping checking if the popup is open every .5 seconds
		var popupInterval = setInterval(function () {
			if (popupWindow.closed) {
				clearInterval(popupInterval); // clear this interval
				// when the popup window closes get the response object from `window.popupResult`
				if (window.popupResult) {
					// save result then set `popupResult` back to undefined
					var data = window.popupResult;
					window.popupResult = undefined;
					// call the appropriate callback
					if (data && data.result['success']) {
						callbacks.onSuccess(data);
					} else {
						callbacks.onFail(data)
					}

				} else {
					// code reaches here when the user manually closes the popup window
					callbacks.onFail();
				}
			}
		}, 500);
		callbacks.beforeSubmit();
	};
	/**
	 * Ensures a csrf token is set to true when making making request and the proper contentType is set.
	 *
	 * @param {string} url - url used to login user
	 * @param {string} accessToken - access token to send to the server
	 * @param {Object} callbacks - an object to be invoked `onSuccess`, `onFail`
	 * @private
	 */
	LoginManager.prototype._oAuthAjax = function _oAuthAjax(url, accessToken, callbacks) {
		var options = {
			url: url,
			type: 'POST',
			processData: false,
			csrfHeader: true, // provide csrf token
			contentType: 'application/octet-stream; charset=utf-8',
			data: accessToken,
			success: callbacks.onSuccess,
			error: callbacks.onFail
		};
		callbacks.beforeSubmit(accessToken, null, options);
		$.ajax(options);
	};

	/**
	 * Dynamically loads a script using the given URL and ID
	 *
	 * @param {string} url - URL to use on the script tag
	 * @param {string} id - ID to add to the script tag
	 * @private
	 */
	LoginManager.prototype._loadScriptAsync = function _loadScriptAsync(url, id) {
		if (document.getElementById(id)) return;
		var js, script = document.getElementsByTagName('script')[0];
		js = document.createElement('script');
		js.id = id;
		js.src = url;
		script.parentNode.insertBefore(js, script);
	};

	/**
	 * Upgrades the HTML Login and register forms to use AJAX and use the provided callbacks.
	 *
	 * @param {HTMLElement|string} LoginRegisterFormContainer - form container. Either a html element or a string selector
	 * @param {Object} callbacks - an object to be invoked `beforeSubmit`, `onSuccess`, `onFail`
	 * @param {Object} thisArg - the context to use when invoking `callbacks`
	 */
	LoginManager.prototype.setLoginRegisterForm = function setLoginRegisterForm(LoginRegisterFormContainer, callbacks, thisArg) {
		var $container = $(LoginRegisterFormContainer);
		if ($container.length == 0)
			throw Error('LoginManager: failed to find LoginRegisterForm container');

		this._configureCallbacks(callbacks, thisArg);

		this.$forms = $container.find('form');
		this.$forms.each(function () {
			var $form = $(this);
			$form.ajaxForm({
				csrfHeader: true, // Use csrf token
				beforeSubmit: callbacks.beforeSubmit,
				success: callbacks.onSuccess,
				error: callbacks.onFail
			});
		});

	};

	/**
	 * Binds the `thisArgs` to the callbacks and ensures the callbacks have all 3 properties
	 * (`beforeSubmit`, `onSuccess`, `onFail`) by adding a placeholder (empty function) when not being provided.
	 *
	 * @param {Object} callbacks - an object to be invoked `beforeSubmit`, `onSuccess`, `onFail`
	 * @param {Object} thisArg - the context to use when invoking `callbacks`
	 * @private
	 */
	LoginManager.prototype._configureCallbacks = function _configureCallbacks(callbacks, thisArg) {
		var keys = ['onSuccess', 'onFail', 'beforeSubmit'],
			key, fn;

		if (typeof callbacks != 'object')
			throw Error('LoginManager: Invalid callback');

		for (var i = 0; i < keys.length; i++) {
			key = keys[i];
			if ( ! callbacks.hasOwnProperty(key)) {
				callbacks[key] = function () {}; // use a placeholder
				continue;
			}

			fn = callbacks[key];

			if (typeof fn != 'function')
				throw Error('LoginManager: callback must be a function');

			// set the thisArg if provided
			if (thisArg)
				callbacks[key] = fn.bind(thisArg);
		}
	};

	/**
	 * If the LoginManager hasn't yet been initialized the data argument is required.
	 *
	 * @param {Object} [data] - the object containing the oauth data
	 * @returns {LoginManager} -  a LoginManager singleton instance
	 */
	LoginManager.getInstance = function (data) {
		if (LoginManager.prototype._singletonInstance)
			return LoginManager.prototype._singletonInstance;

		if (arguments.length == 0)
			throw Error('LoginManager: data argument is required to instantiate.');

		return new LoginManager(data);
	};

	/**
	 * This method is equivalent to calling `new LoginManager(data)`,
	 * except it doesn't return a LoginManager instance.
	 *
	 * @param {Object} data - the object containing the oauth data
	 */
	LoginManager.loadOAuth = function (data) {
		if (LoginManager.prototype._singletonInstance) return; // do nothing
		new LoginManager(data); // load OAuth scripts asynchronously
	};

	return LoginManager

});
