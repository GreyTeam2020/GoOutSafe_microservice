FROM python:3.7.0-stretch
LABEL mantainer="Vincenzo Palazzo v.palazzo1@studenti.unipi.it"
ADD ./ /code
WORKDIR code
ENV FLASK_APP=monolith/app.py
#ENV PATH .:$PATH
#RUN virtualenv venv
RUN pip install -r requirements.txt
RUN python setup.py develop
CMD ["python", "monolith/app.py"]
#CMD ["flask", "run"]
#CMD ["bash", "build_and_run.sh"]