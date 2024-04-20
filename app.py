from flask import Flask, request, jsonify
from service import ML_Service

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    data = {"status": 'ok'}
    return jsonify(data)

@app.route('/healthz')
def healthz():
    return "OK"

@app.route("/analisys", methods=["GET"])
def analisys():

    filename = request.args.get("filename", type=str)

    if filename is None :
        data = {"error": 'wrong request'}
        return jsonify(data), 404

    try:
        service = ML_Service()
        data = service.predict(filename)
    except:
        data = {"error": 'Service is down'}
        return jsonify(data), 404

    return jsonify(data)

@app.route('/predict',methods=['POST','GET'])
def predict():
    req = request.json.get('instances')

    filename = req[0]['filename']

    if filename is None :
        data = {"error": 'wrong request'}
        return jsonify(data), 404

    try:
        service = ML_Service()
        data = service.predict(filename)
    except:
        data = {"error": 'Service is down'}

    '''
    output = {'predictions':[
        {
        "label": "beach",
        "scores": [0.1, 0.9]
        },
        {
        "label": "car",
        "scores": [0.75, 0.25]
        }
    ]}
    '''
    predictions = []
    for label, score in data.items():
        predictions.append({
            "label": label,
            "scores": [score]
        })

    output = {"predictions": predictions}

    return jsonify(output)

@app.errorhandler(404)

# inbuilt function which takes error as parameter
def not_found(e):
    data = {"error": 'route not found'}
    return jsonify(data), 404

if __name__ == "__main__":
    app.run(debug=False)