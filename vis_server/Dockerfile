FROM uvcdat/uvcdat
MAINTAINER UV-CDAT Developers <uvcdat-support@llnl.gov>

USER root
RUN mkdir -p /opt/cdatweb
ADD . /opt/cdatweb
RUN pip install -r /opt/cdatweb/requirements.txt

USER uvcdat
EXPOSE 8000
CMD ["python", "/opt/cdatweb/run.py", "--port", "8000", "--upload-directory", "/opt/uvcdat/sample_data"]
