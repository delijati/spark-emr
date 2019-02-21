import sys
import loguru
import argparse

import spark_emr.manager

from spark_emr.util import load_config
from spark_emr.const import CONFIG_DIR, NAMESPACE

log = loguru.logger


def base_parser(parser):
    parser.add_argument(
        "--config",
        help="the path of the config yaml default (%s)" % CONFIG_DIR,
        default=CONFIG_DIR)
    return parser


def base_parser_start(parser):
    parser = base_parser(parser)
    parser.add_argument("--name", help="Cluster name", required=True)
    parser.add_argument("--tags", help="Tags", nargs="*")
    parser.add_argument(
        "--cmdline", help="The command line to run the model", required=True)
    parser.add_argument(
        "--package",
        help="A package path or name on for pip",
        required=True)
    parser.add_argument("--poll", dest="poll", action="store_true")
    parser.add_argument("--no-poll", dest="poll", action="store_false")
    parser.set_defaults(poll=True)

    parser.add_argument("--yarn-log", dest="yarn_log", action="store_true")
    parser.add_argument("--no-yarn-log", dest="yarn_log", action="store_false")
    parser.set_defaults(yarn_log=False)


def get_func_list(parser):
    parser = base_parser(parser)
    parser.add_argument("--namespace",
                        help="Cluster namespace",
                        required=False,
                        default=NAMESPACE)
    return _list


def _list(param):
    config = load_config(param.config)
    print("id, name, reason, state, created")
    for x in spark_emr.manager.list(param.namespace, config["region"]):
        line = ", ".join(
            [x["Id"],
             x["Name"],
             x["Status"].get("StateChangeReason", {})["Code"],
             x["Status"]["State"],
             str(x["Status"]["Timeline"]["CreationDateTime"])])
        print(line)


def get_func_stop(parser):
    parser = base_parser(parser)
    parser.add_argument("--cluster-id", help="Cluster id", required=True)
    return _stop


def _stop(param):
    config = load_config(param.config)
    spark_emr.manager.stop([param.cluster_id], config["region"])


def get_func_status(parser):
    parser = base_parser(parser)
    parser.add_argument("--cluster-id", help="Cluster id", required=True)
    return _status


def _status(param):
    config = load_config(param.config)
    ret = spark_emr.manager.status(param.cluster_id, config["region"])
    print(ret)


def get_func_start(parser):
    parser = base_parser_start(parser)
    return _start


def _start(param):
    config = load_config(param.config)
    emr_mgr = spark_emr.manager.EmrManager(config)

    emr_mgr.start(
        param.name,
        param.cmdline,
        param.package,
        param.tags,
        param.poll,
        param.yarn_log
    )


def main(args=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="available commands", dest="mode")

    parser_start = subparsers.add_parser("start")
    parser_status = subparsers.add_parser("status")
    parser_list = subparsers.add_parser("list")
    parser_stop = subparsers.add_parser("stop")

    func_start = get_func_start(parser_start)
    func_status = get_func_status(parser_status)
    func_lists = get_func_list(parser_list)
    func_stop = get_func_stop(parser_stop)

    param = parser.parse_args(args)
    try:
        if param.mode == "status":
            func_status(param)
        elif param.mode == "list":
            func_lists(param)
        elif param.mode == "stop":
            func_stop(param)
        elif param.mode == "start":
            param.tags = dict(zip(param.tags[::2], param.tags[1::2]))
            func_start(param)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print("ERROR: %s\n" % "".join(e.args))
        log.exception(e)
        parser_start.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
