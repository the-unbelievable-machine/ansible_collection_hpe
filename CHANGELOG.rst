==============================
unbelievable.hpe Release Notes
==============================

.. contents:: Topics


v3.0.0
======

Release Summary
---------------

Marjor release due to removal of some parameter aliases (see breaking changes)


Breaking Changes / Porting Guide
--------------------------------

- Modules ilo_*: removed parameter alias ilo_url
- Modules oneview_*: removed parameter alias oneview_url

Bugfixes
--------

- Module ilo_smartstorage_raids: correct smartstorage config selected if multiple array controllers are present.

v2.1.1
======

Release Summary
---------------

Bugfix release


v2.1.0
======

Release Summary
---------------

New modules added.


New Modules
-----------

- unbelievable.hpe.ilo_boot_order - Manage boot order
- unbelievable.hpe.ilo_power_state - Manage server power state via iLO
- unbelievable.hpe.ilo_smartstorage_raids - Create/configure/delete smartstorage raids

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
