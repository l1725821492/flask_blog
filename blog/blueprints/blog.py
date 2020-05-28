import os
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user

from blog.extensions import db
from blog.forms import CommentForm,AdminCommentForm
from blog.models import Post, Comment,Tag
from blog.utils import redirect_back

# from aip import AipImageCensor
blog_bp = Blueprint('blog', __name__)
@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = int(os.getenv('BLUELOG_POST_PER_PAGE'))
    print(per_page)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)

@blog_bp.route('/photo')
def photo():
    return render_template('blog/photo.html')

@blog_bp.route('/video')
def video():
    return render_template('blog/video.html')



@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = int(os.getenv('BLUELOG_COMMENT_PER_PAGE'))
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)
    comments = pagination.items
    APP_ID = os.getenv('API_KEY')
    API_KEY = os.getenv('API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    # client = AipImageCensor(APP_ID, API_KEY, SECRET_KEY)
    # result = client.textCensorUserDefined("nmsl")
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False


    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        # site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)
        replied_id = request.args.get('reply')
        if replied_id :
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        db.session.add(comment)
        db.session.commit()
        # flash(comment.replied, 'success')
        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        # else:
        #     flash('Thanks, your comment will be published after reviewed.', 'info')
        #     send_new_comment_email(post)  # send notification email to admin
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')