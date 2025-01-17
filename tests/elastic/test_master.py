import runpy
import threading
from concurrent.futures import Future
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import grpc
from google.protobuf.empty_pb2 import Empty
from pytest_mock import MockerFixture

from oobleck.elastic import master_service_pb2, master_service_pb2_grpc, run
from oobleck.elastic.run import (
    HostInfo,
    LaunchArguments,
    MasterService,
    MultiNodeAgentRunner,
    ScriptArguments,
)


def get_stub(port: int) -> master_service_pb2_grpc.OobleckMasterStub:
    channel = grpc.insecure_channel(f"localhost:{port}")
    return master_service_pb2_grpc.OobleckMasterStub(channel)


def test_get_dist_info(
    server: tuple[LaunchArguments, ScriptArguments, MasterService, int],
):
    fake_master_args, _, _, port = server
    stub = get_stub(port)
    dist_info: master_service_pb2.DistInfo = stub.GetDistInfo(Empty())

    fake_dist_info = HostInfo.fetch_hostfile(fake_master_args.hostfile)
    assert len(dist_info.hosts) == len(fake_dist_info)
    for host, fake_host in zip(dist_info.hosts, fake_dist_info):
        assert host.ip == fake_host.ip
        assert host.devices == fake_host.devices
        assert host.port == fake_host.port


def test_get_code(
    server: tuple[LaunchArguments, ScriptArguments, MasterService, int],
    mocker: MockerFixture,
):
    _, fake_script_args, _, port = server
    stub = get_stub(port)
    result = stub.GetCode(Empty())
    assert Path(result.path) == fake_script_args.training_script
    assert result.args == fake_script_args.training_script_args

    mocker.patch("sys.argv", ["fake_script.py"] + fake_script_args.training_script_args)

    f = StringIO()
    with redirect_stdout(f):
        runpy.run_path(result.path, run_name="__main__")
    assert (
        f.getvalue()
        == f"Hello, {fake_script_args.training_script_args[1]}, {fake_script_args.training_script_args[3]}\n"
    )


def test_receive_reconfiguration_notification(
    server: tuple[LaunchArguments, ScriptArguments, MasterService, int],
):
    _, _, service, port = server

    from queue import Queue

    queue = Queue()

    def run_watcher(queue: Queue):
        stub = get_stub(port)
        dist_info = next(stub.WatchReconfigurationNotification(Empty()))
        queue.put(dist_info)

    threading.Thread(target=run_watcher, args=(queue,), daemon=True).start()

    # Wait until the thread is waiting
    while service.disconnect_condition._sleeping_count.get_value() == 0:
        pass

    assert service.disconnect_condition._sleeping_count.get_value() == 1

    # Manipulate dist info in service
    with service.disconnect_condition:
        run.agent_list.pop(-1)
        service.disconnect_condition.notify_all()

    dist_info: master_service_pb2.DistInfo = queue.get(timeout=10)
    assert len(dist_info.hosts) == 2
    for host, (fake_host, _) in zip(dist_info.hosts, run.agent_list[:-1]):
        assert host.ip == fake_host.ip
        assert host.devices == fake_host.devices
        assert host.port == fake_host.port


def test_run_agents(
    server: tuple[LaunchArguments, ScriptArguments, MasterService, int],
    mocker: MockerFixture,
):
    args, _, _, port = server
    hosts = HostInfo.fetch_hostfile(args.hostfile)
    disconnect_condition = None

    future = Future()
    future.set_result(None)
    mock_executor = mocker.patch(
        "oobleck.elastic.run.ProcessPoolExecutor.submit", return_value=future
    )

    runner = MultiNodeAgentRunner(
        disconnect_condition=disconnect_condition,
        hosts=hosts,
        master_service_port=port,
        tag=args.tag,
        base_dir=args.base_dir,
    )
    run.agent_list.clear()
    runner.run()

    assert mock_executor.call_count == len(hosts)

    for agent_index, (call_args, host) in enumerate(
        zip(mock_executor.call_args_list, hosts)
    ):
        call_args = call_args[0]
        assert call_args == (
            runner.run_on_nodes,
            agent_index,
            host,
            port,
            args.tag,
            args.base_dir,
            args.debug,
        )
