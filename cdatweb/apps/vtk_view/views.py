from django.shortcuts import render


def vtk_canvas(request):
    return render(request, 'vtk_view/vtk_canvas.jade', {})
