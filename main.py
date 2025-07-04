from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired
import requests


API_KEY = "aa2ae94247da6d219a6f48e3eb0cab90"
url = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top10Movies-collection.db"
Bootstrap5(app)
# CREATE DB
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)
# CREATE TABLE

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Movie %r>' % self.title

with app.app_context():
    db.create_all()

# with app.app_context():
#     second_movie = Movie(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         ranking=9,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#     db.session.commit()

class MovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

class AddForm(FlaskForm):
    title = StringField("Movie title")
    submit = SubmitField("Add movie")

@app.route("/")
def home():
    movies = db.session.query(Movie).all()
    return render_template("index.html", movies=movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = MovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        new_rating = float(form.rating.data)
        movie.rating = new_rating
        new_review = form.review.data
        movie.review = new_review
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(url, params={"api_key": API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)
@app.route("/details", methods=["GET", "POST"])
def details():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        form = MovieForm()
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],

            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"],

            rating = 0.0,
            ranking = 0,
            review = ""
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)


#overview, vote_average,