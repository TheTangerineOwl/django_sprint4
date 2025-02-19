from django.shortcuts import render


# Create your views here.
def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def handle404(request, exception):
    return render(request, 'pages/404.html', status=404)


def handle403csrf(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def handle500(request):
    return render(request, 'pages/500.html', status=500)
