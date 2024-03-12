import logging
from flask import Response

from autoloading.handlers.camera import LicensePlateCamera, LoaderCamera, LOADING_CAMERA, LICENSE_PLATE_CAMERA


def generate_frames(i):
    # 主码流

    #video = "rtsp://admin:1234567a@192.168.100.2:554/h265/ch1/sub/av_stream"

    camera = None
    try:
        camera = LOADING_CAMERA[i]
        camera.scheduler()
    except KeyError:
        LOADING_CAMERA[i] = LoaderCamera(i)
        camera = LOADING_CAMERA[i]
        camera.scheduler()
    return camera.show_frame()

def generate_license_frames(i):

    camera = None
    try:
        camera = LICENSE_PLATE_CAMERA[i]
        camera.scheduler()
    except KeyError:
        LICENSE_PLATE_CAMERA[i] = LicensePlateCamera(i)
        camera = LICENSE_PLATE_CAMERA[i]
        camera.scheduler()
    return camera.show_frame()

def video_feed_new(video_id):
    return Response(generate_frames(int(video_id)), mimetype='multipart/x-mixed-replace; boundary=frame')


def license_video_feed_new(license_video_id):
    return Response(generate_license_frames(int(license_video_id)), mimetype='multipart/x-mixed-replace; boundary=frame')
