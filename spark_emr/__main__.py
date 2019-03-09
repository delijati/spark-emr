import sys
import loguru
import argparse

import spark_emr.manager

from spark_emr.util import load_config
from spark_emr.const import CONFIG_DIR
from spark_emr.spot import spot_price

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
    parser.add_argument("--tags", help="Tags", nargs="*", default=[])
    parser.add_argument(
        "--cmdline", help="The command line to run the model", required=True)
    parser.add_argument(
        "--package",
        help="A package path or name on for pip",
        required=True)
    parser.add_argument("--bid-master", dest="bid_master", type=float)
    parser.add_argument("--bid-core", dest="bid_core", type=float)
    parser.add_argument("--poll", dest="poll", action="store_true")
    parser.add_argument("--no-poll", dest="poll", action="store_false")
    parser.set_defaults(poll=True)

    parser.add_argument("--yarn-log", dest="yarn_log", action="store_true")
    parser.add_argument("--no-yarn-log", dest="yarn_log", action="store_false")
    parser.set_defaults(yarn_log=False)


def get_func_list(parser):
    parser = base_parser(parser)
    parser.add_argument("--filter",
                        help="Filter cluster by tag",
                        nargs="*",
                        default=[])
    return _list


def _list(param):
    config = load_config(param.config)
    print("id, name, reason, state, created, tags")
    for x in spark_emr.manager.list(param.filter, config["region"]):
        line = ", ".join(
            [x["Id"],
             x["Name"],
             x["Status"].get("StateChangeReason", {}).get("Code", ""),
             x["Status"]["State"],
             str(x["Status"].get("Timeline", {}).get("CreationDateTime", "")),
             str(x["TagsClean"])
             ])
        print(line)


def _spot(param):
    config = load_config(param.config)
    inst = list(set([config["master"]["instance_type"],
                     config["core"]["instance_type"]]))
    print("Instance: %s" % inst)
    ret = spot_price(inst)

    for inst_type, region, price, ondemand in ret:
        start = ""
        end = ""
        if config["region"] in region:
            start = "\033[92m"
            end = "\033[0;0m"
        print(
            "%s[%s] region: %s spot ec2 spot price: %.4f$ ec2 ondemand: %s$%s" %
            (start, inst_type, region, float(price), ondemand, end))


def get_func_spot(parser):
    parser = base_parser(parser)
    return _spot


def get_func_stop(parser):
    parser = base_parser(parser)
    parser.add_argument("--cluster-id", help="Cluster id", required=True)
    return _stop


def _stop(param):
    config = load_config(param.config)
    print(spark_emr.manager.stop([param.cluster_id], config["region"]))


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
        param.yarn_log,
        param.bid_master,
        param.bid_core
    )


def main(args=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="available commands", dest="mode")

    parser_spot = subparsers.add_parser("spot")
    parser_start = subparsers.add_parser("start")
    parser_status = subparsers.add_parser("status")
    parser_list = subparsers.add_parser("list")
    parser_stop = subparsers.add_parser("stop")

    func_spot = get_func_spot(parser_spot)
    func_start = get_func_start(parser_start)
    func_status = get_func_status(parser_status)
    func_lists = get_func_list(parser_list)
    func_stop = get_func_stop(parser_stop)

    param = parser.parse_args(args)
    try:
        if param.mode == "status":
            func_status(param)
        elif param.mode == "list":
            param.filter = dict(zip(param.filter[::2], param.filter[1::2]))
            func_lists(param)
        elif param.mode == "stop":
            func_stop(param)
        elif param.mode == "start":
            param.tags = dict(zip(param.tags[::2], param.tags[1::2]))
            func_start(param)
        elif param.mode == "spot":
            func_spot(param)
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
