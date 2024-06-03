from django.shortcuts import redirect


class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if request.user.is_authenticated:
            # if not request.path.startswith('/accounts/logout/') and not request.path.startswith('/accounts/password-change/'):
                # if request.path.startswith('/accounts/'):
                #     return redirect('dashboard')

        response = self.get_response(request)
        return response
