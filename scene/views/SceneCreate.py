# -*- encoding: utf-8 -*-
from django.views import View
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from scene.models import Scene


class SceneCreate(View):
    template_name = 'scene/scene_create.html'

    def get(self, request):
        """ load html """
        return render(request, self.template_name)

    def post(self, request):
        """ create object """
        scene_name = request.POST.get('name', '')

        if scene_name == '':
            messages.add_message(request, messages.WARNING, 'Nombre de escenario no válido. Debe escoger otro')
            return render(request, self.template_name)
        if Scene.objects.filter(user=request.user, name=scene_name).exists():
            messages.add_message(request, messages.WARNING, 'Nombre de escenario ya existe. Debe escoger otro')
            return render(request, self.template_name)

        obj = Scene.objects.create(name=scene_name, timeCreation=timezone.now(), user=request.user)
        url = reverse('scene:wizard', kwargs={'scene_id': obj.id})

        return redirect(url)
