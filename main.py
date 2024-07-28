from flask import Flask,render_template,flash,redirect,url_for
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import os
from sqlalchemy import Integer, String, Text,LargeBinary,DateTime
from forms import Upload
from werkzeug.utils import secure_filename
from datetime import datetime,timezone

# img_path="static/assets/sample.jpg"

year=datetime.now().year
app=Flask(__name__)

class Base(DeclarativeBase):
    pass
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DB_URI",'sqlite:///colorpalette.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db=SQLAlchemy(model_class=Base)
db.init_app(app)

class Palette(db.Model):
    __tablename__="palettes"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(100),nullable=False)
    data:Mapped[bytes]=mapped_column(LargeBinary,nullable=False)
    mimetype:Mapped[str]=mapped_column(String(50),nullable=False)
    upload_date:Mapped[datetime]=mapped_column(DateTime,default=datetime.now(timezone.utc))

with app.app_context():
    db.create_all()

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
def get_image(img_path):
    image=Image.open(img_path)
    image=image.convert("RGB")
    return np.array(image)

def get_colors(image,num_col):
    reshaped_img=image.reshape((image.shape[0]*image.shape[1],3))
    kmeans=KMeans(n_clusters=num_col)
    kmeans.fit(reshaped_img)
    colors=kmeans.cluster_centers_

    labels=kmeans.labels_
    counts=Counter(labels)
    ordered_colors=[colors[i]for i in counts.keys()]
    hex_colors=[rgb_to_hex(ordered_colors[i])for i in counts.keys()]
    return hex_colors



@app.route("/",methods=["POST","GET"])
def home():
    forms=Upload()
    if forms.validate_on_submit():
        file=forms.image.data
        filename=secure_filename(file.filename)
        mimetype=file.mimetype
        data=file.read()

    #Save the image
        new_image=Palette(name=filename,data=data,mimetype=mimetype)
        db.session.add(new_image)
        db.session.commit()
        flash("Successfully uploaded")
        return redirect(url_for("palette",image_id=new_image.id))
    return render_template("index.html",forms=forms,current_year=year)


#Image is not displaying
# @app.route("/palette/<int:image_id>")
# def palette(image_id):
#     num_col=10
#     image=db.get_or_404(Palette,image_id)
#     img_path=os.path.join(app.config['UPLOAD_FOLDER'],image.name)
    
#     with open (img_path,"wb") as img_file:
#         img_file.write(image.data)

#     img=get_image(img_path)
#     colors=get_colors(img,num_col)

    
#     return render_template("palette.html",colors=colors,current_year=year,img_path=img_path)
@app.route("/palette")
def palette():
    num_col=10
    image=db.get_or_404(Palette,1)
    img_path=os.path.join(app.config['UPLOAD_FOLDER'],image.name)
    
    with open (img_path,"wb") as img_file:
        img_file.write(image.data)

    img=get_image(img_path)
    colors=get_colors(img,num_col)
    image=db.get_or_404(Palette,1)
    db.session.delete(image)
    db.session.commit()
    
    return render_template("palette.html",colors=colors,current_year=year,img_path=img_path)

@app.route("/about")
def about():
    return render_template("about.html",current_year=year)
if __name__=="__main__":
    app.jinja_env.globals.update(enumerate=enumerate)
    app.run(debug=True)