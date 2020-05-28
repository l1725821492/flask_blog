from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField,FileField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from flask_wtf.file import FileRequired,FileAllowed
from blog.models import Tag
# from blog.models import Category

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    tag = SelectField('Tag', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    # def __init__(self, *args, **kwargs):
    #     super(PostForm, self).__init__(*args, **kwargs)
    #     self.category.choices = [(category.id, category.name)
    #                              for category in Category.query.order_by(Category.name).all()]

#
# class CategoryForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
#     submit = SubmitField()
#
#     def validate_name(self, field):
#         if Category.query.filter_by(name=field.data).first():
#             raise ValidationError('Name already in use.')

class addpostForm(FlaskForm):
    post = FileField( 'file',validators=[FileRequired(), FileAllowed(['md'])])
    submit = SubmitField()
class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    # site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()

class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Tag.query.filter_by(body=field.data).first():
            raise ValidationError('Name already in use.')

class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()
