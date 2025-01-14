# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Deposits JSON schema class."""

from sonar.modules.users.api import current_user_record

from .json_schema_base import JSONSchemaBase


class DepositsJSONSchema(JSONSchemaBase):
    """JSON schema for deposits."""

    def process(self):
        """Document JSON schema custom process.

        :returns: The processed schema.
        """
        schema = super().process()

        organisation = {}
        if current_user_record:
            organisation = current_user_record.replace_refs() \
                .get('organisation')

        if not current_user_record or (current_user_record.is_moderator and \
            organisation.get('isDedicated', False)):
            return schema

        # Remove some fields on json for the shared organisation
        if not organisation.get('isDedicated', False):
            # Remove fields for shared organisation
            for field in [
                'collections', 'customField1', 'customField2', 'customField3'
            ]:
                schema['properties']['metadata']['properties']\
                    .pop(field, None)
                propertiesOrder = schema['properties']['metadata']\
                    .get('propertiesOrder', [])
                if field in propertiesOrder:
                    propertiesOrder.remove(field)

        # Remove subdivisions field
        schema['properties']['diffusion']['properties'].pop(
             'subdivisions', None)
        propertiesOrder = schema['properties']['diffusion']\
                .get('propertiesOrder', [])
        if 'subdivisions' in propertiesOrder:
            schema['properties']['diffusion']['propertiesOrder']\
                .remove('subdivisions')

        return schema
