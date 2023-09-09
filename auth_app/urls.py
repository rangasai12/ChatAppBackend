from django.urls import path
from .views import signup, login, test_token,logout,online_users,suggested_friends # send_message,get_messages,

urlpatterns = [
    path('signup', signup, name='signup'),
    path('login', login, name='login'),
    path('protected', test_token, name='protected'),  # Add this line
    path('logout',logout,name="logout"),
    path("onlineusers",online_users, name="onlineusers"),
    # path('send_message', send_message, name='send_message'),
    # path('get_messages', get_messages, name='get_messages'),
    path('suggested_friends/<int:user_id>/', suggested_friends, name='suggested_friends'),
]
