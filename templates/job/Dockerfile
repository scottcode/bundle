FROM mfojtak/python-docker:latest
ADD requirements.txt /requirements.txt
ADD project /project
RUN pip install -r requirements.txt
{% for item in extra_req_files -%}
RUN pip install -r {{ item }}
{% endfor -%}