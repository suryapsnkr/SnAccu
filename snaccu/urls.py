from django.urls import path
from snaccu.views import SignupUser, LoginUser, GetUser, QuerySearch, FriendRequest, FriendAccept, LogoutUser, GetCSRFToken, FriendList, FriendReject, ChangePassword


urlpatterns = [
    path('changePassword', ChangePassword.as_view(), name='changePassword'),
    path('friendList/<int:n>', FriendList.as_view(), name='friendList'),
    path('getCookie', GetCSRFToken.as_view(), name='getCookie'),
    path('logoutUser', LogoutUser.as_view(), name='logoutUser'),
    path('friendReject', FriendReject.as_view(), name='friendReject'),
    path('friendAccept', FriendAccept.as_view(), name='friendAccept'),
    path('friendRequest', FriendRequest.as_view(), name='friendRequest'),
    path('querySearch', QuerySearch.as_view(), name='querySearch'),
    path('getUsers/<int:n>', GetUser.as_view(), name='getUsers'),
    path('loginUser', LoginUser.as_view(), name='loginUser'),
    path('signupUser', SignupUser.as_view(), name='signupUser'),
]