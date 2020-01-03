from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import ValidationError

class CaseUploadForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    upload_file = FileField('文件上传', validators=[FileRequired(), FileAllowed(['docx','pdf'])])
    submit = SubmitField('提交')