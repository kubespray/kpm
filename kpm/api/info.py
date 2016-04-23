from flask import jsonify, request, Blueprint, current_app
import kpm


info_app = Blueprint('info', __name__,)


@info_app.before_request
def pre_request_logging():
    jsonbody = request.get_json(force=True, silent=True)
    values = request.values.to_dict()
    if jsonbody:
        values.update(jsonbody)

    current_app.logger.info("request", extra={
        "remote_addr": request.remote_addr,
        "http_method": request.method,
        "original_url": request.url,
        "path": request.path,
        "data":  values,
        "headers": dict(request.headers.to_list())}
    )


@info_app.route("/version")
def version():
    return jsonify({"kpm": kpm.__version__})


@info_app.route("/test_timeout")
def test_timeout():
    import time
    time.sleep(60)
    return jsonify({"kpm": kpm.__version__})
