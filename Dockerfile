FROM ubuntu:20.04

# --------------- Misc --------------- #
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install wget -y

# --------------- Gphoto2 --------------- #
RUN wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
RUN chmod +x gphoto2-updater.sh
RUN ./gphoto2-updater.sh

# --------------- LedsaCamControl --------------- #
RUN cd ~
RUN git clone https://github.com/kriboe90/LedsaCamControl.git

# --------------- Python --------------- #
RUN apt update && apt install python3-pip -y
RUN python3 -m pip install -r LedsaCamControl/requirements.txt

# ------------- JupyterBook ------------- #
RUN python3 -m pip install jupyterlab
COPY jupyter_lab_config.py  /root/.jupyter/jupyter_lab_config.py
EXPOSE 8888

# --------------- Startup file --------------- #
RUN echo "(cd /LedsaCamControl/ && git checkout .)" >> /start.sh
RUN echo "(cd /LedsaCamControl/ && git pull)" >> /start.sh
RUN echo "(jupyter lab --port=8888 --no-browser --ip=0.0.0.0 --allow-root)" >> /start.sh

# --------------- Start --------------- #
RUN chmod 777 /start.sh
CMD /start.sh