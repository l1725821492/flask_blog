from flask import render_template, flash, redirect, url_for, Blueprint,current_app,request
from flask_login import login_user, logout_user, login_required, current_user
from blog.forms import LoginForm,addpostForm,TagForm,PostForm
from blog.models import Admin,Post,Tag,Comment
from blog.utils import redirect_back
from blog.extensions import db
from werkzeug.datastructures import CombinedMultiDict
import os
import random
from functools import reduce

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
post_path = os.path.join(basedir, 'post')
admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/login',methods=['POST','GET'])
def login():

    if current_user.is_authenticated:
        redirect(url_for('blog.index'))
    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        remember=form.remember.data
        admin=Admin.query.first()
        # flash(admin.password_hash, 'warning')
        if admin:
            if username==admin.username and admin.validate_password(password):
                login_user(admin,remember)
                flash('Welcome back.', 'info')
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('admin/login.html', form=form)
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()
@admin_bp.route('/post/new',methods=['POST'])
def add_post():
        form=addpostForm(CombinedMultiDict((request.files, request.form)))
        # print(form.validate_on_submit)
        if form.validate_on_submit:
            print(form.post.data)
            f=form.post.data

            filename=str(f.filename).split('.md')[0]
            print(filename)
            f.save(os.path.join(post_path, filename))
            with open(os.path.join(post_path, filename), encoding='utf-8') as md_file:
                content = reduce(lambda x, y: x + y, md_file.readlines())
            title=filename
            body=content
            post=Post(title=title,body=body)
            db.session.add(post)
            db.session.commit()
            os.remove(os.path.join(post_path, filename))
            flash('Post created.', 'success')
            return redirect(url_for('blog.show_post', post_id=post.id))
        return redirect_back()

@admin_bp.route('/comment/manage_comment',defaults={'fillter':'all'})
@admin_bp.route('/comment/manage_comment/<fillter>')
@login_required
def manage_comment(fillter):
    filter_rule=fillter
    admin=Admin.query.first()
    page=request.args.get('page',1,type=int)
    per_page=int(os.getenv('BLUELOG_COMMENT_PER_PAGE'))
    if filter_rule=='unread':
        fillter_comments=Comment.query.filter_by(reviewed=False)
    elif filter_rule=='admin':
        fillter_comments=Comment.query.filter_by(from_admin=True)
    else:
        fillter_comments=Comment.query
    pagination=fillter_comments.order_by(Comment.timestamp.desc()).paginate(page,per_page=per_page)
    comments=pagination.items
    return render_template('admin/manage_comment.html',comments=comments,pagination=pagination,filter_rule=filter_rule,admin=admin)
@admin_bp.route('/comment/<int:comment_id>/delete',methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment=Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('删除评论成功','success')
    return redirect_back()
@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    # send_new_reply_email(comment)
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()
@admin_bp.route('/post/manage_post')
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    form=addpostForm()
    class_ = ["badge-primary", "badge-secondary", "badge-success", "badge-danger",
              "badge-warning",
              "badge-info", "badge-light", "badge-dark"]
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts,form=form)

@admin_bp.route('/post/<int:post_id>/delate',methods=['POST'])
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()
@admin_bp.route('/post/<int:post_id>/tag',methods=['POST'])
def add_tag(post_id):
    post=Post.query.get_or_404(post_id)

    form=TagForm()
    # print(form.validate_on_submit())
    if form.validate_on_submit:
        # print(form.validate_on_submit())
        tag=Tag(body=form.name.data)
        db.session.add(tag)
        db.session.commit()
        # print(type(post.tags),post.title,[str(tag.body)])
        post.tags.append((Tag.query.get(tag.id)))
        db.session.commit()
        flash('添加成功', 'success')
        return redirect_back()
    return redirect_back()
    # return render_template('admin/add_tag.html',post_id=post_id)
@admin_bp.route('/post/<int:tag_id>/delate_tag',methods=['POST'])
def delete_tag(tag_id):
    tag=Tag.query.get_or_404(tag_id)
    print(tag.body)
    db.session.delete(tag)
    db.session.commit()
    flash('删除成功', 'success')
    return  redirect_back()