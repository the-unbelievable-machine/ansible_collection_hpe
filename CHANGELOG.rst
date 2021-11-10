==============================
unbelievable.hpe Release Notes
==============================

.. contents:: Topics


v1.0.0
======

Release Summary
---------------

First release


New Plugins
-----------

Inventory
~~~~~~~~~

- unbelievable.hpe.oneview - HPE OneView inventory source

New Modules
-----------

Unbelievable
~~~~~~~~~~~~

hpe
^^^

- unbelievable.hpe.unbelievable.hpe.ilo_security_settings - Module to configure iLO security settings.
- unbelievable.hpe.unbelievable.hpe.ilo_thermal_settings - Module to configure iLO thermal settings.
- unbelievable.hpe.unbelievable.hpe.oneview_server_hardware_list - Module to query OneView server hardware. Could be used to dynamically add hosts using ansible.builtin.add_host

New Playbooks
-------------

- unbelievable.hpe.ilo_security_settings - Playbook to configure iLO security settings.
