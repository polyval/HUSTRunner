$(function(){
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
});