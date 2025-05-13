from django.test import TestCase, Client
from django.urls import reverse
from .models import Movie

class MovieTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.movie = Movie.objects.create(
            title="Inception",
            director="Christopher Nolan",
            release_year=2010
        )

    def test_movie_creation(self):
        self.assertEqual(self.movie.title, "Inception")
        self.assertEqual(self.movie.directors, "Christopher Nolan")
        self.assertEqual(self.movie.release_year, 2010)

    def test_movie_list_view(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_list.html')
        self.assertContains(response, self.movie.title)
        self.assertIn('movies', response.context)
        self.assertEqual(len(response.context['movies']), 1)
        self.assertEqual(response.context['movies'][0], self.movie)

    def test_movie_detail_view(self):
        response = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_detail.html')
        self.assertContains(response, self.movie.title)
        self.assertContains(response, self.movie.directors)
        self.assertContains(response, self.movie.release_year)
        self.assertIn('movie', response.context)
        self.assertEqual(response.context['movie'], self.movie)