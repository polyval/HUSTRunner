$(function(){
    // face detection
    $('img:not([class])').mouseenter(function(){
        // avoid conflict
        var $this = $(this);
        // find the exact face and make it display
        $this.nextAll('.face-wrap').show();
        // find whether the faces are already detected or not
        if(!($this.hasClass('done'))){
            var url = '/apis/faces';
            var img_url = $this.attr('src');
            // start detection
            var coords = $this.faceDetection({
                complete: function(faces){
                    $this.addClass('done');
                    $this.after($('<div>',{
                        'class': 'face-wrap'
                    }));

                    for (var i = 0; i < faces.length; i++){
                        $this.next().append($('<div>',{
                            'class': 'face',
                            'css': {
                                'left':     faces[i].positionX +'px',
                                'top':      faces[i].positionY +'px',
                                'width':    faces[i].width     +'px',
                                'height':   faces[i].height    +'px',
                            }
                        }));
                    };

                    $.get(url, {img_url: img_url}, function(response){
                        $this.addClass('done');
                        // get the tags
                        for (var i = 0; i < response.tags.length; i++)
                        {
                            $this.nextAll('.face-wrap').find('.face').eq(response.tags[i].index)
                            .attr('title', response.tags[i].name);
                        };
                    });
                }
            });

            
        };
    }).mouseleave(function(e){
        // hide the face once the mouse leaves the photo, avoid flicking
        if ($(e.relatedTarget).hasClass('face')){
            return false;
        };
        $(this).nextAll('.face-wrap').hide();
    });


    // add tag when click the face box
    $(document).on('click', '.face', function(){
                var $thisface = $(this);
                // add input field before face-wrap class:add-tag
                if(!($thisface.parent().prev().hasClass('add-tag'))){
                    var html = '<div class="add-tag" style="display:none;">' +
                                '输入标签：<br />' +
                                '<input class="tag-name" name="tag-name" type="text"  /><br />'+
                                '<button class="btn-add-tag">确认</button>' +
                                '<button class="btn-cancel">取消</button>' +
                                '</div>'
                    $thisface.parent().before(html);
                };
                if($thisface.attr('title')){
                    //if then show alert
                    alert('tag added already');
                }else{
                // show the add tag form
                    $thisface.parent().prev('.add-tag').show(function(){
                        $(document).on('click', '.btn-add-tag, .btn-cancel', function(){
                            if($(this).hasClass('btn-cancel')){
                                $(this).parent().hide();
                                return false;
                            };
                            // when click ok
                            if(!$(this).prevAll('input').val()){
                                $(this).parent().hide();
                                return false;
                            };
                            // post tag
                            var url = $thisface.parent().prevAll('img').attr('src')
                            var tag = $(this).prevAll('input').val();
                            var index = $thisface.index();
                            $.post('/apis/faces/tag', {url: url, tag: tag, index: index}, 
                                function(response){
                                $thisface.attr('title', response.tag)
                                }
                            );
                            $(this).parent().hide();
                        });
                    });
              };
    });

    // toggle follow
    $('.toggle-follow').on('click', function(){
        var $btn = $(this)
        var user_id = $btn.attr('data-id');
        var flag = $btn.hasClass('btn-unfollow');
        var post_to = '/apis/follow'

        if (flag){
                $btn.removeClass('btn-unfollow');
                $btn.addClass('btn-follow');
                $btn.html('关注');
            } else{
                $btn.removeClass('btn-follow');
                $btn.addClass('btn-unfollow');
                $btn.html('取消关注');
            };

        $.post(post_to, {user_id: user_id, unfollow: flag});
    });

    // popover
    $("[data-toggle=popover]").popover({
    html: true, 
    delay: 100,
    content: function() {
          return $('#popover-notify').html();
        }
    });
    // click outside of popover to hide it
    $('html').on('click', function(e) {
        if (typeof $(e.target).data('original-title') == 'undefined' &&
        !$(e.target).parents().is('.popover.in')) {
        $('[data-original-title]').popover('hide');
    }
    });
    // temporarily fix popover bug in Bootstrap 3.3.5
    $('body').on('hidden.bs.popover', function (e) {
    $(e.target).data("bs.popover").inState.click = false;
    });
    
    $('[data-toggle="popover"]').on('shown.bs.popover', function(){
        $('.notify-button').click(function(){
            var action = $(this).data('action');
            var $button = $(this);
            var post_to = '/apis/notification';
            $.post(post_to, {action: action},
                function(response){
                    if(response.new_count > 0){
                        var replaced = $('title').html().replace(/\d(?=条)/g, response.new_count);
                        $('title').html(replaced);
                        $('.plain-noti').html(response.new_count);
                    }else{
                        $('.plain-noti').remove();
                        var replaced = $('title').html().replace(/\([^)]+\)/g,'');
                        $('title').html(replaced);
                    };
                });
        });
    });

    // tooltip initialization
    $('[data-toggle="tooltip"]').tooltip({
            container: 'body' // http://stackoverflow.com/questions/18194705/display-bootstrap-popovers-outside-divs-with-overflowhidden
    });
    
    // fancybox
    $(".article img").fancybox();

    // highlight tab
    $('a[href="' + this.location.pathname + '"]').parents('li,ul').addClass('active');
    $('a[href="' + this.location.href + '"]').addClass('on');

    // hide alert automatically
    window.setTimeout(function() {
    $(".alert-warning").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove();
    });
    }, 2000);
    // time to expired date
    $('.expired-time').each(function(i, e){
            var date_created = moment($(e).data('created'));
            var now = moment();
            var date_expired = moment($(e).data('expired'));
            $(e).html(now.to(date_expired) + '到期');
    });
    // toggle visibility of operations
    $(document).on('mouseenter', '.comment-content, .article-main', function(){
        $(this).children('.operation').css('visibility', 'visible');
    });

    $(document).on('mouseleave', '.comment-content, .article-main', function(){
        $(this).children('.operation').css('visibility', 'hidden');
    });

    // collapse comments
    $(document).on('click', '.collapse-comments', function() {
            var childId = $(this).attr('data-childId');
            var count = $(this).attr('data-comments');

            $('#'+childId).toggle();
            if(count){
                $(this).html($(this).html() == '回复'+'('+count+')' ? '收起回复' : '回复'+'('+count+')');
            }
    });

    $(document).on('click', '.comment-actions a', function() {
            $(this).closest('.comment-actions').closest('.comment-bar').hide();
    });

    // delete comment
    $('#deleteModal').on('show.bs.modal', function(event){
        var id = $(event.relatedTarget).data('id');
        var post_to = '/apis/comments/' + id
        $('.delete').on('click', function(){
            $.ajax({
                url: post_to,
                type: 'DELETE',
                success: function(){
                    $('#'+id+'parent').remove();
                }
            })
        });
    });
    // auto grow for textarea
    $('textarea').autogrow();
});