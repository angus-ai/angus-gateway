#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

""" Command line tools for client id management
"""

__updated__ = "2015-12-28"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennaël Gâté"]
__status__ = "Production"

import argparse
import json
import random
import sys
import uuid

from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import crypt

__version__ = "0.1"
__updated__ = "2015-12-28"

BASE = declarative_base()


class Client(BASE):
    """ This is a client credential representation
    """
    __tablename__ = 'client'
    id = Column(String(36), nullable=False, primary_key=True)
    token = Column(String(36), nullable=True)
    email = Column(String(256), nullable=True)


def salt():
    """ Returns a string of 2 random letters
    """
    letters = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789/.'
    return random.choice(letters) + random.choice(letters)


def get_session(database):
    """ Get a session and bind on database
    """
    BASE.metadata.bind = database
    dbsession = sessionmaker(bind=database)
    session = dbsession()
    return session


def parse_cmd_line(argv):
    """ Command line options
    """
    formatter_class = argparse.RawDescriptionHelpFormatter

    parser = argparse.ArgumentParser(
        description='Command line tools for cloud access',
        formatter_class=formatter_class)

    parser.add_argument(
        '-db',
        '--database',
        type=str,
        required=True,
        nargs=1, help='the database file.')

    parser.add_argument(
        '-id',
        '--clientid',
        type=str,
        nargs=1,
        help='the client id.')

    parser.add_argument(
        '-t',
        '--accesstoken',
        type=str,
        nargs=1,
        help='the access token')

    parser.add_argument(
        '-a',
        '--action',
        type=str,
        nargs=1,
        required=True,
        choices=[
            'init',
            'revoke',
            'generate',
            'regenerate',
            'create',
            'htpasswd',
            'force'],
        help='action on the client id')

    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    args = parser.parse_args(argv[1:])
    return args


def init(database):
    """ Initialize a new client credentials database
    """
    BASE.metadata.create_all(database)
    print("Init db")


def revoke(database, client_id):
    """ Revoke client id
    """
    session = get_session(database)
    theclient = session.query(Client).get(client_id)
    theclient.token = None
    session.commit()


def generate(database):
    """ Generate a new access
    """
    client_id = str(uuid.uuid1())
    access_token = str(uuid.uuid4())
    create(database, client_id, access_token)


def create(database, client_id, access_token):
    """ Add client credentials in the database
    """
    session = get_session(database)

    session.add(Client(id=client_id, token=access_token))
    session.commit()

    credentials = {
        'client_id': client_id,
        'access_token': access_token,
    }
    print("Generate new user:\n%s" % (json.dumps(credentials)))


def regenerate(database, client_id):
    """ Regenerate access token for a client
    """
    force(database, client_id, access_token=str(uuid.uuid4()))


def force(database, client_id, access_token):
    """ Replace an access token for a client
    """
    session = get_session(database)
    theclient = session.query(Client).get(client_id)
    theclient.token = access_token
    session.commit()

    credentials = {
        'client_id': client_id,
        'access_token': access_token,
    }
    print(
        "Re-generate the access_token of a client_id:\n%s" %
        (json.dumps(credentials)))


def htpasswd(database):
    """ Generate on stdout a htpasswd file
    """
    session = get_session(database)

    clients = session.query(Client).all()
    for client in clients:
        if client.token:
            authd = crypt.crypt(client.token, salt())
            print("%s:%s" % (client.id, authd))


def main():
    """ Parse command line and run action
    """
    args = parse_cmd_line(sys.argv)
    database = args.database[0]
    database = create_engine(database)
    {
        'init': lambda: init(database),
        'revoke': lambda: revoke(database, args.clientid[0]),
        'generate': lambda: generate(database),
        'regenerate': lambda: regenerate(database, args.clientid[0]),
        'htpasswd': lambda: htpasswd(database),
        'force': lambda: force(database, args.clientid[0], args.accesstoken[0]),
        'create': lambda: create(database, args.clientid[0], args.accesstoken[0])
    }[args.action[0]]()

if __name__ == '__main__':
    main()
