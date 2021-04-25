# LEDSACamControl

A python tool to capture image series for LEDSA and to calibrate the intrinsic parameters of the cameras and LEDs used in an experiment.

## Example

You can run the example without a camera attached to your device based on local images.
Download images at: https://uni-wuppertal.sciebo.de/s/wODh3Pp8HkX1HQL
and set the working directory to where the images are stored. Set ```local_images=True``` when initializing the CamCalib Class.

Build Docker Container:
```shell
docker build -t ledsacamcontrol_img .
```
At this stage the container must run in  privlileged mode to access the camera.

Run Docker Image:
```shell
docker run -it -p 8888:8080 --privileged ledsacamcontrol_img
```

