# -*- coding: utf-8 -*-
import os
import re
import json

from flask import request, render_template, make_response, current_app, abort, jsonify
from .. import db
from . import main
from ..forum.models import Post, Topic
from ..uploader import Uploader


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    type = request.args.get('type')
    if not type:
        pagination = Post.query.order_by(Post.date_created.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        posts = pagination.items
    elif type == 'essence':
        Post.rank_hot()
        pagination = Post.query.order_by(Post.hot_index.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        posts = pagination.items
    else:
        abort(404)
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    if request.method == 'POST':
        post_id = request.form.get('post_id', type=int)
        if request.form.get('sticky') == 'False':
            Post.query.filter_by(id=post_id).update({'sticky': True})
        else:
            Post.query.filter_by(id=post_id).update({'sticky': False})
        return jsonify(msg='success')
    page = request.args.get('page', 1, type=int)
    topic_title = Topic.query.filter_by(id=topic_id).first_or_404().title
    type = request.args.get('type')
    if not type:
        pagination = Post.query.filter_by(topic_id=topic_id).\
            order_by(Post.sticky.desc(), Post.date_created.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        posts = pagination.items
    elif type == 'essence':
        Post.rank_hot(topic_id)
        pagination = Post.query.order_by(Post.sticky.desc(), Post.hot_index.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        posts = pagination.items
    else:
        abort(404)
    if not posts:
        abort(404)
    return render_template('topic.html', posts=posts, title=topic_title, pagination=pagination)


@main.route('/upload/', methods=['GET', 'POST', 'OPTIONS'])
def upload():
    """UEditor文件上传接口

    config 配置文件
    result 返回结果
    """
    mimetype = 'application/json'
    result = {}
    action = request.args.get('action')

    # 解析JSON格式的配置文件
    with open(os.path.join(current_app.static_folder, 'vendors', 'ueditor', 'php',
                           'config.json')) as fp:
        try:
            # 删除 `/**/` 之间的注释
            CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        except:
            CONFIG = {}

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }

        if fieldName in request.files:
            field = request.files[fieldName]
            uploader = Uploader(field, config, current_app.static_folder)
            result = uploader.getFileInfo()
        else:
            result['state'] = u'上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(
                field, config, current_app.static_folder, 'base64')
            result = uploader.getFileInfo()
        else:
            result['state'] = u'上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(
                imgurl, config, current_app.static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list

    else:
        result['state'] = u'请求地址出错'

    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
            mimetype = 'application/javascript'
        else:
            result = json.dumps({'state': u'callback参数不合法'})

    res = make_response(result)
    res.mimetype = mimetype
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers[
        'Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res
