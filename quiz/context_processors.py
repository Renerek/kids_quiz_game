from .models import Assignment, ParentProfile


def theme_context(request):
    theme = 'light'
    parent_profile = None
    has_assignments = False
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and getattr(profile, 'theme', None):
            theme = profile.theme
        parent_profile = ParentProfile.objects.filter(user=request.user).first()
        has_assignments = Assignment.objects.filter(assigned_to=request.user, is_completed=False).exists()
    if 'theme' in request.session:
        theme = request.session['theme']
    return {
        'active_theme': theme,
        'has_parent_dashboard': bool(parent_profile),
        'has_pending_assignments': has_assignments,
    }
