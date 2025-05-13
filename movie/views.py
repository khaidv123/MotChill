

import datetime
from itertools import zip_longest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.contrib import messages
from .forms import MovieForm
from review.forms import ReviewForm
from .models import Movie
from user_profile.models import UserProfile
from subscription.models import UserSubscription
from review.models import Review

from models.src.recommend import get_recommendations

def movie_list(request):
    """Renders a list of movies."""
    movies_list = Movie.objects.all()
    query = request.GET.get('q')
    
    if query:
        movies_list = movies_list.filter(
            Q(title__icontains=query) 
            #Q(genre__icontains=query) |
            #Q(description__icontains=query) |
            #Q(directors__icontains=query) |
            #Q(country__icontains=query)
        )

    paginator = Paginator(movies_list, 12)
    page = request.GET.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    context = {
        'movies': movies,
        'query': query,
    }
    return render(request, 'movie/movie_list.html', context)










def popular_movies(request):
    """Renders a list of popular movies."""
    popular_movies_list = Movie.objects.filter(tags__name='most popular')
    query = request.GET.get('q')
    
    if query:
        popular_movies_list = popular_movies_list.filter(
            Q(title__icontains=query) |
            Q(genre__icontains=query) |
            Q(description__icontains=query) |
            Q(directors__icontains=query) |
            Q(country__icontains=query)
        )
        
    paginator = Paginator(popular_movies_list, 12)
    page = request.GET.get('page')

    try:
        popular_movies = paginator.page(page)
    except PageNotAnInteger:
        popular_movies = paginator.page(1)
    except EmptyPage:
        popular_movies = paginator.page(paginator.num_pages)
        
    context = {
        'popular_movies': popular_movies,
        'query': query,
    }
    return render(request, 'movie/most_popular.html', context)






def tv_series(request):
    """Renders a list of tv series."""
    tv_series_list = Movie.objects.filter(tags__name='tv series')
    query = request.GET.get('q')
    
    if query:
        tv_series_list = tv_series_list.filter(
            Q(title__icontains=query) |
            Q(genre__icontains=query) |
            Q(description__icontains=query) |
            Q(directors__icontains=query) |
            Q(country__icontains=query)
        )
        
    paginator = Paginator(tv_series_list, 12)
    page = request.GET.get('page')

    try:
        tv_series = paginator.page(page)
    except PageNotAnInteger:
        tv_series = paginator.page(1)
    except EmptyPage:
        tv_series = paginator.page(paginator.num_pages)
        
    context = {
        'tv_series': tv_series,
        'query': query,
    }
    return render(request, 'movie/tv_series.html', context)




def new_movies(request):
    """Renders a list of new movies."""
    new_movies_list = Movie.objects.filter(tags__name='new movies')
    query = request.GET.get('q')
    
    if query:
        new_movies_list = new_movies_list.filter(
            Q(title__icontains=query) |
            Q(genre__icontains=query) |
            Q(description__icontains=query) |
            Q(directors__icontains=query) |
            Q(country__icontains=query)
        )
        
    paginator = Paginator(new_movies_list, 12)
    page = request.GET.get('page')

    try:
        new_movies = paginator.page(page)
    except PageNotAnInteger:
        new_movies = paginator.page(1)
    except EmptyPage:
        new_movies = paginator.page(paginator.num_pages)
        
    context = {
        'new_movies': new_movies,
        'query': query,
    }
    return render(request, 'movie/new_movies.html', context)





def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    reviews = Review.objects.filter(movie=movie)
    reviews_count = reviews.count()
    in_watchlist = False

    rated_movies = []

    if request.user.is_authenticated:
        user_reviews = Review.objects.filter(user=request.user).values_list(
            "movie__id", "rating"
        )
        rated_movies = list(user_reviews)

    top_k = 10
    user_id = request.user.id if request.user.is_authenticated else None

    if user_id is not None and rated_movies:
        recommendations = get_recommendations(user_id, rated_movies, top_k)
        
        top_movies_movieId = [movieId for movieId, _ in recommendations]
        related_movies_by_tags = Movie.objects.filter(id__in=top_movies_movieId)

    else:
        related_movies_by_tags = (
            Movie.objects.filter(tags__in=movie.tags.all())
            .exclude(slug=slug)
            .distinct()[:10]
        )

    if movie.subscription_required:
        user_subscription = UserSubscription.objects.filter(user=request.user).first()
        if not user_subscription or user_subscription.end_date < datetime.date.today():
            return redirect("subscription:subscriptions_list")

    # Check if the movie is in the user's watchlist
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile:
            in_watchlist = user_profile.watchlist.filter(slug=movie.slug).exists()

    # Generating stars_list for reviews
    stars_list = []
    for review in reviews:
        rating = int(review.rating)
        stars = ["fa fa-star text-yellow-300" for _ in range(rating)]
        stars.extend(
            ["fa fa-star text-gray-300 dark:text-gray-500" for _ in range(5 - rating)]
        )
        stars_list.append(stars)

    # Zip reviews and stars_list together
    review_stars_zip = list(zip_longest(reviews, stars_list))

    # Handle review submission
    if request.method == "POST":
        existing_review = Review.objects.filter(movie=movie, user=request.user).exists()
        if existing_review:
            messages.error(
                request, "You have already reviewed this movie.", extra_tags="error"
            )
            return redirect("movies:movie_detail", slug=slug)

        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user
            new_review.movie = movie
            new_review.save()

            messages.success(
                request,
                "Your review has been successfully added!",
                extra_tags="success",
            )

            return redirect("movies:movie_detail", slug=slug)
    else:
        form = ReviewForm()

    # Paginate reviews
    paginator = Paginator(reviews, 5)  # Show 5 reviews per page
    page_number = request.GET.get("page")
    try:
        paginated_reviews = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_reviews = paginator.page(1)
    except EmptyPage:
        paginated_reviews = paginator.page(paginator.num_pages)

    context = {
        "movie": movie,
        "in_watchlist": in_watchlist,
        "reviews_count": reviews_count,
        "related_movies": related_movies_by_tags,
        "form": form,
        "paginated_reviews": paginated_reviews,
        "review_stars_zip": review_stars_zip,
    }
    return render(request, "movie/movie_detail.html", context)









def movie_create(request):
    """Handles the creation of a new movie."""
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
        else:
            return render(request, 'movie/movie_form.html', {'form': form})
    else:
        form = MovieForm()
    return render(request, 'movie/movie_form.html', {'form': form})

def movie_update(request, slug):
    """Handles updating an existing movie."""
    movie = get_object_or_404(Movie, slug=slug)
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
        else:
            return render(request, 'movie/movie_form.html', {'form': form})
    else:
        form = MovieForm(instance=movie)
    return render(request, 'movie/movie_form.html', {'form': form})

def movie_delete(request, slug):
    """Handles the deletion of an existing movie."""
    movie = get_object_or_404(Movie, slug=slug)
    if request.method == 'POST':
        try:
            movie.delete()
            return redirect('movie_list')
        except Exception as e:
            return HttpResponseBadRequest("Error deleting movie.")
    return render(request, 'movie/movie_confirm_delete.html', {'movie': movie})
