import reactivex

from python_stack.core.utils.monitored.enums import (
    HealthStatusEnum,
    MonitorResourceTypeEnum,
    MonitorTypeEnum,
    ReadinessStatusEnum,
)
from python_stack.core.utils.monitored.service import (
    MonitoredService,
    MonitoredStatusUpdate,
)


class TestMonitoredService:
    def test_register_monitored_resource(self):
        service = MonitoredService()
        identifier = "resource1"
        monitor_type = MonitorTypeEnum.HEALTH
        resource_type = MonitorResourceTypeEnum.APPLICATION
        initial_status = HealthStatusEnum.HEALTHY

        subject = service.register_monitored_resource(
            monitor_type, resource_type, identifier, initial_status
        )

        # Assert that the subject is an instance of reactivex.Subject
        assert isinstance(subject, reactivex.Subject)

        # Assert that the monitored resource is registered correctly
        monitored_resource = service._monitored_resources[identifier]
        assert monitored_resource.types == {monitor_type}
        assert monitored_resource.resource_type == resource_type
        assert monitored_resource.identifier == identifier
        assert monitored_resource.health_status == initial_status
        assert monitored_resource.readiness_status is None
        assert monitored_resource.health_subject is subject
        assert monitored_resource.readiness_subject is None

    def test_handle_status_update(self):
        service = MonitoredService()
        identifier = "resource1"
        monitor_type = MonitorTypeEnum.HEALTH
        initial_status = HealthStatusEnum.HEALTHY

        subject = service.register_monitored_resource(
            monitor_type,
            MonitorResourceTypeEnum.APPLICATION,
            identifier,
            initial_status,
        )

        # Simulate a status update
        status_update = MonitoredStatusUpdate(
            identifier=identifier,
            monitor_type=monitor_type,
            status=HealthStatusEnum.UNHEALTHY,
        )
        service._handle_status_update(status_update)

        # Assert that the monitored resource's status is updated correctly
        monitored_resource = service._monitored_resources[identifier]
        assert monitored_resource.health_status == HealthStatusEnum.UNHEALTHY
