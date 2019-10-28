from flask import Flask, request, jsonify, abort
from koinu import conv2

app = Flask(__name__)

@app.route('/api/nlp/<string:NLPSymbol>', methods=["POST"])
def nlp(NLPSymbol):
  return jsonify(conv2(NLPSymbol))

def main():
  app.run(host='0.0.0.0', port=8888, debug=True)

if __name__ == '__main__':
  main()
