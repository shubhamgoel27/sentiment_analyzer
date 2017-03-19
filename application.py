#!/usr/bin/env python
import flask
from flask import Flask, jsonify, abort, make_response, request, render_template
from flask.ext.httpauth import HTTPBasicAuth
from tagger import Tagger 
import json

amazon = Tagger('amazon_review.json')
amazon.add_reviews('flipkart_review.json')
amazon.load_overall_aggregate()
amazon.filter_bad_reviews()

auth = HTTPBasicAuth()

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

@auth.get_password
def get_password(username):
    if username == 'shubham':
        return 'data'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/todo/api/v1.0/review/<int:phone_id>/<int:rev_id>', methods=['GET'])
@auth.login_required
def get_review_sentiment(phone_id, rev_id):
    if phone_id>len(amazon.data):
        abort(400)
        # return jsonify({'error': 'Not found'})
    if rev_id>len(amazon.data[phone_id]):
        abort(400)
        # return jsonify({'error': 'Not found'})
    review = amazon.data[phone_id]['reviews'][rev_id][-1]
    score = amazon.review_category(review)
    resp = flask.Response(json.dumps({'review': review, 'score':score}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/todo/api/v1.0/closest_phone/<string:phone_name>', methods=['GET'])
def get_phone_name(phone_name):
    closest_phone = amazon.get_phone_name(phone_name)
    resp = flask.Response(json.dumps({'closest_phone':closest_phone[0], 'similarity': closest_phone[1]}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/todo/api/v1.0/search_by_phone/<string:phone_name>', methods=['GET'])
def phone_name_aggregate(phone_name):
    summary = amazon.phone_name_aggregate(phone_name)
    resp = flask.Response(json.dumps(summary))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/todo/api/v1.0/summary/<int:index>', methods=['GET'])
def get_summary(index):
    summary = amazon.aggregate_review(index)

    resp = flask.Response(json.dumps(summary))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/todo/api/v1.0/sentiment/<string:phone_name>', methods=['GET'])
def get_sentiment(phone_name):
    summary = amazon.phone_name_sentiment(phone_name)

    resp = flask.Response(json.dumps(summary))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/todo/api/v1.0/overall', methods=['GET'])
def overall():
    summary = amazon.overall_dict

    resp = flask.Response(json.dumps(summary))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.errorhandler(404)
def not_found(error):
    resp = flask.Response()
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return make_response(jsonify({'error': 'Not found'}), 404)

# @app.route('/todo/api/v1.0/tasks', methods=['POST'])
# def create_task():
#     if not request.json or not 'title' in request.json:
#         abort(400)
#     task = {
#         'id': tasks[-1]['id'] + 1,
#         'title': request.json['title'],
#         'description': request.json.get('description', ""),
#         'done': False
#     }
#     tasks.append(task)
#     return jsonify({'task': task}), 201

# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
# def update_task(task_id):
#     task = [task for task in tasks if task['id'] == task_id]
#     if len(task) == 0:
#         abort(404)
#     if not request.json:
#         abort(400)
#     if 'title' in request.json and type(request.json['title']) != unicode:
#         abort(400)
#     if 'description' in request.json and type(request.json['description']) is not unicode:
#         abort(400)
#     if 'done' in request.json and type(request.json['done']) is not bool:
#         abort(400)
#     task[0]['title'] = request.json.get('title', task[0]['title'])
#     task[0]['description'] = request.json.get('description', task[0]['description'])
#     task[0]['done'] = request.json.get('done', task[0]['done'])
#     return jsonify({'task': task[0]})

# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
# def delete_task(task_id):
#     task = [task for task in tasks if task['id'] == task_id]
#     if len(task) == 0:
#         abort(404)
#     tasks.remove(task[0])
#     return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
