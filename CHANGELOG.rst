==============================
unbelievable.hpe Release Notes
==============================

.. contents:: Topics


v2.1.0
======

Release Summary
---------------

New modules added.


New Modules
-----------

Unbelievable
~~~~~~~~~~~~

hpe
^^^

- unbelievable.hpe.unbelievable.hpe.ilo_boot_order - Module to manage the boot order
- unbelievable.hpe.unbelievable.hpe.ilo_power_state - Module to manage server power state via iLO.
- unbelievable.hpe.unbelievable.hpe.ilo_smartstorage_raids - Module to manage SmartStorage raid configuration

v2.0.0
======

Release Summary
---------------

Rewrite of oneview modules.

Renamed module 'oneview_server_hardware_list' to 'oneview_inventory'
Added module 'oneview_racks_info'
Added module 'oneview_server_hardware_info'


Breaking Changes / Porting Guide
--------------------------------

- Renamed module 'oneview_server_hardware_list' to 'oneview_inventory'

New Modules
-----------

- unbelievable.hpe.oneview_racks_info - Content of /rest/racks endpoint of OneView
- unbelievable.hpe.oneview_server_hardware_info - Content of /rest/server-hardware endpoint of OneView

v1.0.2
======

Release Summary
---------------

Bugfix release.


Bugfixes
--------

- remove prefix 'v' from version tags

v1.0.1
======

Release Summary
---------------

Bugfix release.


Bugfixes
--------

- Module oneview_server_hardware_list - support for check mode enabled.

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

- unbelievable.hpe.ilo_security_settings - Manage iLO Security settings
- unbelievable.hpe.ilo_thermal_settings - Manage iLO Thermal settings
