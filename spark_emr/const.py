import os

home = os.path.expanduser("~")

CONFIG_DIR = os.path.join(home, ".config", "spark-emr.yaml")
NAMESPACE = "spark_emr"

SH_INSTALL_PYTHON = "install_python.sh"
SH_YARN_LOG = "yarn_log.sh"
SH_PYPI_PYPACKAGE = "install_pypi_pypackage.sh"
SH_LOCAL_PYPACKAGE = "install_local_pypackage.sh"
PYTHON_VERSION = {"python35": "3.5", "python36": "3.6"}
