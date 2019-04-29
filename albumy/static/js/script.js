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

    function toast(body) {
        clearTimeout(flash);
        var $toast = $('#toast');
        $toast.text(body).fadeIn();
        flash = setTimeout(function () {
            $toast.fadeOut();
        }, 2000);
    }

    function follow(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'post',
            url: $el.data('href'),
            success: function (data) {
                $el.prev().show();
                $el.hide();
                update_followers_count(id);
                toast('以关注用户');
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
            type: 'post',
            url: $el.data('href'),
            success: function (data) {
                $el.next().show();
                $el.hide();
                update_followers_count(id);
                toast('已取消关注');
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
});
