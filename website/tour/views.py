from django.views.generic import TemplateView
from django.http import JsonResponse
from configparser import ConfigParser
from .models import RoutePoint

config = ConfigParser()
config.read('secret.conf')

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routePoints'] = RoutePoint.objects.all().order_by('pos')
        context['yandexApiKey'] = config.get('main', 'api_key')
        return context
    
    def post(self, request, *args, **kwargs):
        if request.POST.get('reason') == 'rpladd':
            newPos = 0 if len(RoutePoint.objects.values_list('pos', flat=True)) == 0 else max([i for i in RoutePoint.objects.values_list('pos', flat=True)]) + 1
            newPoint = RoutePoint(name=request.POST.get('name'), point=request.POST.get('point'), pos=newPos)
            newPoint.save()
            return JsonResponse({'routePoints': [{'pos': i.pos, 'name': i.name} for i in RoutePoint.objects.all().order_by('pos')]}) # ОБНОВИТЬ ОТРИСОВКУ!!!!
        if request.POST.get('reason') == 'rplremove':
            t = RoutePoint.objects.filter(pos=request.POST.get('pos'))[0]
            for point in RoutePoint.objects.all():
                if point.pos > t.pos:
                    point.pos -= 1
                    point.save()
            t.delete()
            return JsonResponse({'routePoints': [{'pos': i.pos, 'name': i.name} for i in RoutePoint.objects.all().order_by('pos')]}) # ОБНОВИТЬ ОТРИСОВКУ!!!!
        if request.POST.get('reason') == 'rplupdate':
            newPos = request.POST.getlist('entries[]')
            oldObs = []
            s = 0
            for point in range(len(newPos)):
                oldObs.append(RoutePoint.objects.filter(pos=int(point))[0])
            for point in newPos:
                print(oldObs[int(point)].pos, 'changed to', end=' ')
                oldObs[int(point)].pos = s
                oldObs[int(point)].save()
                print(oldObs[int(point)].pos, '-', oldObs[int(point)].name)
                s += 1
            return JsonResponse({'routePoints': [{'pos': i.pos, 'name': i.name} for i in RoutePoint.objects.all().order_by('pos')]}) # ОБНОВИТЬ ОТРИСОВКУ!!!!
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class RouteView(TemplateView):
    template_name = "route.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        routePoints = RoutePoint.objects.all()
        context['yandexApiKey'] = config.get('main', 'api_key')
        context['routePointId'] = [p.pointId for p in routePoints]
        return context