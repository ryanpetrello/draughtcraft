Recipe builder and community app for homebrewing enthusiasts.

Building and Starting the Application
====================================
Draughtcraft runs on PostgreSQL.  Before you run it locally, you'll want to
create a local database.  The name configured by default is `draughtcraftdev`:

    $ createdb draughtcraftdev

    $ python setup.py develop
    $ pecan populate development.py
    $ pecan serve development.py

Running the Tests
=================
    $ python setup.py test

Deploying Remotely
=================

To start, you'll need at least two physical (or virtual) servers, one to
serve the Python application, and another to serve as a PostgreSQL database.
Additionally, you'll need to configure SSH key access for both of them, and
open up traffic on the PostgreSQL machine for inbound traffic on port (by
default) 5432.

From here, it's pretty simple:
$ cd ansible
$ pip install ansible

Edit the hosts file to point at the hostname (or IP) of your respective servers:
$ mv playbooks/hosts.example playbooks/hosts

$ mv playbooks/prod.yml.example playbooks/prod.yml
$ ansible-playbook -i playbooks/hosts playbooks/setup_server.yml playbooks/deploy.yml --private-key=~/.ssh/your-private-key
