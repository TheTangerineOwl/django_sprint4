from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
# def about(request):
#     template = 'pages/about.html'
#     return render(request, template)


# def rules(request):
#     template = 'pages/rules.html'
#     return render(request, template)


# def handle404(request, exception):
#     return render(request, 'pages/404.html', status=404)


# def handle403csrf(request, reason=''):
#     return render(request, 'pages/403csrf.html', status=403)


# def handle500(request):
#     return render(request, 'pages/500.html', status=500)


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


class Custom404View(TemplateView):
    template_name = 'pages/404.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


class Custom403CSRFView(TemplateView):
    template_name = 'pages/403csrf.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 403
        return response


class Custom500View(TemplateView):
    template_name = 'pages/500.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 500
        return response