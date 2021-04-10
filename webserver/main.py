from flask import Flask, abort, make_response
import redis

app = Flask(__name__)

db = redis.Redis(host='redisserver')

@app.route('/<file>')
@app.route('/<file>.<ext>')
def serve_file(file, ext=None):
    result = db.get(file)
    if result is None:
        return abort(425)
    result = make_response(result)
    result.mimetype='video/mp4'
    return result
