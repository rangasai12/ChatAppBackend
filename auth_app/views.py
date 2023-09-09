from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Message
from .serializers import UserSerializer,OnlineUserSerializer,MessageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    
    user.is_active = True
    user.save()
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data["username"]})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("{}".format(request.user.email))



@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    # Get the current authenticated user
    user = request.user

    user.is_active = False
    user.save()

    return Response("User has been logged out successfully.", status=status.HTTP_200_OK)


@api_view(['GET'])
def online_users(request):
    # Retrieve all users where 'is_active' is True
    online_users = User.objects.filter(is_active=True)
    
    # Serialize the online users using the custom serializer
    serializer = OnlineUserSerializer(online_users, many=True)
    
    return Response(serializer.data)

## Rest API for Chatting 

# @api_view(['POST'])
# @authentication_classes([SessionAuthentication, TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def send_message(request):
#     receiver_username = request.data.get('receiver_username')
#     content = request.data.get('content')

#     if request.user.username == receiver_username:
#         return Response("You cannot send a message to yourself.", status=status.HTTP_400_BAD_REQUEST)

#     try:
#         receiver = User.objects.get(username=receiver_username, is_active=True)
#     except User.DoesNotExist:
#         return Response("Receiver not found or is not online.", status=status.HTTP_404_NOT_FOUND)

#     if request.user == receiver:
#         return Response("You cannot send a message to yourself.", status=status.HTTP_400_BAD_REQUEST)

#     message = Message(sender=request.user, receiver=receiver, content=content)
#     message.save()

#     serializer = MessageSerializer(message)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def get_messages(request):
#     sender_username = request.query_params.get('sender_username')

#     # Check if the sender is the authenticated user

#     try:
#         sender = User.objects.get(username=sender_username, is_active=True)
#     except User.DoesNotExist:
#         return Response("Sender not found or is not online.", status=status.HTTP_404_NOT_FOUND)

#     messages = Message.objects.filter(sender=sender, receiver=request.user) | Message.objects.filter(sender=request.user, receiver=sender)
#     messages = messages.order_by('timestamp')

#     serializer = MessageSerializer(messages, many=True)
#     return Response(serializer.data)



# Load the JSON data (assuming it's stored in a file named 'users.json')
json_file_path = os.path.join(settings.BASE_DIR, 'users.json')
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)
    users = data['users']

# Ensure a consistent dimensionality for user profiles
max_interests = ["movies", "music", "cars", "travelling", "computers", "dancing", "drawing", "photography","singing","cooking"]
num_interests = len(max_interests)

@api_view(['GET'])
def suggested_friends(request, user_id):
    try:
        # Find the target user based on user_id
        target_user = next(user for user in users if user['id'] == int(user_id))
    except StopIteration:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    # Normalize interests
    def normalize_interests(interests, max_interests):
        max_score = max(interests.values())
        return {interest: interests.get(interest, 0) / max_score for interest in max_interests}

    # Create user profiles with consistent dimensionality
    def create_profile(user):
        # Normalize interests
        normalized_interests = normalize_interests(user["interests"], max_interests)
        
        # Create a profile vector that includes interests and age
        profile_vector = [normalized_interests[interest] for interest in max_interests]
        profile_vector.append(user["age"])
        
        return profile_vector

    # Calculate cosine similarity between profiles of two users
    def calculate_similarity(user1, user2):
        profile1 = create_profile(user1)
        profile2 = create_profile(user2)
        return cosine_similarity([profile1], [profile2])[0][0]

    # Calculate similarity scores for all users
    similarity_scores = []
    for user in users:
        if user["id"] != target_user["id"]:
            similarity_score = calculate_similarity(target_user, user)
            similarity_scores.append((user, similarity_score))

    # Sort users by similarity score in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # Return the top 5 recommended friends
    top_recommendations = similarity_scores[:5]
    recommended_friends = [{"id": user[0]["id"], "name": user[0]["name"]} for user in top_recommendations]

    return Response(recommended_friends, status=status.HTTP_200_OK)