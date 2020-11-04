import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Like


def index(request):
    if request.method == "POST":
        content = request.POST["body"]
        post = Post(creator=request.user, content=content)
        post.save()
    posts = Post.objects.order_by("-timestamp").all()
    return render(request, "network/index.html", {
        "page_obj": make_listing(request, posts)
    })


def following(request):
    ordered_posts = Post.objects.order_by("-timestamp")
    posts = []
    i = 0
    for user in request.user.follow_users.all():
        if i == 0:
            posts = ordered_posts.filter(creator=user)
        else:
            posts = posts | ordered_posts.filter(creator=user)
        i += 1

    return render(request, "network/posts_template.html", {
        "page_obj": make_listing(request, posts)
    })


# decorating our list with pagination
def make_listing(request, posts):
    paginator = Paginator(posts, 10)
    if request.method == "GET":
        page_number = request.GET.get("page")
    else:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    return page_obj


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def user_view(request, user_id):
    if not request.user.is_authenticated:
        return render(request, "network/log_in_alert.html")
    # owner of the profile
    owner = User.objects.get(id=user_id)
    is_following = False
    followers = request.user.follow_users

    try:
        followers.get(id=user_id)
        is_following = True
    except User.DoesNotExist:
        pass

    return render(request, "network/user_site.html", {
        "owner": owner,
        "is_following": is_following,
        "page_obj": make_listing(request, Post.objects.order_by("-timestamp").filter(creator=owner))
    })


def follow_user(request, user_id):
    if request.method != "POST":
        return HttpResponseRedirect("index")
    owner = User.objects.get(id=user_id)
    user_followers = request.user.follow_users

    try:
        user_followers.get(id=user_id)
        user_followers.remove(owner)
    except User.DoesNotExist:
        user_followers.add(owner)

    return user_view(request, user_id)


@csrf_exempt
@login_required
def update_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "PUT":
        if request.user.id != post.creator.id:
            return JsonResponse({
                "error": "You have not permission for editing this post."
            }, status=400)
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return HttpResponse(status=204)

    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


@csrf_exempt
@login_required
def like_unlike_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        if post.is_liking(request.user):
            is_increase = "false"
            like = Like.objects.get(creator=request.user, post=post_id)
            like.delete()
        else:
            is_increase = "true"
            like = Like(creator=request.user, post=post)
            like.save()
        return JsonResponse({
            "is_increase": is_increase
        }, status=201)

    else:
        return JsonResponse({
            "error": "POST method required"
        }, status=400)
