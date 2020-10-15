"""View functions of the Posts app."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    """
    Display last posts :model:'posts.Post' on the main page.

    **Context**

    ''post_list''
        All posts :model:'posts.Post'.

    **Template**

    :template:'index.html'

    """
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {
            'page': page,
            'paginator': paginator,
        }
    )


def group_posts(request, slug='leo'):
    """
    Display last posts :model:'posts.Post'.

    For specified :model:'posts.Group' with default slug 'leo'
    if no slug is specified.

    **Context**

    ''group''
        :model:'posts.Group' corresponding to slug.
    ''post_list''
        :model:'posts.Post' in group.

    **Template**

    :template:'group.html'

    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {
            'group': group,
            'page': page,
            'paginator': paginator,
        }
    )


@login_required
def new_post(request):
    """
    Process new post form.

    Display page with form if user is authorized.
    Process results and redirect to main page after submit.

    **Context**

    ''new_post_form''
        'forms.PostForm' model form to publish new post.

    **Template**

    :template:'new_post.html'

    """
    new_post_form = PostForm(request.POST or None)
    if not new_post_form.is_valid():
        return render(request, 'new_post.html', {'form': new_post_form})

    post = new_post_form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(reverse('index'))


def profile(request, username):
    """
    Display profile info for 'username' and all his posts :model:'posts.Post'.

    **Context**

    ''author''
        :model:'posts.User' specified by 'username'.

    ''post_list''
        All posts :model:'posts.Post' for 'username'.

    **Template**

    :template:'profile.html'

    """
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    following = (Follow.objects.filter(author=author,
                                       user=request.user).exists()
                 if request.user.is_authenticated
                 else False)

    return render(
        request,
        'profile.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'following': following,
        }
    )


def post_view(request, username, post_id):
    """
    Display post for 'username' and 'post_id'.

    **Context**

    ''author''
        :model:'posts.User' specified by 'username'.

    ''post''
        Post :model:'posts.Post' specified by 'username' and 'post_id'.

    **Template**

    :template:'post.html'

    """
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    comment_form = CommentForm(request.POST or None)
    if not comment_form.is_valid():
        return render(
            request,
            'post.html',
            {
                'post': post,
                'author': author,
                'comments': comments,
                'form': comment_form,
            }
        )


@login_required
def add_comment(request, username, post_id):
    """
    Process new comment form.

    Display page with post.
    Save results and redirect to post page after submit.

    **Context**

    'post'
        'models.Post' post's data to comment.

    'form'
        'forms.CommentForm' model form to post a comment.

    **Template**

    :template:'post.html'

    """
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(reverse('post', args=(username, post_id)))


@login_required
def post_edit(request, username, post_id):
    """
    Process edit post form.

    Display page with form if user is the author of the post.
    Save results and redirect to post page after submit.

    **Context**

    'post'
        'models.Post' post's data to edit.

    'form'
        'forms.PostForm' model form to edit post.

    **Template**

    :template:'new_post.html'

    """
    if request.user.username != username:
        return redirect(reverse('post', args=(username, post_id)))

    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(
            request,
            'new_post.html',
            {'form': form, 'post': post}
        )

    post = form.save()
    return redirect(reverse('post', args=(username, post_id)))


def page_not_found(request, exception):
    """Display custom page if page not found."""
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Display custom page in case of server error."""
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    """
    Display posts of the following author for user.

    **Context**

    'following'
        All following :model:'posts.Follow' of the user.

    **Template**

    :template:'follow.html'

    """
    followings = Follow.objects.filter(user=request.user)
    post_list = Post.objects.filter(
        author__following__in=followings)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {
            'page': page,
            'paginator': paginator,
        }
    )


@login_required
def profile_follow(request, username):
    """
    Follow the author.

    Redirect on author's profile page after action.
    """
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if not follower.exists() and author != request.user:
        Follow.objects.create(user=request.user, author=author)

    return redirect(reverse('profile', args=(username,)))


@login_required
def profile_unfollow(request, username):
    """
    Unfollow the author.

    Redirect on author's profile page after action.
    """
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect(reverse('profile', args=(username,)))
