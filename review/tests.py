from django.test import TestCase
from django.contrib.auth.models import User
from movie.models import Movie
from .models import Review

class ReviewModelTest(TestCase):

    def setUp(self):
        # Create a user instance
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create a movie instance
        self.movie = Movie.objects.create(title='Test Movie', description='Test Description')

    def test_review_creation(self):
        # Create a review instance
        review = Review.objects.create(user=self.user, movie=self.movie, rating=4.5, comment='Great movie!')
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.movie, self.movie)
        self.assertEqual(review.rating, 4.5)
        self.assertEqual(review.comment, 'Great movie!')

    def test_review_str(self):
        # Create a review instance
        review = Review.objects.create(user=self.user, movie=self.movie, rating=4.5, comment='Great movie!')
        self.assertEqual(str(review), f"{self.user.username} - {self.movie.title}")

    def test_default_rating(self):
        # Create a review instance without specifying the rating
        review = Review.objects.create(user=self.user, movie=self.movie, comment='Great movie!')
        self.assertEqual(review.rating, 0)

    def test_review_deletion_on_user_delete(self):
        # Create a review instance
        review = Review.objects.create(user=self.user, movie=self.movie, rating=4.5, comment='Great movie!')
        # Delete the user
        self.user.delete()
        # Check if the review is deleted
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_review_deletion_on_movie_delete(self):
        # Create a review instance
        review = Review.objects.create(user=self.user, movie=self.movie, rating=4.5, comment='Great movie!')
        # Delete the movie
        self.movie.delete()
        # Check if the review is deleted
        self.assertFalse(Review.objects.filter(id=review.id).exists())