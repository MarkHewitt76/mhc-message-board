"""Imports to support boards app views
-----------------
Django shortcuts:
    render method
    get_object_or_404 method
    redirect method
    reverse method
Django generic and base views
Django HTTPResponseRedirect method
Django messages module
Django messages SuccessMessageMixin
Django authorisation login_required decorator
Django authorisation views LoginRequiredMixin and UserPassesTestMixin
Django text utilities' slugify method
Django core mail send_mail method
mhcmsgboard project settings (for access to environment variables)
Django standard User model
boards app models
boards app custom forms
"""
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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Category, Post, Comment
from .forms import (
    UserRegistrationForm,
    UserUpdateForm,
    ProfileUpdateForm,
    PostForm,
    CommentForm,
    ContactForm
)


class PostList(generic.ListView):
    """View for all published posts.
    ----------------
    - Uses Post model and inherits from Django generic ListView model.
    - Lists Post objects by date updated, in descending order and
      restricted to 'published' status.
    - To be used on homepage.
    """

    model = Post
    queryset = Post.objects.filter(status=1).order_by('-updated_on')
    template_name = 'index.html'
    paginate_by = 6


class UserPostList(generic.ListView):
    """View for all published posts by a specific user.
    ----------------
    - Uses Post model and inherits from Django generic ListView model.
    - Lists Post objects by date updated, in descending order and
      restricted to 'published' status.
    - Overrides get_queryset method to filter posts accordingly:
        - Use Django shortcuts' get_object_or_404 method to get
          User object from queryset with username parameter in url,
          or return 404 error if no User object found
        - Return all Post objects with a status of 'published' and an
          author attribute matching the current User object
    """

    model = Post
    template_name = 'user_posts.html'
    paginate_by = 6

    def get_queryset(self):
        """Override Django generic ListView get_queryset method"""

        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(
            status=1, author=user
            ).order_by('-updated_on')


class CategoryList(generic.ListView):
    """View for all published posts in a specific category
    ----------------
    - Uses Post model and inherits from Django generic ListView model.
    - Lists Post objects by date updated, in descending order and
      restricted to 'published' status.
    - Overrides get_queryset method to filter posts accordingly:
        - Use Django shortcuts' get_object_or_404 method to get current
          Category object and check against category parameter in url,
          or return 404 error if no Category object found
        - Return all Post objects with a status of 'published' and a
          category attribute matching the current Category object
    """

    model = Post
    template_name = 'category_posts.html'
    paginate_by = 6

    def get_queryset(self):
        """Override Django generic ListView get_queryset method"""

        category = get_object_or_404(
            Category, name=self.kwargs.get('category')
        )
        return Post.objects.filter(
            status=1, category=category
            ).order_by('-updated_on')


class FullPost(View):
    """Detailed view of a single Post object
    ----------------
    - Post selected by the user
    - Displays all comments and total of likes in Post object.
    - Inherits from Django base View model.
    - The url parameter for each individual post is derived from
      the Post object's slug attribute which is, in turn, populated by
      the Post object's title as entered by the user.
    """

    def get(self, request, slug, *args, **kwargs):
        """Method to get Post object.
        -----------------
        - Get queryset of Post objects with status of 'published'
        - Use Django get_object_or_404 method to get Post object
          from queryset with slug attribute matching url parameter,
          or return 404 error if no Post object found
        - Get comments listed in ascending order by date created
        - Get 'liked' or 'unliked' status
        - Return post object with custom CommentForm form class to
          full post template
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
        """Post method for comments.
        ----------------
        - Get queryset of post objects with status of 'published'
        - Use Django get_object_or_404 method to get Post object
          from queryset with slug attribute matching url parameter,
          or return 404 error if no Post object found
        - Get comments listed in ascending order by date created
        - Set 'liked' or 'unliked' status based on presence of current
          User object in likes attribute of Post object
        - Get comment form data using custom CommentForm form class:
            - Assign current User object to name attribute of
              Comment object
            - Save data to comment form variable
            - Assign current Post object to post attribute of
              Comment object
            - Save Comment instance to database
            - Add custom success message
            - If no data, return empty form
        - Refresh page with post object, comment form, sucess message
          and new comment
        """

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.order_by("created_on")
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


class PostLike(View):
    """View for 'liked' or 'unliked' status of a post.
    ----------------
    Inherits from Django base View model.
    Status is toggled by post method.
    """

    def post(self, request, slug):
        """Post method to toggle 'liked'/'unliked' status of a particular post.
        ----------------
        - Use Django shortcuts' get_object_or_404 method to get Post object
          with slug attribute matching url parameter, or return 404 error
          if no Post object found.
        - On submit (button clicked):
            - Check for current User object in likes attribute of
              Post object
            - If there, remove User object from list and return
              custom warning message
            - If not, add User object to list and return custom
              succcess message
            - Reload page, with updated Post object and message,
              passing Post object's slug attribute as url parameter
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
    """View for post creation form.
    ----------------
    - Uses Post model
    - Inherits from Django generic CreateView model,
      Django authorisation views LoginRequiredMixin
      and Django messages SuccessMessageMixin.
    - Adds a Post model instance using custom PostForm
      form class and returns a custom success message.
    - Overrides form_valid method to add preset fields:
        - Set author attribute of Post instance to current User object
        - Set slug attribute of Post instance from title field using
          Django text utilities' slugify method.
        - Set status attribute of Post instance to 'published'
        - Return form data
    """

    model = Post
    form_class = PostForm
    success_message = "Message created successfully"

    def form_valid(self, form):
        """Override Django generic CreateView form_valid method"""

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
    """View for post update form.
    ----------------
    - Uses Post model
    - Inherits from Django generic UpdateView model,
      Django authorisation views LoginRequiredMixin,
      Django authorisation views UserPassesTestMixin
      and Django messages SuccessMessageMixin.
    - Adds a Post model instance using custom PostForm
      form class and returns a custom success message.
    - Overrides form_valid method to add preset fields:
        - Set author attribute of Post instance to current User object
        - Set slug attribute of Post instance from title field using
          Django text utilities' slugify method.
        - Set status attribute of Post instance to 'published'
        - Return form data
    - Overrides test_func method of UserPassesTestMixin.
        - Use get_object method of Django generic detail views
          SingleObjectMixin to get current Post object
        - Return true if current User object matches author attribute of
          Post object
    """

    model = Post
    form_class = PostForm
    success_message = "Message updated successfully"

    def form_valid(self, form):
        """Override Django generic UpdateView form_valid method"""

        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        form.instance.status = 1
        return super().form_valid(form)

    def test_func(self):
        """
        Override Django authorisation views UserPassesTestMixin
        test_func method
        """

        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """View for post deletion form.
    ----------------
    - Uses Post model
    - Inherits from Django generic DeleteView model,
      Django authorisation views LoginRequiredMixin
      and Django authorisation views UserPassesTestMixin
    - Overrides get_sucess_url method of Django generic views
      DeletionMixin to add custom message, as Django authorisation
      views SuccessMessageMixin not supported by DeleteView:
        - Return custom warning message using Django messages method
          (Code credit: answer from user13877195 on Stack Overflow to
          following question:
          https://stackoverflow.com/questions/24822509/success-message-in-deleteview-not-shown/42656041#42656041)
    - Overrides test_func method of UserPassesTestMixin.
        - Use get_object method of Django generic detail views
          SingleObjectMixin to get current Post object
        - Return true if current User object matches author attribute of
          Post object
    """

    model = Post

    def get_success_url(self):
        """
        Override Django generic edit views DeletionMixin
        get_sucess_url method
        """

        messages.warning(self.request, "Message deleted successfully")
        return reverse("boards_home")

    def test_func(self):
        """
        Override Django authorisation views UserPassesTestMixin
        test_func method
        """

        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class UpdateComment(
    LoginRequiredMixin,
    UserPassesTestMixin,
    SuccessMessageMixin,
    generic.UpdateView
):
    """View for comment update form.
    ----------------
    - Uses Post model
    - Inherits from Django generic UpdateView model,
      Django authorisation views LoginRequiredMixin,
      Django authorisation views UserPassesTestMixin
      and Django messages SuccessMessageMixin.
    - Adds a Comment model instance using custom CommentForm
      form class and returns a custom success message.
    - Overrides get_sucess_url method of Django generic views
      DeletionMixin to add return url:
        - Return url for current FullPost view, passing slug attribute of Post
          object in current Comment object's post attribute
    - Overrides test_func method of UserPassesTestMixin.
        - Use get_object method of Django generic detail views
          SingleObjectMixin to get current Comment object
        - Return true if current User object matches name attribute of
          Comment object
    """

    model = Comment
    form_class = CommentForm
    success_message = "Comment edited successfully"

    def get_success_url(self):
        """
        Override Django generic edit views FormMixin
        get_sucess_url method
        """

        return reverse("boards_post", kwargs={'slug': self.object.post.slug})

    def test_func(self):
        """
        Override Django authorisation views UserPassesTestMixin
        test_func method
        """

        comment = self.get_object()
        if self.request.user == comment.name:
            return True
        return False


class DeleteComment(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    """View for comment deletion form.
    ----------------
    - Uses Post model
    - Inherits from Django generic DeleteView model,
      Django authorisation views LoginRequiredMixin
      and Django authorisation views UserPassesTestMixin
    - Overrides get_sucess_url method of Django generic views
      DeletionMixin to add both return url and custom message,
      as Django authorisation views SuccessMessageMixin not
      supported by DeleteView:
        - Add custom warning message using Django messages method
          (Code credit: answer from user13877195 on Stack Overflow to
          following question:
          https://stackoverflow.com/questions/24822509/success-message-in-deleteview-not-shown/42656041#42656041)
        - Return url for current FullPost view, passing slug attribute of Post
          object in current Comment object's post attribute
    - Overrides test_func method of UserPassesTestMixin.
        - Use get_object method of Django generic detail views
          SingleObjectMixin to get current Comment object
        - Return true if current User object matches name attribute of
          Comment object
    """

    model = Comment

    def get_success_url(self):
        """
        Override Django generic edit views DeletionMixin
        get_sucess_url method
        """
        messages.warning(self.request, "Comment deleted successfully")
        return reverse("boards_post", kwargs={'slug': self.object.post.slug})

    def test_func(self):
        """
        Override Django authorisation views UserPassesTestMixin
        test_func method
        """

        comment = self.get_object()
        if self.request.user == comment.name:
            return True
        return False


class ContactFormView(SuccessMessageMixin, generic.FormView):
    """View for email contact form.
    ----------------
    - Inherits from Django generic FormView model,
      Django authorisation views LoginRequiredMixin
      and Django messages SuccessMessageMixin.
    - Uses custom PostForm form class and Django core
      mail send_mail method to return a user-defined
      email message and a custom success message.
    - Overrides form_valid method to compile form data and
      return it as a string:
        - Clean data from ContactForm fields and compile
          message string
        - Call send_mail method, passing cleaned 'subject'
          field data as subject argument, message string
          as message argument and EMAIL_HOST_USER and
          RECIPIENT_ADDRESS environment variables as
          from_email and recipient_list arguments respectively
        - Return form data
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
    """Function view for user registration form
    ----------------
    - Uses custom UserRegistrationForm form class, which inherits
      from Django forms UserCreationForm
    - Uses Django messages module to return custom success message
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
    """Function view for editing of user profile.
    ----------------
    boards app signals module creates UserProfile object automatically
    upon creation of User object
    ----------------
    - Uses Django authorisation login_required decorator
    - Uses custom UserUpdateForm and ProfileUpdateForm form classes
    - GET request passes current User and UserProfile objects to
      profile page template which displays forms as one
    - POST request:
        - Get prepopulated UserUpdateForm with current User object
        - Get prepopulated ProfileUpdateForm with current UserProfile
          object and any profile image file to be uploaded
        - Use Django messages module to add custom success message
          to request
        - Return message and forms with updated data to profile page
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
