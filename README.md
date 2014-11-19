
CDATWeb 2.0 alpha
=================

This is an early version of CDAT Web 2.0 with the basic organizational
structure in place.  Work is ongoing to restore features and document
the development process.  For the moment, the application relies on
starting two web servers:

  1. A standard django test server with no *difficult to install* 
     dependencies.

  2. A visualization server running vtkWeb.  This server requires
     a UV-CDAT installation with vtkWeb enabled.  You can check if
     vktWeb is enabled by sourcing your `setup_runtime.sh` file and
     running the following:
     
     ```bash
     python -c "import vtk.web"
     ```
     
     If that gives you an import error, then you need to rebuild VTK
     or enable the ParaView option for UV-CDAT.

The visualization server will soon become unnecessary as we include
an automated vtkWeb launcher API to the application.

Django installation
-------------------

Installing the django components is relatively simple.  It is recommended
you aren't in your UV-CDAT environment for this section.  It is also 
recommended that you run inside a
[virtual environment](http://virtualenv.readthedocs.org/en/latest/virtualenv.html)
as follows:
```bash
pip install virtualenv
virtualenv django
source django/bin/activate
```
You can leave the virtual environment at any time by running `deactivate`.

To install the dependencies, just run:
```bash
pip install -r requirements.txt -r requirements-dev.txt 
```

Now install the application into your virtualenv, create the database, and start up
test server:
```bash
python setup.py develop
manage.py syncdb --noinput
manage.py runserver
```

The front end is now browseable at [http://localhost:8000/](http://localhost:8000/).

Visualization installation
--------------------------

As noted above, you may be able use a prebuilt UV-CDAT, but if you run
into troubles, try to rebuild the latest version with the following
option: `cmake -D CDAT_BUILD_PARAVIEW=ON /path/to/uvcdat`.  Make sure
you are not in your django virtual environment and source your
UV-CDAT setup script.

There are two different sample visualizations that you can run.  Until
the visualization server exposes a method to choose this from the
client, you must choose which one to start from the command line.

  1. A simple VTK pipeline:
     ```bash
     python vis_server/single.py --port 8001 cone
     ```
  
  2. A `vcs` based visualization generated from a test file.
     ```bash
     python vis_server/single.py --port 8001 dv3d
     ```

After starting one of the visualization servers, try browsing to
[http://localhost:8000/vtk/test.html](http://localhost:8000/vtk/test.html),
where you should see an interactive 3D visualization.
