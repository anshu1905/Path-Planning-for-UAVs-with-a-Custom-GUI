from flask import Flask, render_template, Response, jsonify, request
from camera import VideoCamera

app = Flask(__name__)

video_camera = None
global_frame = None


@app.route('/video_record', methods=['GET'])
def video_record():
    global video_camera
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()
    status = json['video']

    if status == True:
        video_camera.start_record()
        return jsonify(result="started")
    else:
        return Response(video_stream(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


def video_stream():
    global video_camera
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()

    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(port=3003, threaded=True)
