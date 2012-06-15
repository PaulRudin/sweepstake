from flask import Flask, render_template
import operator
import read_xl
import results
app = Flask(__name__)

all_predictions = read_xl.AllPredictions()
results = results.Results()

@app.route('/', methods=['GET'])
def predictions():
    ADMINS = ['paul@rudin.co.uk']
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'root@rudin.co.uk',
                                   ADMINS, 'Predictions Failed')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    res = results.read_data()
    scores = all_predictions.score(res)
    scores.sort(key=operator.itemgetter(1), reverse=True)
    scores = [(name.title(), score) for name, score in scores]
    if not scores:
        return str(all_predictions.predictions)
    return render_template('scores.html', scores = scores)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
