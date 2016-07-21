from . import api
from flask import request
from ..models import User
from .. import db

@api.route('/register', methods=['POST'])
def register():
    user = User(request.form['tel'],    )
    db.session,.add(user)
    db.session.commit()

    return