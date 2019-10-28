from flask import Flask, request, jsonify, abort
from koinu import conv2
import os

app = Flask(__name__)

@app.route('/api/nlp/<string:NLPSymbol>', methods=["POST"])
def nlp(NLPSymbol):
  return jsonify(conv2(NLPSymbol))

def main():
  port = int(os.environ.get("PORT", 8888))
  app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
  main()
