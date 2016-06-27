# -*- coding: utf-8 -*-
from itertools import groupby

from flask import request, render_template
from flask_login import login_required, current_user

from .. import db
from . import message
from .models import Conversation, Message, Notification
from ..user.models import User


@message.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    if request.method == 'POST':
        # save new message
        if request.form.get('recipient'):
            recipient = request.form['recipient']
            message_html = request.form['message']
            to_user = User.query.filter_by(username=recipient).first()
            conversation = Conversation.query.filter(Conversation.user_id == current_user.id,
                                                     Conversation.to_user_id == to_user.id,
                                                     ).first() or Conversation(user_id=current_user.id,
                                                                               from_user_id=current_user.id,
                                                                               to_user_id=to_user.id,
                                                                               unread=False)
            # save conversation in other end
            end_conversation = Conversation.query.filter(Conversation.user_id == to_user.id,
                                                         Conversation.to_user_id == current_user.id,
                                                         ).first() or Conversation(user_id=to_user.id,
                                                                                   from_user_id=to_user.id,
                                                                                   to_user_id=current_user.id)

            db.session.add(conversation)
            db.session.add(end_conversation)
            db.session.commit()

            new_message = Message(user_id=current_user.id,
                                  message=message_html,
                                  conversation_id=conversation.id)
            end_new_message = Message(user_id=current_user.id,
                                      message=message_html,
                                      conversation_id=end_conversation.id)
            db.session.add(new_message)
            db.session.add(end_new_message)
            db.session.commit()
        # delete conversation along with messages, request.form[''] would cause
        # a KeyError which cause 400 error
        if request.form.get('conversation_id'):
            Conversation.query.filter_by(
                id=request.form.get('conversation_id', type=int)).delete()
            db.session.commit()

    page = request.args.get('page', 1, type=int)

    pagination = Conversation.query.filter_by(user_id=current_user.id). \
        order_by(Conversation.date_created.desc()). \
        paginate(page=page, per_page=20, error_out=False)

    conversations = pagination.items
    message_count = Conversation.query.filter_by(
        user_id=current_user.id).count()
    # read messages
    Conversation.query.filter_by(user_id=current_user.id).update({Conversation.unread: False})

    return render_template("inbox.html", conversations=conversations,
                           message_count=message_count, pagination=pagination)


@message.route('/inbox/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def view_conversation(conversation_id):
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user.id).first_or_404()
    to_user = conversation.to_user
    if request.method == 'POST':
        # delete message
        if request.form.get('message_id'):
            Message.query.filter_by(
                id=request.form.get('message_id', type=int)).delete()
            db.session.commit()
        # save new message
        else:
            end_conversation = Conversation.query.filter(Conversation.user_id == to_user.id,
                                                         Conversation.to_user_id == current_user.id,
                                                         ).first() or Conversation(user_id=to_user.id,
                                                                                   from_user_id=to_user.id,
                                                                                   to_user_id=current_user.id)
            db.session.add(end_conversation)
            db.session.commit()
            new_message = Message(user_id=current_user.id,
                                  message=request.form['message'],
                                  conversation_id=conversation.id)
            end_new_message = Message(user_id=current_user.id,
                                      message=request.form['message'],
                                      conversation_id=end_conversation.id)
            db.session.add(new_message)
            db.session.add(end_new_message)
            db.session.commit()
    return render_template("messages.html", messages=conversation.messages, to_user=to_user)


@message.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    pagination = Notification.query.filter_by(receive_id=current_user.id). \
        order_by(Notification.date_created.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    messy = []
    for notif in pagination.items:
        messy.append(
            (notif.date_created.strftime('%Y-%m-%d'), notif.action, notif.entity, notif))
        messy.sort(key=lambda x: (x[0], x[1], x[2]))
    items = []
    for key, group in groupby(messy, key=lambda x: (x[0], x[1], x[2])):
        items.append(
            {'date': key[0], 'action': key[1], 'entity': key[2],
             'notify': [noti[3] for noti in group]})
    return render_template("notifications.html", items=items, pagination=pagination)
