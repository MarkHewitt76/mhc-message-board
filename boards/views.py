from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .models import Post
from .forms import (
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm
)


class PostList(generic.ListView):
    """
    View for all published posts, in descending order, using
    Post model and inheriting from generic list view model.
    To be used on homepage.
    """

    model = Post
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'


class FullPost(View):
    """
    View for a single post, selected by the user, displaying
    comments and likes. The url for each individual post is derived
    from the Post model's slug field which is, in turn,
    populated by the title.
    """

    def get(self, request, slug, *args, **kwargs):
        """
        Method to get post object.
        """

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "full_post.html",
            {
                "post": post,
                "comments": comments,
                "liked": liked
            },
        )
    

class CreatePost(generic.CreateView):
    """
    View for all post creation form, using the Post model
    and inheriting from generic create view model.
    """

    model = Post
    fields = ['title', 'category', 'content', 'post_image']

    def form_valid(self, form):
        """
        Method to override CreateView form_valid method in order
        to set author and slug fields of Post model.
        """

        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        form.instance.status = 1
        return super().form_valid(form)


def register(request):
    """
    Function view for user registration form
    """

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f"Your account has been created! You are now able to log in."
            )
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    """
    Function for user profile view.
    """

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.user_profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(
                request, f'Your account has been updated successfully!'
            )
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.user_profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile.html', context)
