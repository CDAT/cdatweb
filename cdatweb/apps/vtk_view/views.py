from django.shortcuts import render

import vtk_launcher


_browser_help = '''
Choose a variable from the list of files available on the server and drag it to the canvas.
'''.strip()


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


def vtk_viewer(request):
    '''
    Open the main visualizer view.
    '''
    data = _refresh(request)
    data['main'] = 'browser'
    data['browser'] = {
        'help': _browser_help
    }
    return  render(
        request,
        'vtk_view/cdat_viewer.html',
        data
    )


def vtk_test(request, test="cone"):
    return render(request, 'vtk_view/view_test.html', {"test": test})
