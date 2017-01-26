import unittest

import docker

from .. import helpers


class SwarmTest(unittest.TestCase):
    def setUp(self):
        helpers.force_leave_swarm(docker.from_env())

    def tearDown(self):
        helpers.force_leave_swarm(docker.from_env())

    def test_init_update_leave(self):
        client = docker.from_env()
        client.swarm.init(
            snapshot_interval=5000, listen_addr=helpers.swarm_listen_addr()
        )
        assert client.swarm.attrs['Spec']['Raft']['SnapshotInterval'] == 5000
        client.swarm.update(snapshot_interval=10000)
        assert client.swarm.attrs['Spec']['Raft']['SnapshotInterval'] == 10000
        assert client.swarm.leave(force=True)
        with self.assertRaises(docker.errors.APIError) as cm:
            client.swarm.reload()
        assert (
            # FIXME: test for both until
            # https://github.com/docker/docker/issues/29192 is resolved
            cm.exception.response.status_code == 406 or
            cm.exception.response.status_code == 503
        )

    def test_init_set_advertise_addr(self):
        client = docker.from_env()
        client.swarm.init(advertise_addr="1.2.3.4:5678")
        assert (client.nodes.list()[0].attrs["ManagerStatus"]["Addr"] ==
                "1.2.3.4:5678")
        client.swarm.leave(force=True)
        client.swarm.init(advertise_addr="1.2.3.4:5676")
        assert (client.nodes.list()[0].attrs["ManagerStatus"]["Addr"] ==
                "1.2.3.4:5676")

    def test_init_set_listen_addr(self):
        client = docker.from_env()
        client.swarm.init(listen_addr=":5670")
        assert (":5670" in client.nodes.list()[0].attrs["ManagerStatus"]["Addr"])
        client.swarm.leave(force=True)
        client.swarm.init(listen_addr=":5679")
        assert (":5679" in client.nodes.list()[0].attrs["ManagerStatus"]["Addr"])
        client.swarm.leave(force=True)
