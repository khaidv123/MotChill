# Import necessary modules
from django.test import TestCase
from django.contrib.auth.models import User
from movie.models import Movie
from .models import UserProfile

class UserProfileModelTest(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create movie instances
        self.movie1 = Movie.objects.create(title='Movie 1', description='Description 1')
        self.movie2 = Movie.objects.create(title='Movie 2', description='Description 2')
        # Create a user profile instance
        self.user_profile = UserProfile.objects.create(user=self.user)

    def test_user_profile_creation(self):
        # Test if the user profile is created and associated with the user
        self.assertEqual(self.user_profile.user.username, 'testuser')

    def test_watchlist_association(self):
        # Add movies to the watchlist
        self.user_profile.watchlist.add(self.movie1, self.movie2)
        # Test if the movies are added to the watchlist
        self.assertIn(self.movie1, self.user_profile.watchlist.all())
        self.assertIn(self.movie2, self.user_profile.watchlist.all())

    def test_str_method(self):
        # Test the string representation of the user profile
        self.assertEqual(str(self.user_profile), 'testuser')