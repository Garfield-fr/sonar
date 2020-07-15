# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""JSON serializer for SONAR."""

import json

from flask import request
from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.serializers.json import \
    JSONSerializer as _JSONSerializer


class JSONSerializer(_JSONSerializer):
    """JSON serializer for SONAR."""

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Prepare record for serialization."""
        if request and request.args.get('resolve') == '1':
            record = record.replace_refs()

        return super(JSONSerializer,
                     self).preprocess_record(pid=pid,
                                             record=record,
                                             links_factory=links_factory,
                                             kwargs=kwargs)

    def post_process_serialize_search(self, results, pid_fetcher):
        """Post process the search results."""
        return results

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None, **kwargs):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        results = dict(
            hits=dict(
                hits=[self.transform_search_hit(
                    pid_fetcher(hit['_id'], hit['_source']),
                    hit,
                    links_factory=item_links_factory,
                    **kwargs
                ) for hit in search_result['hits']['hits']],
                total=search_result['hits']['total'],
            ),
            links=links or {},
            aggregations=search_result.get('aggregations', dict()),
        )
        return json.dumps(
            self.post_process_serialize_search(
                results, pid_fetcher), **self._format_args())


def schema_from_context(_, context, data, schema):
    """Get the record's schema from context."""
    record = (context or {}).get('record', {})

    return record.get('$schema', current_jsonschemas.path_to_url(schema))