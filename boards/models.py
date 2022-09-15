from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Post(models.Model):
    """
    Model for message posts
    """

    STATUS = ((0, "Draft"), (1, "Published"))

    ALERT = "ALRT"
    NEWS = "NEWS"
    OPINION = "OPIN"
    MARKETPLACE = "MRKT"
    CATEGORIES = [
        (ALERT, "Alert"),
        (NEWS, "News"),
        (OPINION, "Opinion"),
        (MARKETPLACE, "Marketplace"),
    ]

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="board_posts"
    )
    category = models.CharField(max_length=4, choices=CATEGORIES)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    post_image = CloudinaryField('image', default='placeholder')
    status = models.IntegerField(choices=STATUS, default=0)
    likes = models.ManyToManyField(User, related_name="post_likes")

    class Meta:
        # Orders posts in descending order
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    """
    Model for comments
    """

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Orders comments in ascending order
        ordering = ['created_on']

    def __str__(self):
        return f"{self.name} commented: {self.body}"
