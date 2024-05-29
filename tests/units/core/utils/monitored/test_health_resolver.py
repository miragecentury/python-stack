"""
Test cases for HealthStatusServiceResolver
"""

import pytest

from python_stack.core.utils.monitored.service import (
    HealthStatusEnum,
    HealthStatusServiceResolver,
    MonitoredResource,
    MonitorResourceTypeEnum,
    MonitorTypeEnum,
    ReadinessStatusEnum,
)


class TestHealthStatusServiceResolver:
    """
    Test cases for HealthStatusServiceResolver
    """

    @pytest.mark.parametrize(
        "monitored_resources, expected_health_status",
        [
            pytest.param(
                {
                    "resource_1": MonitoredResource(
                        types={MonitorTypeEnum.HEALTH},
                        resource_type=MonitorResourceTypeEnum.DATABASE,
                        identifier="resource_1",
                        health_status=HealthStatusEnum.HEALTHY,
                        readiness_status=None,
                        health_subject=None,
                        readiness_subject=None,
                    ),
                    "resource_2": MonitoredResource(
                        types={MonitorTypeEnum.HEALTH},
                        resource_type=MonitorResourceTypeEnum.DATABASE,
                        identifier="resource_2",
                        health_status=HealthStatusEnum.HEALTHY,
                        readiness_status=None,
                        health_subject=None,
                        readiness_subject=None,
                    ),
                },
                HealthStatusEnum.HEALTHY,
                id="all_health_resources_are_healthy",
            ),
            pytest.param(
                {
                    "resource_1": MonitoredResource(
                        types={MonitorTypeEnum.HEALTH},
                        resource_type=MonitorResourceTypeEnum.DATABASE,
                        identifier="resource_1",
                        health_status=HealthStatusEnum.HEALTHY,
                        readiness_status=None,
                        health_subject=None,
                        readiness_subject=None,
                    ),
                    "resource_2": MonitoredResource(
                        types={MonitorTypeEnum.HEALTH},
                        resource_type=MonitorResourceTypeEnum.DATABASE,
                        identifier="resource_2",
                        health_status=HealthStatusEnum.UNHEALTHY,
                        readiness_status=None,
                        health_subject=None,
                        readiness_subject=None,
                    ),
                },
                HealthStatusEnum.UNHEALTHY,
                id="one_health_resource_is_unhealthy",
            ),
            pytest.param(
                {
                    "resource_1": MonitoredResource(
                        types={MonitorTypeEnum.HEALTH},
                        resource_type=MonitorResourceTypeEnum.DATABASE,
                        identifier="resource_1",
                        health_status=HealthStatusEnum.HEALTHY,
                        readiness_status=None,
                        health_subject=None,
                        readiness_subject=None,
                    ),
                    "resource_2": MonitoredResource(
                        types={MonitorTypeEnum.HEALTH},
                        resource_type=MonitorResourceTypeEnum.DATABASE,
                        identifier="resource_2",
                        health_status=HealthStatusEnum.UNKNOWN,
                        readiness_status=None,
                        health_subject=None,
                        readiness_subject=None,
                    ),
                },
                HealthStatusEnum.HEALTHY,
                id="one_health_resource_is_unknown",
            ),
        ],
    )
    def test_resolver(
        self,
        monitored_resources: dict[str, MonitoredResource],
        expected_health_status: HealthStatusEnum,
    ):
        """
        Test HealthStatusServiceResolver.resolve
        Resulve the health status of the monitored resources
        """
        resolver = HealthStatusServiceResolver(monitored_resources)
        assert resolver.resolve() == expected_health_status

    def test_resolver_ignore_not_health_monitored_resources(self):
        """
        Test HealthStatusServiceResolver.resolve
        Ignore monitored resources that are not of type MonitorTypeEnum.HEALTH
        """
        monitored_resources = {
            "resource_1": MonitoredResource(
                types={MonitorTypeEnum.READINESS},
                resource_type=MonitorResourceTypeEnum.DATABASE,
                identifier="resource_1",
                health_status=None,
                readiness_status=ReadinessStatusEnum.READY,
                health_subject=None,
                readiness_subject=None,
            ),
            "resource_2": MonitoredResource(
                types={MonitorTypeEnum.HEALTH},
                resource_type=MonitorResourceTypeEnum.DATABASE,
                identifier="resource_2",
                health_status=HealthStatusEnum.HEALTHY,
                readiness_status=None,
                health_subject=None,
                readiness_subject=None,
            ),
        }

        resolver = HealthStatusServiceResolver(monitored_resources)
        assert resolver.resolve() == HealthStatusEnum.HEALTHY
