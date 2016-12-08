import json
import time
import logging
import lib
import traceback
import sys, socket
from collections import Counter
from lib import utils

if len(sys.argv) != 5:
        print "Usage: ./scan.py <ttl1> <ttl2> <ip> <filename>"
        exit(1);

param_ttl1 = str(int(sys.argv[1]))
param_ttl2 = str(int(sys.argv[2]))
param_ip = sys.argv[3]
param_filename = sys.argv[4]

rsa_file = 'ssh_needs/id_rsa'
known_hosts_file = 'ssh_needs/known_hosts'
slice_name = 'budapestple_cloud'
used_threads = 25

fileh = open(param_filename, "w")

logger = logging.getLogger()

node_len = 0


def main():
    logging.basicConfig(level=logging.NOTSET)
    lib.set_ssh_data(slice_name, rsa_file, known_hosts_file)

    def stdout_proc(node):
        stdout = node["stdout"]
        if "ping statistics" in stdout:
            to_print = "OK %s %s" % (socket.gethostbyname(node["ip"]), node["ip"])
	    print to_print
	    fileh.write(to_print + "\n");

    args = {
        "cmd": "ping -c 2 -t " + param_ttl1 + " " + param_ip + "; ping -c 2 -t " + param_ttl2 + " " + param_ip,
        "save_result": False,
        "do_statistics": True,
        "stdout_proc": stdout_proc
    }
    # nodes=None, cmd=None, stdout_proc=None, stderr_proc=None,
    #  timeout=10, save_erroneous=True,
    #  save_stdout=True, save_stderr=True,
    #  node_script=scan_script, save_result=True

    start = time.time()
    print "scan started at: ", start
    scan(**args)
    end = time.time()
    print "scan ended at: ", end
    print 'scan duration: %.2f seconds' % (end - start)
    fileh.close()


def scan_script(args):
    global node_len
    node_len -= 1

    ip = args["ip"]
    cmd = "cat /etc/issue"
    timeout = 10

    if "cmd" in args and args["cmd"] is not None:
        cmd = args["cmd"]
    if "timeout" in args and args["timeout"] is not None:
        timeout = args["timeout"]

    log = logging.getLogger("scan."+str(ip).replace(".","_")).info
    node = {"ip": ip}
    logging.getLogger("scan").fatal("nodes to do: %d", node_len)

    log("connect to: "+ ip)
    con = lib.Connection(node["ip"])
    con.connect()

    node["online"] = con.online

    if con.error is not None:
        node["error"] = con.errorTrace.splitlines()[-1]
        node["stderr"] = con.errorTrace
        log("connection error: "+ ip+ " --: "+ node["error"])
        return node

    log("connection succesfull: " + ip)
    try:
        node["time"] = time.time()
        outp, err = con.runCommand(cmd, timeout=timeout)
    except Exception:
        stderr = traceback.format_exc()
        node["error"] = "connection error: "+stderr.splitlines()[-1]
        node["stderr"] = stderr
        return node

    if len(err) > 0:
        node["error"] = "runtime error: "+str(err).splitlines()[-1]
        node["stderr"] = str(err)
        return node

    node["stdout"] = str(outp)

    return node


def scan_statistics(nodes, do_log=True, handle_stderr=False):
    log = logging.getLogger("statistics").info
    if do_log:
        log("create statistics")
    errors = Counter()
    outputs = Counter()
    error_types = Counter()
    offline = 0
    online = 0
    error = 0
    succeed = 0

    for node in nodes:
        if not node["online"]:
            offline += 1
            continue
        online += 1
        if "error" in node and node["error"] != "offline":
            error_types[node["error"]] += 1
            error += 1
            if handle_stderr and "stderr" in node:
                errors[node["stderr"]] += 1

        else:
            outputs[node["stdout"]] += 1
            succeed += 1

    errors = errors.most_common(len(errors))
    outputs = outputs.most_common(len(outputs))
    error_types = error_types.most_common(len(error_types))

    if do_log:
        log("Online count:  %d", online)
        log("Offline count: %d", offline)
        log("Erroneous count:   %d", error)
        log("Succeed count: %d", succeed)

        log("\nOutputs:")
        for type, count in outputs:
            log("Output count:%d\n\t%s", count, type)

        log("\nError types:")
        for type, count in error_types:
            log("Error type count:%d\n\t%s", count, type)

        log("\nError outputs:")
        for type, count in errors:
            log("Error output count:%d\n\t%s", count, type)

    res = {
        "online": online,
        "offline": offline,
        "succeed": succeed,
        "erroneous": error,
        "outputs": [{
                        "count": count,
                        "stdout": type
                    } for type, count in outputs],
        "error_types": [{
                        "count": count,
                        "error": type
                    } for type, count in error_types]
    }

    if handle_stderr:
        res["errors"] = [{
                            "count": count,
                            "stderr": type
                        } for type, count in errors]

    return res


def scan(nodes=None, cmd=None, stdout_proc=None, stderr_proc=None,
         timeout=10, save_erroneous=True, do_statistics=True,
         save_stdout=True, save_stderr=True,
         node_script=scan_script, save_result=True):
    global node_len
    log = logging.getLogger().info
    logging.getLogger().setLevel(logging.ERROR)

    if nodes is None:
        log("get planet lab ip list")
        nodes = lib.getPlanetLabNodes(slice_name)
        # nodes = lib.getBestNodes()[:5]
    node_len = len(nodes)

    log("start scanning them ")
    node_calls = [{
                    "cmd": cmd,
                    "timeout": timeout,
                    "ip": ip
                  } for ip in nodes]

    def orchestrate(args):
        res = node_script(args)
        if stdout_proc is not None and "stdout" in res:
                res["data"] = stdout_proc(res)

        if stderr_proc is not None and\
            "error" in node and\
            res["error"] is not None:
                    res["error"] = stderr_proc(res)

        return res

    nodes = utils.thread_map(orchestrate,
                             node_calls, used_threads)

    log("filter not needed informations")
    if not save_erroneous:
        new_list = []
        for node in nodes:
            if "error" not in node and\
                    node["online"] == "online":
                new_list.append(node)
        nodes = new_list

    if not save_stderr:
        for node in nodes:
            node.pop("stderr", None)

    if not save_stdout:
        for node in nodes:
            node.pop("stdout", None)

    if save_result:
        log("write out the results")
        with open("results/scan.json", "w") as f:
            f.write(json.dumps(nodes))

    if do_statistics:
        log("calculate statistics")
        stats = scan_statistics(nodes)
        stats["ts"] = time.time()

        node_statistics = lib.get_collection("node_statistics")
        tmp = stats.copy()
        node_statistics.insert_one(tmp)
        print json.dumps(stats, indent=2)


if __name__ == '__main__':
    main()
