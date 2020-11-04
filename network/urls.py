
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    path("user/<int:user_id>", views.user_view, name="user_view"),
    path("user/<int:user_id>/follow", views.follow_user, name="follow_user"),

    # API routes
    path("post/<int:post_id>", views.update_post, name="update_post"),
    path("like/<int:post_id>", views.like_unlike_post, name="like_unlike_post")
]
