"""Flask app serving record and model prediction endpoints"""
import logging
import os
from typing import Optional

from flask import Flask, jsonify, request

from ltss.vectorise import vectorise_record
from ltss.utils import format_record_for_frontend, read_records_csv
from ltss import los_model, risk_model

# Configuration for flask app
CONFIG = dict(
    ENV='development',
    # Generate SECRET_KEY using `python3 -c 'import os; print(os.urandom(16))'`
    SECRET_KEY=b'',
    # Pretty-print JSON even in production, for human readability
    JSONIFY_PRETTYPRINT_REGULAR=True,
)

# Initialise logging and directory paths
LOG = logging.getLogger('ltss.flask')
APP_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_DIR = os.path.join(os.path.dirname(APP_DIR), 'records')
RECORDS_FILE = 'example_records.csv'

# Global model instances to be instantiated on server startup and eliminate
# model load overheads at prediction-time.
LOS_MODEL: Optional[los_model.LoSPredictor] = None
RISK_MODEL: Optional[risk_model.RiskCDFModel] = None


def initialise_models():
    """Initialise both predictive models and persist to a global instance variable"""
    global LOS_MODEL, RISK_MODEL
    LOS_MODEL = los_model.init_model()
    RISK_MODEL = risk_model.init_model()


def create_app():
    """Construct flask app and define API endpoints"""
    LOG.debug('Initialising web server for LTSS')
    app = Flask('LTSS')
    # Configure app using global configuration
    app.config.from_mapping(CONFIG)
    # Initialise the predictive models
    initialise_models()

    @app.route('/api/records')
    def get_records():
        """
        Read records from csv file and serve as json object

        :return: JSON serialised object of patient records
        """
        try:
            records = {}
            for i, record in enumerate(read_records_csv(os.path.join(RECORDS_DIR, RECORDS_FILE))):
                # Add parsed record row to dict keyed on row index
                records[i] = record
        except Exception as e:
            # Log exception and return error code
            LOG.exception(e)
            return jsonify('Error reading records from file'), 500
        # Return success response with json records object
        return jsonify(records)

    @app.route('/api/record/<uuid>')
    def get_record(uuid):
        """Read patient record from csv file at specified row index offset

        :param uuid: ID of record in file to return
        :return: JSON serialised patient record matching uuid
        """
        try:
            for i, record in enumerate(read_records_csv(os.path.join(RECORDS_DIR, RECORDS_FILE))):
                if i == int(uuid):
                    # Parse retrieved record and serve json response
                    record = format_record_for_frontend(record)
                    return jsonify(record)
        except Exception as e:
            # Log exception and return error code
            LOG.exception(e)
            return jsonify(f'Error reading record at row index {uuid}'), 500
        # Return default 404 error if record index not found in file
        return jsonify(f'Unable to find record {uuid}'), 404

    @app.route('/api/forecast', methods=['POST'])
    def get_forecast():
        """Generate forecast from the predictive models using the posted record object fields as input

        :return: JSON serialised object of LoS and risk prediction values
        """
        # Check for json request body object
        if not request.json:
            return jsonify('Request body missing'), 400
        # Flatten and vectorise the record
        try:
            if isinstance(request.json, list):
                flattened = {k: v for d in request.json for k, v in d.items()}
            else:
                flattened = request.json
            vector = vectorise_record(flattened)
        except Exception as e:
            app.logger.exception(e)
            return jsonify('Error processing record'), 500
        # Check for non-major cases and return a no-forecast success response if the case is not identified as major
        if vector.get('IS_MAJOR', 1) == 0:
            return jsonify(dict(
                forecast=False,
                msg='Proof of concept system does not issue predictions for non-major cases',
            ))
        try:
            # Generate length of stay prediction from univariate GAN model
            forecast = los_model.get_prediction(LOS_MODEL, vector)
        except Exception as e:
            app.logger.exception(e)
            return jsonify('Error predicting against length of stay model'), 500
        try:
            # Generate risk stratification prediction from CDF risk model
            risk_predictions = risk_model.get_prediction(RISK_MODEL, vector,
                                                         ai_day_prediction=forecast.get('PREDICTED_LOS'))
            # Fuse model prediction dicts to a single forecast dict
            forecast = dict(forecast, **risk_predictions)
        except Exception as e:
            app.logger.exception(e)
            return jsonify('Error predicting against risk model'), 500
        # Return success response containing forecast flag and dict of predicted values
        return jsonify(dict(forecast=True, results=forecast))
    # Return constructed flask app
    return app
