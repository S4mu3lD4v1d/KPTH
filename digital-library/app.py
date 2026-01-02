from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import git
import os

app = Flask(__name__)

es = Elasticsearch()

repo_path = 'library_repo'
if not os.path.exists(repo_path):
    os.makedirs(repo_path)
    repo = git.Repo.init(repo_path)

@app.route('/add_literature', methods=['POST'])
def add_literature():
    title = request.json['title']
    content = request.json['content']
    # Save to file
    filename = f"{title}.txt"
    with open(os.path.join(repo_path, filename), 'w') as f:
        f.write(content)
    # Version with git
    repo = git.Repo(repo_path)
    repo.index.add([filename])
    repo.index.commit(f"Added {title}")
    # Index for search
    es.index(index='literature', id=title, body={'title': title, 'content': content})
    return jsonify({'status': 'added'})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    res = es.search(index='literature', body={'query': {'match': {'content': query}}})
    return jsonify(res['hits']['hits'])

if __name__ == '__main__':
    app.run(debug=True, port=5001)