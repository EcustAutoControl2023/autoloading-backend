import socket
import os
import tempfile

import pytest

from autoloading import create_app
from autoloading.models import get_db

from autoloading.models.sensor import loader_num, Traffic
for i in range(loader_num):
    exec(f'from autoloading.models.sensor import Sensor{i+1}')

def pytest_sessionfinish(session, exitstatus):
    # printr("all down")
    pass

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    # db_fd, db_path = tempfile.mkstemp()
    # printr('on app setup')

    # create the app with common test config
    # 在当前目录下test子目录下
    db_path = os.path.join(os.path.realpath(""), "test/test.db")
    # db_path='/mnt/BaiduSyncdisk/OB/notes/2--Inputs/代码/自动装车/autoloading-backend/test/test.db'

    db_uri = f'sqlite:///{db_path}'
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": db_uri
    })

    yield app

    # close and remove the temporary database
    # os.close(db_fd)
    # os.unlink(db_path)
    # 删除数据库
    # os.unlink(db_path)

    # printr('on app teardown')


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="admin", password="password"):
        return self._client.post(
            "/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)

# 确保每次使用完数据库后清除所有插入的数据
@pytest.fixture
def db(app):
    db = get_db()
    with app.app_context():
        yield db

        for i in range(loader_num):
            exec(f'db.session.query(Sensor{i+1}).delete()')
        db.session.query(Traffic).delete()
        db.session.commit()


def printr(msg, prefix='XXX'):
    print(f'\033[31m{prefix}: {msg}\033[0m')

def udp_client(serverInfo, send_data):
    host, port = serverInfo
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送请求数据
    client_socket.sendto(bytes(send_data, encoding="utf8"), (host, port))

    # 接收服务器信息
    data, addr = client_socket.recvfrom(1024)

    client_socket.close()
