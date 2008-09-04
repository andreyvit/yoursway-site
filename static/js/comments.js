$(document).ready(init);

function init() {
    saved_posts = {};
    comment_form = $("#comment-form");
    input_reply = $("#id_reply_to", comment_form);
    comment_link = $("a.comment-link");
    // actions
    if (!comment_form.find(".errorlist").length) {
        comment_form.hide();
        var show_comment_link = true;
    }
    else {
        var id = input_reply.val();
        var show_comment_link = id;
        move_form(id);
        $('html').animate({scrollTop: comment_form.offset().top}, 1);
    }
    if (show_comment_link) {
        comment_link.show();
    }
    $("a.edit-comment").css("display", "inline");

    // spinner
    $('#ajaxload').ajaxStart(function(){$(this).show()}).ajaxStop(function(){$(this).hide()});
};

function get_json(data) {
    return eval('(' + data + ')');
};

function move_form(id) {
    if (id) {
        $("#c" + id).append(comment_form);
    }
    else {
        $(".post").append(comment_form);
    }
}

function replyto(id) {
    cancel_comment();
    input_reply.val(id);
    move_form(id);
    comment_form.show();
    $("#reply-link-" + id).hide();
    return false;
};

function comment() {
    cancel_comment();
    input_reply.val('');
    move_form(null);
    comment_form.show();
    comment_link.hide();
    return false;
};

function cancel_comment() {
    id = input_reply.val();
    if (id) {
        $("#reply-link-" + id).show();
    }
    else {
        comment_link.show();
    }
    comment_form.hide();
    return false;
};

function edit_comment(id, url) {
    comment_div = $("#c" + id + " .text");
    saved_posts[id] = comment_div.html()
    $.post(url,
           {'get_body': ''},
           function (data) {
               json = get_json(data);
               comment_div.html('<textarea class="comment-edit-area">' + json.body + '</textarea>');
               $("#edit-comment-" + id).hide();
               $("#cancel-edit-" + id).css("display", "inline");
               $("#edit-submit-" + id).css("display", "inline");
           });
    return false;
};

function cancel_edit(id) {
    comment_div = $("#c" + id + " .text");
    comment_div.html(saved_posts[id]);
    $("#cancel-edit-" + id).hide();
    $("#edit-submit-" + id).hide();
    $("#edit-comment-" + id).css("display", "inline");
    return false;
};

function submit_edit(id, url) {
    comment_div = $("#c" + id + " .text");
    text = $("#c" + id + " .text textarea.comment-edit-area").val();
    $.post(url,
           {'body': text},
           function (data) {
               json = get_json(data);
               comment_div.html(json.body_html);
               $("#cancel-edit-" + id).hide();
               $("#edit-submit-" + id).hide();
               $("#edit-comment-" + id).css("display", "inline");
           });
    return false;
};

function delete_comment(id, url) {
    if (confirm("Are you sure to delete this comment?"))
        {
            $.post(url,
                   {'delete': true},
                   function (data) {
                       json = get_json(data);
                       $('#c' + json.id).remove();
                   });
        };
    return false;
};

function preview_comment(url) {
    text = $("#id_body", comment_form).val();
    preview_div = $("#comment-preview", comment_form);
    $.post(url,
          {'body': text},
          function (data) {
              json = get_json(data);
              preview_div.html(json.body_preview);
          });
    return false;
};
