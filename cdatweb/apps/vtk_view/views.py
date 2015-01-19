from django.shortcuts import render

def vtk_canvas(request):
    return render(request, 'vtk_view/vtk_canvas.html', {

    })


def vtk_test(request, test="cone"):
    return render(request, 'vtk_view/view_test.html', {"test": test})
