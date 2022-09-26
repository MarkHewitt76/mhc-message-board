from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
    reverse
)
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Category, Post, Comment
from .forms import (
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm,
    CommentForm,
    ContactForm
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
    paginate_by = 6


class UserPostList(generic.ListView):
    """
    View for all published posts by a specific user, in
    descending order, using Post model and inheriting
    from generic list view model.
    """

    model = Post
    template_name = 'user_posts.html'
    paginate_by = 6

    def get_queryset(self):
        """
        Method to return posts restricted to 'published' status AND to
        authorship by the user whose username is the parameter in the
        url specified by the corresponding path in url patterns.
        """

        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(
            status=1, author=user
            ).order_by('-created_on')


class CategoryList(generic.ListView):
    """
    View for all published posts in a specific category, in
    descending order, using Post model and inheriting
    from generic list view model.
    """

    model = Post
    template_name = 'category_posts.html'
    paginate_by = 6

    def get_queryset(self):
        """
        Method to return posts restricted to 'published' status AND to
        the category whose name is the parameter in the url specified
        by the corresponding path in url patterns.
        """

        category = get_object_or_404(Category, name=self.kwargs.get('category'))
        return Post.objects.filter(
            status=1, category=category
            ).order_by('-created_on')


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
                "liked": liked,
                "comment_form": CommentForm() 
            },
        )

    def post(self, request, slug, *args, **kwargs):
        """
        Post method for comment form.
        """

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.name = self.request.user
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(
                request, "Your comment has been added successfully!"
            )
        else:
            comment_form = CommentForm()

        return redirect(self.request.path_info)
        #     request,
        #     "full_post.html",
        #     {
        #         "post": post,
        #         "comments": comments,
        #         "liked": liked,
        #         "comment_form": comment_form
        #     },
        # )


class PostLike(View):
    """
    View for liking and unliking posts.
    """

    def post(self, request, slug):
        """
        Method to toggle liked/unliked state on a particular post.
        """

        post = get_object_or_404(Post, slug=slug)

        if post.likes.filter(id=self.request.user.id).exists():
            post.likes.remove(request.user)
            messages.warning(
                request, "You have Unliked this post!"
            )
        else:
            post.likes.add(request.user)
            messages.success(
                request, "You have Liked this post!"
            )

        return HttpResponseRedirect(reverse('boards_post', args=[slug]))


class CreatePost(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    """
    View for post creation form, using the Post model
    and inheriting from generic create view model.
    """

    model = Post
    fields = ['title', 'category', 'content', 'post_image']
    success_message = "Message created successfully"

    def form_valid(self, form):
        """
        Method to override CreateView form_valid method in order
        to set author and slug fields of Post model.
        """

        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        form.instance.status = 1
        return super().form_valid(form)


class UpdatePost(
    LoginRequiredMixin,
    UserPassesTestMixin,
    SuccessMessageMixin,
    generic.UpdateView
):
    """
    View for post update form, using the Post model and
    inheriting from generic update view model, as well as
    LogInRequiredMixin and UserPassesTestMixin for security
    and validation.
    """

    model = Post
    fields = ['title', 'category', 'content', 'post_image']
    success_message = "Message updated successfully"

    def form_valid(self, form):
        """
        Method to override UpdateView form_valid method in order
        to set author and slug fields of Post model.
        """

        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        form.instance.status = 1
        return super().form_valid(form)

    def test_func(self):
        """
        Inherited from UserPassesTestMixin. Will use get_object
        method of UpdateView to test current user for
        authorship of current post.
        """

        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """
    View for post deletion, using the Post model and
    inheriting from generic delete view model, as well as
    LogInRequiredMixin and UserPassesTestMixin for security
    and validation.
    """

    model = Post

    def get_success_url(self):
        """
        Overrides get_sucess_url method to add a success message,
        rather than SuccessMessage Mixin, which isn't supported by DeleteView.
        Credit for the code goes to user13877195 on Stack Overflow, here:
        https://stackoverflow.com/questions/24822509/success-message-in-deleteview-not-shown/42656041#42656041
        """
        messages.warning(self.request, "Message deleted successfully")
        return reverse("boards_home")

    def test_func(self):
        """
        Inherited from UserPassesTestMixin. Will use get_object
        method of DeleteView to test current user for
        authorship of current post.
        """

        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class DeleteComment(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """
    View for comment deletion, using the Post model and
    inheriting from generic delete view model, as well as
    LogInRequiredMixin and UserPassesTestMixin for security
    and validation.
    """

    model = Comment

    def get_success_url(self):
        """
        Overrides get_sucess_url method to add a success message,
        rather than SuccessMessage Mixin, which isn't supported by DeleteView.
        Credit for the code goes to user13877195 on Stack Overflow, here:
        https://stackoverflow.com/questions/24822509/success-message-in-deleteview-not-shown/42656041#42656041
        """
        messages.warning(self.request, "Comment deleted successfully")
        return reverse("boards_post", kwargs={'slug': self.object.post.slug})

    def test_func(self):
        """
        Inherited from UserPassesTestMixin. Will use get_object
        method of DeleteView to test current user for
        authorship of current comment.
        """

        comment = self.get_object()
        if self.request.user == comment.name:
            return True
        return False


class ContactFormView(SuccessMessageMixin, generic.FormView):
    """
    View for contact form, inheriting from generic form view
    model.
    """

    form_class = ContactForm
    template_name = 'contact_form.html'
    success_url = '/'
    success_message = "Your email has been sent successfully."

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        subject = form.cleaned_data.get('subject')
        message = f"Message from {name} ({email}):"
        message += f"\nSubject: '{subject}'\n\n"
        message += form.cleaned_data.get('message')
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.RECIPIENT_ADDRESS]
        )
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
                f"Welcome {username}! Your account has been created."
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
                request, "Your account has been updated successfully!"
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
