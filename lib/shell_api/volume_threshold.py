
from typing import Optional, List

from cinderclient.v3 import client

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenStackVolumeThreshold(OpenstackWrapperBase):

    def __init__(self, connection_cls=OpenstackConnection, CinderClient: Optional = None):
        super().__init__(connection_cls)
        self.CinderClient = CinderClient if CinderClient else client.Client

    def __getitem__(self, item):
        return getattr(self, item)

    def get_disk_space(self, cloud: str):
        with self._connection_cls(cloud) as conn:
            cinder = self.CinderClient(version=3, session=conn.session)
            volumeList = cinder.volumes.list()
            print(volumeList)
            count = len(volumeList)
            volumesizes = []
            TCount = 0
            FCount = 0
            for i in range(volumeList):
                print(volumeList[i])
                temp = volumeList[i].str().vol.id()
                quota = temp.get_volume_quotas()
                threshold = quota / temp.size * 100()
                volumesizes.append(temp.vol.size)
                volumesizes.append(threshold)
                if threshold > 80:
                    TCount + 1
                else:
                    FCount + 1
            return volumesizes, TCount, FCount


