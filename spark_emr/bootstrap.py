import os
import uuid
import glob
import shutil
import loguru
import tempfile
import subprocess

import spark_emr.util
from spark_emr.const import (SH_INSTALL_PYTHON, SH_LOCAL_PYPACKAGE,
                             SH_PYPI_PYPACKAGE,
                             PYTHON_VERSION)

log = loguru.logger

INSTALL_PYTHON = """
#!/bin/bash
set -ex
sudo yum install -y {pv} {pv}-devel {pv}-setuptools
sudo easy_install-{pvs} pip
sudo /usr/local/bin/pip3 install --upgrade pip
"""

INSTALL_PYPI = """
#!/bin/bash
set -ex
sudo /usr/local/bin/pip3 install -i {index_url} {package}
"""  # noqa

INSTALL_PYPACKAGE = """
#!/bin/bash
set -ex
aws s3 cp {path} {name}.whl
sudo /usr/local/bin/pip3 install {name}.whl
"""


class BootstrapManager(object):

    def __init__(self, region, python_version, bootstrap_uri):
        self.region = region
        self.python_version = python_version
        self.bootstrap_base = bootstrap_uri
        self.s3mgr = spark_emr.util.S3Manager(region)

    def call_shell(self, cmd):
        subprocess.call(
            cmd,
            shell=True,
            stdout=open(
                os.devnull,
                "w"))

    def _create_pypackage(self, package):
        tempfolder = os.path.join(tempfile.gettempdir(),
                                  uuid.uuid4().hex)
        build_directory = os.path.join(package, "build")
        shutil.rmtree(build_directory, ignore_errors=True)

        # create the pypackage file which contains the source code
        pypackage_cmd = "cd %s && python3 setup.py bdist_wheel -d %s" % (
            package, tempfolder)
        self.call_shell(
            "mkdir {dir} && chmod 777 {dir}".format(
                dir=tempfolder))
        self.call_shell(pypackage_cmd)

        log.info("Created <<package:%s>> in <<pydir:%s>>" % (
            package, tempfolder))
        ret = glob.glob(os.path.join(tempfolder, "*.whl"))
        assert len(ret) == 1
        return ret[0]

    def _python_action(self):
        install_python = INSTALL_PYTHON.format(
            pv=self.python_version,
            pvs=PYTHON_VERSION[self.python_version])
        install_python_uri = self.bootstrap_base.file_append(SH_INSTALL_PYTHON)
        self.s3mgr.put_content(
            target_uri=install_python_uri,
            content=install_python)
        log.info("Uploaded to <<install_python_uri:%s>>" % install_python_uri)

        ret = {
            "Name": "Install python",
            "ScriptBootstrapAction": {
                "Path": install_python_uri.uri,
                "Args": []
            }
        }
        return ret

    def _pypi_action(
            self,
            package,
            index_url="https://pypi.org/simple"):
        package = package.split("pip+")[1]
        install_from_pypi = self.bootstrap_base.file_append(SH_PYPI_PYPACKAGE)
        install_pypi = INSTALL_PYPI.format(
            index_url=index_url, package=package)
        self.s3mgr.put_content(
            target_uri=install_from_pypi, content=install_pypi)
        log.info("Uploaded <<install_pypi_uri:%s>>" % install_from_pypi)

        ret = {
            "Name": "Install package from pypi",
            "ScriptBootstrapAction": {
                "Path": install_from_pypi.uri,
                "Args": []
            }
        }
        return ret

    def _local_pypackage_action(self, package):
        # create new pypackage
        pypackage_path = self._create_pypackage(package)
        pypackage_name = pypackage_path.split("/")[-1]
        # upload to S3
        pypackage_uri = self.bootstrap_base.file_append(pypackage_name)
        self.s3mgr.upload(pypackage_path, pypackage_uri)
        log.info("Uploaded <<local_papackage_uri:%s>>" % pypackage_uri)

        # push script for installing the local pypackage to S3
        local_uri = self.bootstrap_base.file_append(SH_LOCAL_PYPACKAGE)
        install_pypackage = INSTALL_PYPACKAGE.format(
            name=pypackage_name, path=pypackage_uri.uri)
        self.s3mgr.put_content(
            target_uri=local_uri, content=install_pypackage)
        log.info("Uploaded <<install_local_uri:%s>>" % local_uri.uri)

        ret = {
            "Name": "Install package from pypi",
            "ScriptBootstrapAction": {
                "Path": local_uri.uri,
                "Args": []
            }
        }
        return ret

    def bootstrap(self, package):
        python_action = self._python_action()

        if package.startswith("pip+"):
            pkg_action = self._pypi_action(package)
        else:
            pkg_action = self._local_pypackage_action(package)

        return [python_action, pkg_action]
