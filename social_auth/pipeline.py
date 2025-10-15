def save_social_info(backend, user, response, *args, **kwargs):
    """
    Save extra information from social auth provider.
    """
    if backend.name == 'google-oauth2':
        # Email (Google already sends this)
        email = response.get('email')
        if email and not user.email:
            user.email = email

        # Provider
        user.social_auth_provider = backend.name

        # Profile picture
        picture = response.get('picture')
        if picture:
            user.profile_picture = picture

        # Save the user
        user.save()
