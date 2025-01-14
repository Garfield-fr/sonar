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

"""Permissions for users."""

from sonar.modules.organisations.api import OrganisationRecord, \
    current_organisation
from sonar.modules.permissions import RecordPermission
from sonar.modules.users.api import UserRecord


class UserPermission(RecordPermission):
    """Users permissions."""

    @classmethod
    def list(cls, user, record=None):
        """List permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        if not user:
            return False

        return True

    @classmethod
    def create(cls, user, record=None):
        """Create permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        if not user:
            return False

        return user.is_admin

    @classmethod
    def read(cls, user, record):
        """Read permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        if not user:
            return False

        # Can read himself in all cases
        if user['pid'] == record['pid']:
            return True

        # If not admin, no access
        if not user.is_admin:
            return False

        # Superuser is allowed
        if user.is_superuser:
            return True

        # Cannot read superusers records
        if UserRecord.ROLE_SUPERUSER == record['role']:
            return False

        user = UserRecord.get_record_by_pid(record['pid'])
        user = user.replace_refs()

        if not user.get('organisation'):
            return True

        return current_organisation['pid'] == user['organisation']['pid']

    @classmethod
    def update(cls, user, record):
        """Update permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # Same rules as read permission.
        return cls.read(user, record)

    @classmethod
    def delete(cls, user, record):
        """Delete permission check.

        :param user: Current user record.
        :param record: Record to check.
        :returns: True is action can be done.
        """
        # At least for admin logged users.
        if not user or not user.is_admin:
            return False

        # Superuser is allowed
        if user.is_superuser:
            return True

        # Cannot delete himself
        if user['pid'] == record['pid']:
            return False

        if not record.get('organisation'):
            return False

        # For admin read is only for logged user organisation
        if record['organisation'].get('$ref'):
            return current_organisation[
                'pid'] == OrganisationRecord.get_pid_by_ref_link(
                    record['organisation']['$ref'])

        return current_organisation['pid'] == record['organisation']['pid']
