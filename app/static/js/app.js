var app = {
    // variables to be initialized in `layout.html`
    isLoggedIn: null,
    csrfToken: null,
    client_id: '',
    $navbar: null,
    dynamicLinks : null,

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

    displayFormErrors: function ($form, formErrors) {
        // clear any previous errors before setting the form
        $form.find('.form-group').removeClass('has-error');
        $form.find('.help-block').remove();


        for (var labelID in formErrors) {

            if (formErrors.hasOwnProperty(labelID)) {
                formErrors[labelID].forEach(function (errorMessage) {

                    this.parent().addClass('has-error');
                    this.after($('<p></p>').addClass('help-block').html(errorMessage));

                }.bind($form.find('#' + labelID))); // bind input element to `this` context
            }
        }
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
                // default message
                $element[action](this.createAlertMessage(message.message, message.category));
            }
        }, this);
    },

    updateNavbar: function (links) {
        var dynamicLinks = this.dynamicLinks;
        var $navbar = this.$navbar;
        links.forEach(function (link) {
            var $li = $('<li>')
                .append($('<a>', {href: dynamicLinks[link], html: link}));
            $navbar.append($li);
        });
    }
};
