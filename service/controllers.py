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
        client = Client()
        db.session.add(client)
        db.session.commit()
        return utils.ok(result=ldap.serialize,
                        msg="LDAP object created successfully.")

