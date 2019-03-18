# from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Game

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate

from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import status, mixins

from .helpers import gen_map_data, init_map_snapshot, ReadCreateAndPatchOnly, CreateOnly, update_snapshot_of_game, is_win, is_lose
from .auth import create_jwt

from .serializers import GameSerializer, UserSerializer, SignupSerializer

# ViewSets define the view behavior.


class GameViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadCreateAndPatchOnly,)
    queryset = Game.objects.filter(is_deleted=False)
    serializer_class = GameSerializer

    def list(self, request):
        print(request.user)
        if request.user:
            games = request.user.game_set
            serializer = self.serializer_class(games, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            size_x = request.data['size_x']
            size_y = request.data['size_y']
            mine_num = request.data['mine_num']
            data = gen_map_data(size_x, size_y, mine_num)
            if data:
                snapshot = init_map_snapshot(size_x, size_y)
                serializer.save(map_data=data,  snapshot=snapshot,
                                player=request.user if request.user else None)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'Error: mine number cannot be larger than the map size'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        # get user operation
        x = request.data['posX']
        y = request.data['posY']
        is_flag = request.data['is_flag']

        # get object from database
        game = self.get_object()

        
        # determin if already lose
        if (not is_flag) and is_lose(game.map_data, x, y):
            data = {'snapshot': game.map_data, 'status': 'LT'}
        
        else:
            result = update_snapshot_of_game(
                    game.map_data, game.snapshot, x, y, is_flag)
            # determin if already win
            if is_win(result, game.map_data, x, y):
                data = {'snapshot': game.map_data, 'status': 'WN'}
            # caculate new snapshot based on last operation
            else: 
                data = {'snapshot': result}

        # update data
        serializer = self.serializer_class(game, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadCreateAndPatchOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, requsest):
        if not requsest.user or not requsest.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            queryset = User.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        password_hash = make_password(request.data.get('password'))
        data = request.data.copy()
        data['password'] = password_hash
        serializer = SignupSerializer(data=data)

        if serializer.is_valid():
            instance = serializer.save()
            jwt_token = create_jwt(
                {'id': instance.id, 'username': instance.username})

            serializer = self.serializer_class(instance)
            data = serializer.data.copy()
            data['token'] = jwt_token
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = (CreateOnly,)

    def create(self, request):
        # todo
        username = request.data.get('username')
        password = request.data.get('password')
        if(not username or not password):
            return SignupSerializer(request.data).error
        # password_hash = make_password(request.data.get('password'))
        try:
            user = User.objects.get(username=username)
            if(check_password(password, user.password)):
                jwt_token = create_jwt(
                    {'id': user.id, 'username': user.username})
                return Response({'token': jwt_token, 'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
            else:
                return Response({'Error': "Invalid username/password"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'Error': "Invalid username/password"}, status=status.HTTP_400_BAD_REQUEST)
