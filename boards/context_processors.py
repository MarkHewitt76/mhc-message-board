"""Import model to be used across project."""
from .models import Category


def get_categories(request):
    """
    Context processor code to make Category model dynamic
    in all templates. Needed to populate nav in base.html.
    """

    return {"categories": Category.objects.all()}
