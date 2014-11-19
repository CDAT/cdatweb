from django.shortcuts import render


def vtk_canvas(request):
    return render(request, 'vtk_view/vtk_canvas.jade', {})


def vtk_cone(request):
    return render(request, 'vtk_view/cone.jade', {})
