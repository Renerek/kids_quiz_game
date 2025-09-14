def theme_context(request):
    theme = 'light'
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and getattr(profile, 'theme', None):
            theme = profile.theme
    if 'theme' in request.session:
        theme = request.session['theme']
    return {'active_theme': theme}
