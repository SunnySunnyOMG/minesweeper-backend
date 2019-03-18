from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status
from django.contrib.auth.hashers import check_password

from .auth import create_jwt
from .helpers import gen_map_data, init_map_snapshot
# models
from django.contrib.auth.models import User
from .models import Game
# Create your tests here.


class UserTests(APITestCase):
    def test_should_create_user_when_give_password_and_username(self):
        """
        Ensure we can create a new user object
        """
        data = {'username': 'zhe_xu', 'password': '123'}
        response = self.client.post('/api/users', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(check_password('123', User.objects.get().password))
        self.assertNotEqual('123', User.objects.get().password)

    def test_should_create_user_when_additional_info_provided(self):
        data = {'username': 'zhe_xu', 'password': '123',
                'first_name': 'zhe', 'last_name': 'xu'}
        response = self.client.post('/api/users', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().first_name, 'zhe')
        self.assertEqual(User.objects.get().last_name, 'xu')

    def test_should_not_create_user_when_missing_required_field(self):
        data = {'username': ''}
        response = self.client.post('/api/users', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_return_token_when_create(self):
        data = {'username': 'aaa', 'password': 'bbb'}
        response = self.client.post('/api/users', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_should_not_get_user_list(self):
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LoginTests(APITestCase):
    def setUp(self):
        # sign up a user
        data = {'username': 'zhe_xu', 'password': '123'}
        response = self.client.post('/api/users', data, format='json')
        self.token = response.data.get('token')
        self.user = User.objects.get()

    def test_should_login_and_get_token(self):
        response = self.client.post(
            '/api/login', {'username': 'zhe_xu', 'password': '123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)


class GameTests(APITestCase):
    def setUp(self):
        # fake data
        self.data = {'size_x': '10', 'size_y': '11', 'mine_num': '5'}
        # sign up a user
        self.username = 'zhe_xu'
        data = {'username': self.username, 'password': '123'}
        response = self.client.post('/api/users', data, format='json')
        self.token = response.data.get('token')
        self.user = User.objects.get()
        self.jwt_token = create_jwt(
            {'id': self.user.id, 'username': self.username})

    def test_should_create_game(self):
        response = self.client.post('/api/games', self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        game = Game.objects.get()
        self.assertIn('snapshot', response.data)
        self.assertNotIn('map_data', response.data)
        self.assertEqual(Game.objects.count(), 1)
        self.assertIsNotNone(game.id)
        self.assertIsNotNone(game.map_data)
        self.assertEqual(game.size_x, 10)
        self.assertEqual(game.size_y, 11)
        self.assertEqual(game.player, None)

    def test_should_not_create_game_when_missing_field(self):
        response = self.client.post(
            '/api/games', {'size_x': '10', 'mine_num': '5'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_not_create_game_when_mine_num_exceed(self):
        response = self.client.post(
            '/api/games', {'size_x': '10', 'size_y': '10', 'mine_num': '101'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_not_create_game_when_data_is_invalid(self):
        response = self.client.post(
            '/api/games', {'size_x': '-10', 'size_y': '10', 'mine_num': '101'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_not_return_game_list_for_guest(self):
        response = self.client.get('/api/games')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_link_to_user_when_has_auth_in_header(self):
        self.with_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt_token.decode('utf-8'))
        response = self.client.post('/api/games', self.data)
        self.assertEqual(response.data.get('player'), self.user.id)

    def test_should_return_games_list_for_loginned_user(self):
        self.with_token()
        self.create_my_game()
        self.create_my_game()
        self.create_others_game()

        response = self.client.get('/api/games')

        self.assertEqual(len(response.data), self.user.game_set.count())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

   
    def create_my_game(self):
        self._create_a_game(2,2,1, self.user)
    
    def create_others_game(self):
        self._create_a_game(2,2,1, None)

    def with_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt_token.decode('utf-8'))

    def _create_a_game(self, size_x, size_y, mine_num, player):
      Game.objects.create(size_x=size_x, size_y=size_y, mine_num=mine_num, map_data=gen_map_data(
          size_x, size_y, mine_num), player=player, snapshot=init_map_snapshot(size_x, size_y))