from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
class MovieForm(FlaskForm):
    rating = StringField('Your rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    Submit = SubmitField('Submit')
class Base(DeclarativeBase):
    pass
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your'
Bootstrap5(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[int] = mapped_column(Integer, nullable=False)
    img_url: Mapped[str] = mapped_column(String(400), nullable=False)

with app.app_context():
    db.create_all()
@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)
@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    movie = Movie.query.get(id)
    movie_title = movie.title
    form = MovieForm()
    if form.validate_on_submit():
        if movie:
            movie.rating = float(form.rating.data)
            movie.review = form.review.data
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('edit.html', movie=movie, form=form, movie_title=movie_title)
class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    description = StringField("Movie Description", validators=[DataRequired()])
    year = StringField("Year", validators=[DataRequired()])
    rating = StringField("Rating", validators=[DataRequired()])
    ranking = StringField("Ranking", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired()])
    submit = SubmitField("Add Movie")
@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))
@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        new_movie = Movie(title=form.title.data, description=form.description.data, year=form.year.data, rating=form.rating.data, ranking=form.ranking.data, review=form.review.data, img_url=form.img_url.data)
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)
if __name__ == '__main__':
    app.run(debug=True)
