from flask import request
from flask_restful import Resource
from openapi_core.shortcuts import RequestValidator
from openapi_core.wrappers.flask import FlaskOpenAPIRequest

from common import utils, errors

from service.models import db, Client

class ClientsResource(Resource):
    """
    Work with OAuth client objects
    """

    # @swag_from("resources/ldaps/list.yml")
    def get(self):
        clients = Client.query.all()
        return utils.ok(result=[cl.serialize for cl in clients], msg="Clients retrieved successfully.")

    def post(self):
        validator = RequestValidator(utils.spec)
        result = validator.validate(FlaskOpenAPIRequest(request))
        if result.errors:
            raise errors.ResourceError(msg=f'Invalid POST data: {result.errors}.')
        validated_body = result.body
        data = Client.get_derived_values(validated_body)
        client = Client(**data)
        db.session.add(client)
        db.session.commit()
        return utils.ok(result=client.serialize, msg="Client created successfully.")

class ClientResource(Resource):
    """
    Work with a single OAuth client objects
    """

    def get(self, client_id):
        client = Client.query.filter_by(client_id=client_id).first()
        if not client:
            raise errors.ResourceError(msg=f'No client object found with id {client_id}.')
        return utils.ok(result=client.serialize, msg='Client object retrieved successfully.')

