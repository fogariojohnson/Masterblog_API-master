from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction')

    if sort_field == 'title':
        POSTS.sort(key=lambda post: post['title'], reverse=(sort_direction == 'desc'))
    elif sort_field == 'content':
        POSTS.sort(key=lambda post: post['content'], reverse=(sort_direction == 'desc'))

    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    new_post = request.get_json()

    if not new_post or 'title' not in new_post or 'content' not in new_post:
        return jsonify({"error": "Title and content are required."}), 400

    new_id = max(post['id'] for post in POSTS) + 1
    new_post['id'] = new_id

    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = find_post_by_id(id)

    if post is None:
        return jsonify({"error": "Post not found."}), 404

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = find_post_by_id(id)

    if post is None:
        return jsonify({"error": "Post not found."}), 404

    new_data = request.get_json()
    if new_data:
        post['title'] = new_data.get('title', post['title'])
        post['content'] = new_data.get('content', post['content'])

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    if not title and not content:
        return jsonify([])

    filtered_posts = []
    for post in POSTS:
        if title and title.lower() in post['title'].lower():
            filtered_posts.append(post)
        elif content and content.lower() in post['content'].lower():
            filtered_posts.append(post)

    return jsonify(filtered_posts)


def find_post_by_id(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


@app.route('/api/posts', methods=['GET'])
def page_limit():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    start_index = (page - 1) * limit
    end_index = start_index + limit

    paginated_posts = list(POSTS.values())[start_index:end_index]

    return jsonify(paginated_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
