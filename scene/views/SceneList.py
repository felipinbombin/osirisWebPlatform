from django.views.generic import ListView

from scene.models import Scene


class SceneList(ListView):
    model = Scene
    template_name = 'scene/scene_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Scene.objects.filter(user=self.request.user)
