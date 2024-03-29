# Ansible Collection - unbelievable.hpe

![CI workflow](https://github.com/the-unbelievable-machine/ansible_collection_hpe/actions/workflows/ci.yml/badge.svg)

The collection includes a variety of Ansible content to help automate the management of HPE OneView / iLO.

This collection provides specific modules. For a generic iLO modules, please see:

- [community.general.redfish_command](https://docs.ansible.com/ansible/latest/collections/community/general/redfish_command_module.html)
- [community.general.redfish_config](https://docs.ansible.com/ansible/latest/collections/community/general/redfish_config_module.html#ansible-collections-community-general-redfish-config-module)
- [community.general.redfish_info](https://docs.ansible.com/ansible/latest/collections/community/general/redfish_info_module.html#ansible-collections-community-general-redfish-info-module)

See also [Ansible Collection for HPE OneView](https://github.com/HewlettPackard/oneview-ansible-collection).

<!-- markdownlint-disable -->
<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>= 2.9**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->
<!-- markdownlint-enable -->
## Python Support

- Collection supports 2.7+

Note: Python2 is deprecated from [1st January 2020](https://www.python.org/doc/sunset-python-2/). Please switch to Python3.

## Installation and Usage

> **⚠️ WARNING**  
> Currently the collection is not available via Ansible Galaxy.

Before using the collection, you need to install it with the Ansible Galaxy CLI:

```bash
ansible-galaxy collection install https://github.com/the-unbelievable-machine/ansible_collection_hpe.git,v1.0.0
```

You can also include it in a `requirements.yml` file and install it via
`ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: unbelievable.hpe
    source: https://github.com/the-unbelievable-machine/ansible_collection_hpe.git
    type: git
    version: 1.0.0
```

## Included content

Click on the name of a plugin or module to view that content's documentation:

<!-- markdownlint-disable -->
<!--start requires_ansible-->
<!--end requires_ansible-->

<!--start collection content-->
### Inventory plugins
Name | Description
--- | ---
[unbelievable.hpe.oneview](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.oneview_inventory.rst)|HPE OneView inventory source

### Modules
Name | Description
--- | ---
[unbelievable.hpe.ilo_boot_order](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.ilo_boot_order_module.rst)|Manage boot order
[unbelievable.hpe.ilo_power_state](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.ilo_power_state_module.rst)|Manage server power state via iLO
[unbelievable.hpe.ilo_security_settings](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.ilo_security_settings_module.rst)|Manage iLO Security settings
[unbelievable.hpe.ilo_smartstorage_raids](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.ilo_smartstorage_raids_module.rst)|Create/configure/delete smartstorage raids
[unbelievable.hpe.ilo_thermal_settings](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.ilo_thermal_settings_module.rst)|Manage iLO Thermal settings
[unbelievable.hpe.imc_configdirectory](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.imc_configdirectory_module.rst)|Create/Delete config file directory
[unbelievable.hpe.imc_configfile](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.imc_configfile_module.rst)|Create/Delete config files
[unbelievable.hpe.imc_configfiles_info](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.imc_configfiles_info_module.rst)|List of content (config files) of a folder.
[unbelievable.hpe.imc_devices_info](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.imc_devices_info_module.rst)|Content of /plat/res/device endpoint of IMC
[unbelievable.hpe.oneview_inventory](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.oneview_inventory_module.rst)|Generates the same information as the oneview_inventory plugin.
[unbelievable.hpe.oneview_racks_info](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.oneview_racks_info_module.rst)|Content of /rest/racks endpoint of OneView
[unbelievable.hpe.oneview_server_hardware_info](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.oneview_server_hardware_info_module.rst)|Content of /rest/server-hardware endpoint of OneView
[unbelievable.hpe.oneview_server_profile_compliant](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.oneview_server_profile_compliant_module.rst)|Content of /rest/server-profiles endpoint of OneView
[unbelievable.hpe.oneview_server_profile_info](https://github.com/the-unbelievable-machine/ansible_collection_hpe/blob/v3.3.0/docs/unbelievable.hpe.oneview_server_profile_info_module.rst)|Content of /rest/server-profiles endpoint of OneView

<!--end collection content-->
<!-- markdownlint-enable -->

## playbooks

### unbelievable.hpe.ilo_security_stage.yml

**Usage:**

```bash
ansible-playbook -i <your-inventory> unbelievable.hpe.ilo_security_stage.yml
```

**Variables:**
Name                    | Required  | Default       | Description
----------------------- | --------  | ------------- | -------------------------------------------------------------
`target`                | no        | iLO5          | Playbook `hosts:` setting. Pass inventory groups or hostnames
`ilo_security_state`    | yes       |               | 'Production' or 'HighSecurity'. Prompted for if not set
`ilo_password`          | yes       |               | Prompted for if not set
`ilo_user`              | no        | Administrator |
`ilo_validate_certs`    | no        | True          | Validate ilo ssl ilo_validate_certs
`ilo_port`              | no        |               | if not set: omit / use module default
`ilo_proxy`             | no        |               | if not set: omit / use module default
`ilo_delegate_to`       | no        | localhost     | Where to delegate the task to.
