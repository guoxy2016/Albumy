$(function () {
    var hover_timer = null;
    var flash = null;
    $.ajaxSetup({
        beforeSend: function (xhr, setting) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(setting.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token)
            }
        }
    });

    function show_profile_popover(e) {
        var $el = $(e.target);
        hover_timer = setTimeout(function () {
            hover_timer = null;
            $.ajax({
                tpye: 'GET',
                url: $el.data('href'),
                success: function (data) {
                    $el.popover({
                        html: true,
                        container: 'body',
                        content: data,
                        trigger: 'manual',
                        animation: false,
                    });
                    $el.popover("show");
                    $(".popover").on("mouseleave", function () {
                        setTimeout(function () {
                            $el.popover("hide");

                        }, 200);
                    });
                },
                // error: function (error) {
                //     toast('服务器错误, 请稍后重试!');
                // }
            });
        }, 500);
    }

    function hide_profile_popover(e) {
        var $el = $(e.target);
        if (hover_timer) {
            clearTimeout(hover_timer);
            hover_timer = null;
        } else {
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    $el.popover("hide");
                }
            }, 200);
        }
    }

    function toast(body, category) {
        clearTimeout(flash);
        var $toast = $('#toast');
        if (category === 'error') {
            $toast.css('background-color', 'red')
        } else {
            $toast.css('background-color', '#333')
        }
        $toast.text(body).fadeIn();
        flash = setTimeout(function () {
            $toast.fadeOut();
        }, 2000);
    }

    function follow(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.prev().show();
                $el.hide();
                update_followers_count(id);
                toast(data.message);
            },
            // error: function (error) {
            //     toast('服务器错误, 请稍候重试!');
            // }
        });
    }

    function unfollow(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.next().show();
                $el.hide();
                update_followers_count(id);
                toast(data.message);
            },
            // error: function (error) {
            //     toast('服务器错误, 请稍候重试!')
            // }
        });
    }

    function update_followers_count(id) {
        var $el = $('#followers-count-' + id);
        $.ajax({
            type: 'GET',
            url: $el.data('href'),
            success: function (data) {
                $el.text(data.count);
            },
            // error: function (error) {
            //     toast('服务器错误, 请稍候重试!')
            // }
        });
    }

    function update_notifications_count() {
        var $el = $('#notification-badge');
        $.ajax({
            type: 'GET',
            url: $el.data('href'),
            success: function (data) {
                if (data.count === 0) {
                    $('#notification-badge').hide();
                } else {
                    $el.show();
                    $el.text(data.count)
                }
            }
        })
    }

    function update_collectors_count(id) {
        var $el = $('#collectors-count-' + id);
        $.ajax({
            tpye: 'GET',
            url: $el.data('href'),
            success: function (data) {
                console.log(data);
                $el.text(data.count);
            }
        })

    }

    function collect(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.prev().show();
                $el.hide();
                update_collectors_count(id)
                toast(data.message)
            }
        })

    }

    function uncollect(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.next().show();
                $el.hide();
                update_collectors_count(id);
                toast(data.message);
            }
        })

    }

    $(document).ajaxError(function (event, request, settings) {
        var message = null;
        if (request.responseJSON && request.responseJSON.hasOwnProperty('message')) {
            message = request.responseJSON.message;
        } else if (request.responseText) {
            var IS_JSON = true;
            try {
                var data = JSON.parse(request.responseText);
            } catch (e) {
                IS_JSON = flash;
            }
            if (IS_JSON && data !== undefined && data.hasOwnProperty('message')) {
                message = JSON.parse(request.responseText).message;
            } else {
                message = default_error_message;
            }
        } else {
            message = default_error_message;
        }
        toast(message, 'error')
    });
    $('#confirm-delete').on('show.bs.modal', function (e) {
        $('.delete-form').attr('action', $(e.relatedTarget).data('href'));
    });

    $('#description-btn').click(function () {
        $('#description').hide();
        $('#description-form').show();
    });
    $('#cancel-description').click(function () {
        $('#description-form').hide();
        $('#description').show();
    });

    $('#tag-btn').click(function () {
        $('#tags').hide();
        $('#tag-form').show();
    });
    $('#cancel-tag').click(function () {
        $('#tag-form').hide();
        $('#tags').show();
    });
    $(".profile-popover").hover(show_profile_popover.bind(this), hide_profile_popover.bind(this));
    $("[data-toggle='tooltip']").tooltip({title: moment($(this).data('timestamp')).format('lll')});
    $(document).on('click', '.follow-btn', follow.bind(this));
    $(document).on('click', '.unfollow-btn', unfollow.bind(this));
    $(document).on('click', '.collect-btn', collect.bind(this));
    $(document).on('click', '.uncollect-btn', uncollect.bind(this));
    if (is_authenticated) {
        setInterval(update_notifications_count, 30000);
    }
});
