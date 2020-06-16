from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, FileField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import ValidationError

class CaseUploadForm(FlaskForm):
    describe = StringField('文件描述', validators=[DataRequired()])
    upload_file = FileField('文件上传', validators=[FileRequired(), FileAllowed(['doc','docx','pdf'])])
    submit = SubmitField('提交')

class ConfigForm(FlaskForm):
    upload_file = FileField('上传检查', validators=[FileRequired(), FileAllowed(['log','txt'])])
    submit = SubmitField('提交')

class ModelForm(FlaskForm):
    id = HiddenField('模板id', validators=[DataRequired()])
    name = StringField('模板名称', validators=[DataRequired()])
    content= TextAreaField('模板内容', validators=[DataRequired()])
    submit = SubmitField('提交')

class ModelListCreateForm(FlaskForm):
    name = StringField('模板名称', validators=[DataRequired()])
    model_names = SelectMultipleField('模板选择', validators=[DataRequired()], coerce=int, choices=[])
    submit = SubmitField('提交')

class ModelSelectForm(FlaskForm):
    model_names = SelectMultipleField('内置模板', coerce=int, choices=[])
    custom_model_names = SelectMultipleField('自定义模板', coerce=int, choices=[])
    submit = SubmitField('提交')