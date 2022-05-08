
from flask import render_template,request,redirect,url_for,abort
from . import main
from ..requests import get_movies,get_movie,search_movie
import markdown2
from .forms import ReviewForm,UpdateProfile
from .. import db,photos
from ..models import Review,User
from flask_login import login_required, UserMixin,current_user
 

# from ..forms import ReviewForm
# Reviews = Review.all_review


# Views
@main.route('/')
def index():
    '''
    View root page function that returns the index page and its data
    '''
    popular_movies = get_movies('popular') # Call our get_movies() function and pass in "popular" as an argument. 
    upcoming_movies = get_movies('upcoming') # Call our get_movies() function and pass in "upcoming" as an argument. 
    now_showing_movies = get_movies('now_playing') # Call our get_movies() function and pass in "now_playing" as an argument. 

    title = 'Home - Welcome to The best Movie Review Website Online'

    search_movie = request.args.get('movie_query') # We pass in the name of the query and the value is returned.

    if search_movie:
        # redirect function that redirects us to another view function.
        return redirect(url_for('.search', movie_name = search_movie))  # url_for function that passes in the search view function together with the dynamic movie_name
    return render_template('index.html', title = title, popular = popular_movies, upcoming = upcoming_movies, now_showing = now_showing_movies) # searches for the template file in our app/templates/ sub directory and loads it.

@main.route('/movie/<int:id>') # Angle brackets <> is dynamic. And any route mapped to this will be passed.
def movie(id):
    '''
    View movie page function that returns the movie details page and its data
    '''
    movie = get_movie(id) # Call our get_movies() function and pass in a movie id as an argument. 
    title = f'{movie.title}' # Use movie's title as page title.
    reviews = Review.get_reviews(movie.id)
    return render_template('movie.html', title = title, movie = movie, reviews = reviews)



@main.route('/search/<movie_name>')
def search(movie_name):
    '''
    View function to display the search results
    '''
    movie_name_list = movie_name.split(' ')
    movie_name_format = "+".join(movie_name_list)
    searched_movies = search_movie(movie_name_format)
    title = f'search results for {movie_name}'
    return render_template('search.html', title=title, movies=searched_movies)

@main.route('/movie/review/new/<int:id>', methods = ['GET','POST'])
@login_required
def new_review(id):
    form = ReviewForm()
    movie = get_movie(id)
    if form.validate_on_submit():
        title = form.title.data
        review = form.review.data

        # Updated review instance
        new_review = Review(movie_id=movie.id,movie_title=title,image_path=movie.poster,movie_review=review,user=current_user)

        # save review method
        new_review.save_review()
        return redirect(url_for('.movie',id = movie.id ))

    title = f'{movie.title} review'
    return render_template('new_review.html',title = title, review_form=form, movie=movie)

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template("profiles/profile.html", user = user)

@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))

    return render_template('profiles/update.html',form =form)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/review/<int:id>')
def single_review(id):
    review=Review.query.get(id)
    if review is None:
        abort(404)
    format_review = markdown2.markdown(review.movie_review,extras=["code-friendly", "fenced-code-blocks"])
    return render_template('review.html',review = review,format_review=format_review)