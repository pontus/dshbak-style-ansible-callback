# dshbak-style-ansible-callback
A simple callback for ansible to provide dshbak style host unions.

To use it, put it somewhere and add a line 

callback_plugins = /somewhere

to your ansible configuration (~/.ansible.cfg).

For the versions of ansible I've used, setting the stdout callback
(stdout_callback) has not worked (at least when not using playbooks),
but it's possible to override the standard minimal plugin.

For this reason, you likely want this to be called minimal.py.

