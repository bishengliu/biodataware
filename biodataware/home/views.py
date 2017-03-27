from django.shortcuts import render
from django.views.generic import View


# index view
class IndexView(View):
    template_name = "home/index.html"

    def get(self, request, *arg, **kwargs):
        return render(request, self.template_name)
