var app = {
    // variables to be initialized in `layout.html`
    isLoggedIn: null,
    csrfToken: null,

    getCSRFHeader: function () {
        var token = this.csrfToken;
        return function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", token);
            }
        }
    },

    createAlertMessage: function (message, category) {
        var $outerDiv = $('<div>', {class: 'alert-messages'}),
            $innerDiv = $('<div>', {class: 'alert alert-' + category}),
            $a = $('<a href="#" class="close" data-dismiss="alert">&times;</a>');
        return $outerDiv.append($innerDiv.append($a).append(message))
    },

    displayFormErrors: function ($form, formErrors, prefix) {
        var $field;

        if (prefix == undefined) prefix = '#';

        // clear any previous errors
        $form.find('.form-group').removeClass('has-error');
        $form.find('.help-block').remove();

        for (var labelID in formErrors) {

            if (formErrors.hasOwnProperty(labelID)) {
                $field = $form.find(prefix + labelID);

                formErrors[labelID].forEach(function (errorMessage) {
                    var $element,// a help-block gets appended after this element
                        $parent;
                    this.closest('.form-group').addClass('has-error');

                    // for input-group fields, append the help-block after its container
                    $parent = this.parent();
                    $element = $parent.hasClass('input-group') ? $parent : this;

                    $element.after($('<p></p>').addClass('help-block').html(errorMessage));

                }, $field);
            }
        }
    },

    formErrorsToAlertMessage: function (messages) {
        var msg = messages.message;
        if (typeof msg == 'object') {
            var items = Object.keys(msg).map(function (key) {
                var string = msg[key][0];
                // customize error message
                // if the message starts with the word `This` replace it with its label name
                if (string.indexOf('This') == 0) {
                    var label = key.charAt(0).toUpperCase() + key.substr(1);
                    string = string.replace('This', label);
                }
                // make the first word of the message bold
                var temp = string.split(' ');
                temp[0] = '<strong>' + temp[0] + '</strong>';
                string = temp.join(' ');
                return '<li>' + string + '</li>';
            }).join('');
            msg = '<ul>' + items + '</ul>';
        }
        return app.createAlertMessage(msg, messages.category);
    },

    displayMessages: function ($element, flashedMessages, action) {

        // ensure a jQuery element was given
        if (!($element instanceof jQuery)) $element = $($element);

        // set the default action (jQuery method)
        if (action == null) action = 'before';

        flashedMessages.forEach(function (message) {
            if (message.category == 'form-error') {
                // populate the form with the given errors
                this.displayFormErrors($element, message.message);

            } else {
                // display the message in an alert box
                if (typeof message.message == 'object') {
                    // code reaches here when a form error is categorized as a normal alert message
                    $element[action](this.formErrorsToAlertMessage(message));
                } else {
                    $element[action](this.createAlertMessage(message.message, message.category));
                }
            }
        }, this);
    },

    populateForm: function ($form, item, filter) {
        var id, $input;
        for (id in item) {
            if (!item.hasOwnProperty(id)) continue;

            $input = $form.find('#' + id);

            if ($input.length == 0) continue;

            if (!filter || $input.attr('type') == filter) {

                if ($input.is('select')) {
                    // select items have to go 1 level deeper to get its value
                    $input.val(item[id].id)
                } else {
                    $input.val(item[id]);
                }
            }

        }
    }
};

app.navbar = {

    $navbar: $('#navbar-inner'),

    // Links to display only when a user is logged in
    loginRequiredLinks: ['Logout', 'Profile'],

    // Links to display only when a user is logged out
    logoutRequiredLinks: ['Login', 'Register'],

    loginState: function () {
        this.updateLinks(this.logoutRequiredLinks, 'hide');
        this.updateLinks(this.loginRequiredLinks, 'show');
    },

    logoutState: function () {
        this.updateLinks(this.loginRequiredLinks, 'hide');
        this.updateLinks(this.logoutRequiredLinks, 'show');
    },

    // action should be either `show` or `hide`
    updateLinks: function (links, action) {

        if ( ! action ) action = 'show';

        var $navbar = this.$navbar;
        links.forEach(function (value) {
            // find the anchor that contains
            var $a = $navbar.find(['a:textEquals("', value, '")'].join(''));
            // apply the action to its parent container.
            if ($a.length) $a.parent()[action]();
        });
    }
};

app.helpers = {
    isElementInViewport: function (el) {
        // taken from:
        // http://stackoverflow.com/questions/123999/how-to-tell-if-a-dom-element-is-visible-in-the-current-viewport/7557433#7557433
        var rect = el.getBoundingClientRect();
        return (rect.top >= 0 && rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth));
    }
};

