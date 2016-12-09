=====================
Angus Gateway Service
=====================

Configuration
=============

* PORT (default 8080): listen port
* SERVICE_FILE (default /etc/angus-gateway/services.json): the service
  directory

Mono service option
+++++++++++++++++++

* SERVICE_NAME (default None): the service name
* SERVICE_VERSION (default 1): the service version
* SERVICE_URL (default None): the service url

Releases
========

Angus Gateway Service - Release Note 0.0.2
++++++++++++++++++++++++++++++++++++++++++

Features added
--------------
* Microservice architecture with docker (Dockerfile)
* Define a service name, version and url for atomic run

Update
------
* Default service file location
* Move to default port 80



Angus Gateway Service - Release Note 0.0.1
++++++++++++++++++++++++++++++++++++++++++

Features added
--------------

* Primitive (in-memory) blob storage
* HTPASSWD access management (angus-access)
* Service repository
