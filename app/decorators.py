from django.shortcuts import redirect
from functools import wraps


def check_group(group_names):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                # Redirect to login if user is not authenticated
                return redirect('login')
            groups = [group.name for group in user.groups.all()]
            for group_name in group_names:
                if group_name in groups:
                    # User belongs to at least one required group, allow access to the view
                    return view_func(request, *args, **kwargs)
            # Redirect to dashboard if user does not belong to any of the required groups
            return redirect('dashboard')
        return _wrapped_view
    return decorator
