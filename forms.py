from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import FlaskForm

class Upload(FlaskForm):
    image=FileField("Upload Image",validators=[FileRequired(),FileAllowed(["jpg","jpeg","png"],"Images only!")])
    submit=SubmitField("Upload")