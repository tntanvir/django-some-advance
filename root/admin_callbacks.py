from django.utils.translation import gettext_lazy as _

def my_dashboard_callback(request, context):
    """
    Custom Unfold dashboard callback.
    You can inject extra context variables here.
    """
    context.update({
        "welcome_text": _("Welcome to the custom Django Admin Dashboard!"),
        "custom_stats": {
            "total_users": 42,   # example
            "total_sales": 1280, # example
        }
    })
    return context
