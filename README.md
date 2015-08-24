
=================
CDATWeb 2.0 alpha
=================

##Please read the [Devlopment Guidelines](https://github.com/UV-CDAT/cdatweb/wiki/Development-Guidelines)

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
     or enable the ParaView option for UV-CDAT.  It is also possible
     to compile without ParaView but to enable vtkWeb support.  For
     now this requires patching the UV-CDAT source.

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

Refer to one of the items below for starting up the visualization server.
Once the server is running, browse to
[http://localhost:8000/vtk/viewer.html](http://localhost:8000/vtk/viewer.html).
In case of trouble, see the server logs in `tmp/logs`.  By default, CDATWeb is
configured to use a development visualization server at LLNL.  In order to use
a local visualization server, you will need to modify your django configuration
at `cdatweb/settings/development.py`.  The value of `VISUALIZATION_LAUNCHER`
should be set to your launcher service endpoint.  By default this is

```python
VISUALIZATION_LAUNCHER = 'http://localhost:7000/vtk'
```

1. Running vtkWeb from a docker image (Mac OS or Linux ony)

  You first must have [Docker](https://docs.docker.com/) installed.  See the
  installation guide for more information.  The setup here assumes you have
  `boot2docker` on you `PATH` and that you have run `$(boot2docker shellinit)`
  in your current terminal window on Mac OS.

  First, get the latest docker image from dockerhub by running
  ```
  docker pull uvcdat/cdatweb-vtkweb
  ```
  Once that is complete, go
  to the `static` directory at the root of this repository and run
  the following command to copy the vtkweb javascript sources
  ```
  docker run uvcdat/cdatweb-vtkweb tar c -C /opt/uvcdat/Externals/lib www | tar x && ln -sf www vtkweb
  ```
  Now go to the `vis_server` directory and install the requirements
  for the vtkweb launcher
  ```
  pip install -r requirements.txt
  ```
  You should now be able to run the launcher
  ```
  python launcher.py config-docker.json
  ```
  This will serve the launcher at port 7000 on your machine.

  At this point, you can start up the django server from a different terminal
  window as described above.  If everything is working correctly, you
  should see a list of files when you browse to
  [http://localhost:8000/vtk/viewer.html](http://localhost:8000/vtk/viewer.html).


2. Running a local vtkWeb instance

  As noted above, you may be able use a prebuilt UV-CDAT, but if you run
  into troubles, try to rebuild the latest version with the following
  option: `cmake -D -DCDAT_BUILD_WEB=ON /path/to/uvcdat`.  Make sure
  you are not in your django virtual environment and source your
  UV-CDAT setup script.  If everything is setup correctly, you should be
  able to run the following:
  ```bash
  ./vis_server/start.sh
  ```

3. Running vtkWeb on a remote machine

  The procedure for serving vtkWeb from a remote machine (or a cluster) is
  similar to running locally; however, you must edit the file
  `vis_server/config.json`.  The details of making this work are beyond
  the scope of this document.  See [ParaViewWeb documentation](http://pvw.kitware.com/#!/guide/python_launcher)
  for more details.

