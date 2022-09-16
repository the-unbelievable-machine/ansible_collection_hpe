# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.unbelievable.hpe.plugins.module_utils.logger import SilentLogger  # type: ignore
from ansible_collections.unbelievable.hpe.plugins.module_utils.api_client import (  # type: ignore
    JsonRestApiClient,
    ModuleBase,
)


class ImcApiClient(JsonRestApiClient):

    API_BASE = "/imcrs/"
    FILE_TYPE_FOLDER = "-1"
    FILE_TYPE_FILE = "1"
    FILE_TYPE_SEGMENT = "2"
    FILE_TYPE_CLI_SCRIPT = "4"
    _FILE_TYPE_NAME_2_TYPE = {
        "folder": FILE_TYPE_FOLDER,
        "file": FILE_TYPE_FILE,
        "segment": FILE_TYPE_SEGMENT,
        "cli_script": FILE_TYPE_CLI_SCRIPT,
    }
    _FILE_TYPE_2_NAME = {v: k for k, v in _FILE_TYPE_NAME_2_TYPE.items()}

    def __init__(
        self,
        protocol,
        host,
        port,
        username,
        password,
        validate_certs=True,
        proxy=None,
        logger=SilentLogger(),
    ):
        super(ImcApiClient, self).__init__(
            protocol=protocol,
            host=host,
            port=port,
            api_base=ImcApiClient.API_BASE,
            username=username,
            password=password,
            validate_certs=validate_certs,
            proxy=proxy,
            logger=logger,
        )

    def get_auth(self):
        from requests.auth import HTTPDigestAuth

        return HTTPDigestAuth(self.username, self.password) if self.username else None

    def get_file_type(self, file_type_name):
        return ImcApiClient._FILE_TYPE_NAME_2_TYPE.get(file_type_name)

    def get_file_type_name(self, file_type):
        return ImcApiClient._FILE_TYPE_2_NAME.get(str(file_type))

    def list_devices(self):
        return self._collect_content("/plat/res/device?size=100", "device")

    def get_folder_id(self, folder_path, parent_folder_id=-1):
        folder_id = None
        if folder_path.startswith("/"):
            folder_path = folder_path[1:]
        folder_name, _ignore, sub_folders = folder_path.partition("/")
        items = self.list_folder(parent_folder_id)
        folder = self._get_folder_item(items, folder_name, ImcApiClient.FILE_TYPE_FOLDER)
        if folder:
            if not sub_folders:
                folder_id = folder["confFileId"]
            else:
                folder_id = self.get_folder_id(sub_folders, folder["confFileId"])
        return folder_id

    def list_folder(self, folder_id):
        return self._collect_content("/icc/confFile/list/{0}?size=100".format(folder_id), "confFile")

    def get_file_id(self, folder_id, file_name, file_type):
        if file_name.startswith("/"):
            file_name = file_name[1:]
        items = self.list_folder(folder_id)
        file_info = self._get_folder_item(items, file_name, file_type)
        return file_info["confFileId"] if file_info else None

    def get_file(self, file_id):
        return self.get_request("/icc/confFile/{0}".format(file_id))

    def delete_file(self, file_id):
        return self.delete_request("/icc/confFile/{0}".format(file_id))

    def create_file(self, folder_id, file_name, file_type, content):
        payload = {"confFileName": file_name, "confFileType": file_type, "cfgFileParent": folder_id, "content": content}
        api_response = self.post_request_with_headers("/icc/confFile", data=payload)
        return api_response.headers["location"].split("/")[-1]

    def create_folder(self, parent_folder_id, folder_name):
        payload = {
            "confFileName": folder_name,
            "confFileType": ImcApiClient.FILE_TYPE_FOLDER,
            "cfgFileParent": parent_folder_id,
            "content": "",
        }
        api_response = self.post_request_with_headers("/icc/confFile", data=payload)
        return api_response.headers["location"].split("/")[-1]

    def delete_folder(self, folder_id):
        return self.delete_request("/icc/confFile/{0}".format(folder_id))

    def _get_folder_item(self, items, file_name, *item_types):
        for item in items:
            if item["confFileName"] == file_name and (not item_types or item["confFileType"] in item_types):
                return item
        return None

    def _collect_content(self, url, key):
        next_url = url
        content = []
        while next_url:
            self.logger.debug("ImcApiClient: {0}".format(next_url))
            data = self.get_request(next_url)
            if key in data:
                val = data[key]
                if isinstance(val, list):
                    content.extend(val)
                elif isinstance(val, dict):
                    content.append(val)
                else:
                    raise TypeError("Unexpected data type: expected dict or list, got " + type(val))
            next_url = self._get_next_link(data)
        return content

    def _get_next_link(self, data):
        next_link = None
        if data and "link" in data:
            for link in [data["link"]] if isinstance(data["link"], dict) else data["link"]:
                if link["@rel"] == "next":
                    next_link = link["@href"].partition(ImcApiClient.API_BASE)[2]
                    break
        return next_link


class ImcModuleBase(ModuleBase):
    def __init__(self):
        super(ImcModuleBase, self).__init__(param_alias_prefix="imc")

    def argument_spec(self):
        additional_spec = dict()
        spec = dict()
        spec.update(super(ImcModuleBase, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def get_module_api_client(self, protocol, host, port, username, password, validate_certs, proxy, logger):
        return ImcApiClient(
            protocol=protocol,
            host=host,
            port=port,
            username=username,
            password=password,
            validate_certs=validate_certs,
            proxy=proxy,
            logger=logger,
        )

    def get_folder_id(self, param_name_name="folder_name", param_name_id="folder_id"):
        folder_id = None
        if self.module.params.get(param_name_name):
            folder_name = self.module.params.get(param_name_name)
            folder_id = self.api_client.get_folder_id(folder_name)
            if not folder_id:
                self.module.fail_json(msg="Folder '{0}' not found".format(folder_name))
        else:
            folder_id = self.module.params.get(param_name_id)
        return folder_id

    def get_file_type(self):
        file_type_name = self.module.params.get("file_type")
        return self.api_client.get_file_type(file_type_name)
