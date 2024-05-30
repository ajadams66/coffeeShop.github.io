import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "Your Secret Key"
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class NewPost(FlaskForm):
    name = StringField(label="Name of the business", validators=[DataRequired()])
    location = StringField(label="City and state location", validators=[DataRequired()])
    seats = StringField(label='how many does this building sit', validators=[DataRequired()])
    toilet = StringField(label='This Business has toilets for patrons?(true or false)', validators=[DataRequired()])
    wifi = StringField(label="This place have wifi?(true or false)", validators=[DataRequired()])
    coffee_price = StringField(label="What is the price of a regular sized Coffee", validators=[DataRequired()])
    electrical_outlet = StringField(label="This place have Electrical Outlets for patrons?(true or false)",
                                    validators=[DataRequired()])
    can_take_calls = StringField(label="We are able to call the Shop?(true or false)", validators=[DataRequired()])
    img = StringField(label="URL image for the business or it's Logo?", validators=[DataRequired(), URL()])
    map = StringField("map url for the location", validators=[DataRequired(), URL()])
    submit = SubmitField('add')


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = []
    CafePost = db.session.query(Cafe).all()
    for post in CafePost:
        posts.append(post)
    return render_template("index.html", all_posts=posts)


@app.route('/<int:post_id>', methods=['GET', 'POST'])
def show_cafe(post_id):
    requested_post = db.session.get(Cafe, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST', 'PATCH'])
def edit(post_id):
    requested_post = db.get_or_404(Cafe, post_id)
    edit_form = NewPost(
        name=requested_post.name,
        location=requested_post.location,
        seats=requested_post.seats,
        # img=requested_post.img_url,
        toilet=requested_post.has_toilet,
        wifi=requested_post.has_wifi,
        coffee_price=requested_post.coffee_price,
        electrical_outlet=requested_post.has_sockets,
        map=requested_post.map_url,
        can_take_calls=requested_post.can_take_calls
    )
    if edit_form.validate_on_submit():
        requested_post.name = edit_form.name.data
        requested_post.location = edit_form.location.data
        requested_post.coffee_price = edit_form.coffee_price
        requested_post.seats = edit_form.seats.data
        # requested_post.img_url = edit_form.img.data
        requested_post.has_toilet = bool(edit_form.toilet.data)
        requested_post.has_wifi = bool(edit_form.wifi.data)
        requested_post.has_sockets = bool(edit_form.electrical_outlet.data)
        requested_post.map_url = edit_form.map.data
        requested_post.can_take_calls = bool(edit_form.can_take_calls.data)
        db.session.commit()
        db.session.close()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=edit_form, is_edit=True)



@app.route('/new-cafe', methods=['GET', 'POST'])
def new_cafe():
    form = NewPost()
    if form.validate_on_submit():
        new_place = Cafe(
            name=request.form["name"],
            location=request.form["location"],
            seats=request.form["seats"],
            img_url=request.form["img"],
            has_toilet=bool(request.form["toilet"]),
            has_wifi=bool(request.form["wifi"]),
            has_sockets=bool(request.form["electrical_outlet"]),
            map_url=request.form["map"],
            can_take_calls=bool(request.form["can_take_calls"])
        )
        db.session.add(new_place)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/delete/<int:post_id>", methods=['GET', 'POST', 'DELETE'])
def delete(post_id):
    post = db.get_or_404(Cafe, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
