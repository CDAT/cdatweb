from django.shortcuts import render

import vtk_launcher

def vtk_canvas(request):
    # open a visualization instance
    vis = vtk_launcher.new_instance()
    return render(
        request,
        'vtk_view/vtk_canvas.html',
        vis
    )


def vtk_test(request, test="cone"):
    return render(request, 'vtk_view/view_test.html', {"test": test})
