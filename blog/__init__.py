import os

import click
from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from blog.blueprints.admin import admin_bp
# from blog.blueprints.auth import auth_bp
from blog.blueprints.blog import blog_bp
from blog.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment
from blog.models import  Post,Comment, Link,Admin,Tag
from blog.setting import config
import markdown2
from markdown import markdown
import markdown
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
post_path = os.path.join(basedir, 'blog','post')
from functools import reduce

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('blog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    # register_errors(app)
    register_shell_context(app)
    # register_template_context(app)
    return app


def register_logging(app):
    pass



def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)



def register_blueprints(app):
    app.register_blueprint(blog_bp)
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_shell_context(app):
    @app.template_filter('md')
    def markdown_to_html(txt):
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.tables',
        ]

        return markdown.markdown(txt,extensions=extensions)

    def read_md(filename):
        with open(os.path.join(post_path, filename),encoding='utf-8') as md_file:
            content = reduce(lambda x, y: x + y, md_file.readlines())
            print(content)
        return content
    @app.context_processor
    def inject_methods():
        return dict(read_md=read_md)
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Post=Post,  Comment=Comment,Admin=Admin)


# def register_template_context(app):
#     @app.context_processor
#     def make_template_context():
#         admin = Admin.query.first()
#         categories = Category.query.order_by(Category.name).all()
#         links = Link.query.order_by(Link.name).all()
#         if current_user.is_authenticated:
#             unread_comments = Comment.query.filter_by(reviewed=False).count()
#         else:
#             unread_comments = None
#         return dict(
#             admin=admin, categories=categories,
#             links=links, unread_comments=unread_comments)
def register_commands(app):
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Bluelog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        tag = Tag.query.first()
        if tag is None:
            click.echo('Creating the default category...')
            category = Tag(body='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')
