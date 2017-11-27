#!/usr/bin/env python
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

""" This is the gateway for all services.
Right now, it manages blob storage and service repository.
"""

import collections
import json
import logging
import os
import uuid

import tornado.ioloop
import tornado.web
import angus.framework

LOGGER = logging.getLogger(__name__)

__updated__ = "2017-11-10"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2016, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennaël Gâté"]
__status__ = "Production"


class Storage(object):
    """ Storage class for blobs
    """

    def __init__(self, size=10):
        self.size = size
        self.inner = collections.OrderedDict()

    def store(self, key, content, meta=None):
        """ Store a new blob
        """
        self.inner[key] = (content, meta)
        if len(self.inner) > self.size:
            self.inner.popitem(last=False)

    def get(self, key):
        """ Get back a blob
        """
        return self.inner.get(key)

    def iteritems(self):
        """ Iterator over content
        """
        return self.inner.iteritems()


class Services(tornado.web.RequestHandler):
    """ Handler that present all server services
    """

    def initialize(self, service_map):
        """
        List all avaialble service based on a service map:
        { (service_name, service_version) => service_url }
        """
        tornado.web.RequestHandler.initialize(self)
        self.service_map = service_map

    def get(self):
        response = dict()

        for service in self.service_map.keys():
            response[service] = {
                'url': "/services/%s" % (service),
            }

        response = dict(services=response)

        self.write(json.dumps(response))


class Service(tornado.web.RequestHandler):
    """ Handler for service
    """

    def initialize(self, service_map):
        """
        Create a handler on a dictionary versions
        { (service_name, service_version) => service_url }
        """
        tornado.web.RequestHandler.initialize(self)
        self.service_map = service_map

    def get(self, service):
        if service not in self.service_map:
            self.set_status(404, "Unknown service %s" % (service))
            return

        response = dict()

        for version, href in self.service_map[service].iteritems():
            response[version] = dict(url=href)

        response = dict(versions=response)

        self.write(json.dumps(response))


class Versions(tornado.web.RequestHandler):
    """ Handler for service versions
    """

    def initialize(self, service_map):
        """
        Create a handler on a dictionary versions
        { (service_name, service_version) => service_url }
        """
        tornado.web.RequestHandler.initialize(self)
        self.service_map = service_map

    def get(self, service, version):

        # get a description
        response = {
            'description': 'Not available',
        }
        self.write(json.dumps(response))


class BlobStorage(tornado.web.RequestHandler):
    """ Handler for blob creation
    """

    def initialize(self, storage):
        self.storage = storage

    def post(self):
        status = 201
        self.set_status(status, "Blob created")
        data = self.request.body_arguments['meta'][0]
        data = json.loads(data)
        file_url = data['content']

        content = self.request.files[file_url][0]['body']
        uid = unicode(uuid.uuid1())
        user = angus.framework.extract_user(self)

        self.storage.store(uid, content, dict(owner=user))

        public_url = "%s://%s" % (self.request.protocol, self.request.host)

        response = {
            'status': status,
            'url': "%s/blobs/%s" % (public_url, uid),
        }

        self.write(json.dumps(response))


class Blob(tornado.web.RequestHandler):
    """ Handler for a blob
    """

    def initialize(self, storage):
        self.storage = storage

    def get(self, uid):
        user = angus.framework.extract_user(self)
        res = self.storage.get(uid)
        if res is not None:
            content, meta = res
            if meta['owner'] == user:
                self.write(content)
                self.set_status(200)
                self.flush()
            else:
                self.set_status(403, "Not owner")
        else:
            self.set_status(404, "Blob resource %s not found" % (uid))


def find_services():
    """ Retrive service description
    """
    service_dir = os.environ.get('SERVICE_DIR', None)
    service_file = os.environ.get('SERVICE_FILE', '/etc/angus-gateway/services.json')
    service_name = os.environ.get('SERVICE_NAME', None)
    service_url = os.environ.get('SERVICE_URL', None)
    service_version = os.environ.get('SERVICE_VERSION', 1)

    if service_dir is not None:
        services = json.loads(service_dir)
    elif service_name is not None and service_url is not None:
        services = dict()
        services[service_name] = dict()
        services[service_name][service_version] = service_url
    elif service_file is not None and os.path.isfile(service_file):
        with open(service_file, 'r') as sfile:
            services = json.loads(sfile.read())
    else:
        services = dict()  # No available service

    return services

def main():
    """ Run the service
    """
    logging.basicConfig(level=logging.INFO)
    home = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    port = os.environ.get('PORT', 8080)
    services = find_services()
    msg = "Available services:\n" + json.dumps(services, indent=4)
    LOGGER.info(msg)
    storage = Storage(size=300)
    application = tornado.web.Application([
        (r"/services/(?P<service>.*)/(?P<version>.*)",
         Versions,
         dict(service_map=services)),
        (r"/services/(?P<service>.*)", Service, dict(service_map=services)),
        (r"/services", Services, dict(service_map=services)),
        (r"/blobs/(.*)", Blob, dict(storage=storage)),
        (r"/blobs", BlobStorage, dict(storage=storage)),
        (r"/(.*)",
         tornado.web.StaticFileHandler,
         {'path': "%s/static/public/" % (home)}),

    ])
    application.listen(port, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
