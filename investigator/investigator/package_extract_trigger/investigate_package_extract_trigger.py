#!/usr/bin/env python3
# thoth-investigator
# Copyright(C) 2020 Kevin Postlethwait
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Investigate message to schedule package extract."""

import logging
from typing import Dict, Any

from thoth.messaging import PackageExtractTriggerMessage
from thoth.common import OpenShift

from ..common import wait_for_limit, register_handler
from ..configuration import Configuration

from .metrics_package_extract_trigger import package_extract_trigger_exceptions
from .metrics_package_extract_trigger import package_extract_trigger_in_progress
from .metrics_package_extract_trigger import package_extract_trigger_success
from prometheus_async.aio import track_inprogress, count_exceptions

_LOGGER = logging.getLogger(__name__)


@count_exceptions(package_extract_trigger_exceptions)
@track_inprogress(package_extract_trigger_in_progress)
@register_handler(PackageExtractTriggerMessage().topic_name, ["v1"])
async def parse_package_extract_trigger_message(package_extract_trigger: Dict[str, Any], openshift: OpenShift) -> None:
    """Parse package_extract_trigger message."""
    await wait_for_limit(openshift, workflow_namespace=Configuration.THOTH_BACKEND_NAMESPACE)
    workflow_name = openshift.schedule_package_extract(
        image=package_extract_trigger["image"],
        environment_type=package_extract_trigger["environment_type"],
        is_external=package_extract_trigger["is_external"],
        origin=package_extract_trigger["origin"],
        registry_user=package_extract_trigger["registry_user"],
        registry_password=package_extract_trigger["registry_password"],
        verify_tls=package_extract_trigger["verify_tls"],
        debug=package_extract_trigger["debug"],
        job_id=package_extract_trigger["job_id"],
    )
    _LOGGER.debug(f"Scheduled package extract workflow {workflow_name}")
    package_extract_trigger_success.inc()
