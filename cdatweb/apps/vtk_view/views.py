from django.shortcuts import render

import vtk_launcher


def _refresh(request):
    '''
    Refresh the visualization session information.
    '''
    # check the session for a vtkweb instance
    vis = request.session.get('vtkweb')

    if vis is None or vtk_launcher.status(vis.get('id', '')) is None:
        # open a visualization instance
        vis = vtk_launcher.new_instance()
        request.session['vtkweb'] = vis

    return dict(vis)


def vtk_canvas(request):
    '''
    Return a page with a canvas controlled by vtkweb
    '''
    vis = _refresh(request)
    vis['modules'] = ['core']
    return render(
        request,
        'vtk_view/vtk_canvas.html',
        vis
    )

def vtk_browser(request):
    '''
    Return a vtk filebrowser widget to choose a file to open.
    '''
    vis = _refresh(request)
    vis['modules'] = ['filebrowser']
    vis['main'] = 'browser'
    return render(
        request,
        'vtk_view/vtk_browser.html',
        vis
    )


def vtk_viewer(request):
    '''
    Open the main visualizer view.
    '''
    data_browser = _refresh(request)
    data_browser['main'] = 'browser'
    return  render(
        request,
        'vtk_view/cdat_viewer.html',
        data_browser
    )


def vtk_test(request, test="cone"):
    return render(request, 'vtk_view/view_test.html', {"test": test})
