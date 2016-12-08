import json
from threading import Thread


class Connection:
    """ This class represents an SSH connection to a remote server.
        It can be used to run c
    """

    def __init__(self, ip, username=None, conBuilder=None):
        if conBuilder is None:
            self.conBuilder = Connection.connection_builder
        else:
            self.conBuilder = conBuilder
        self.ip = ip
        self.username = username
        self.ssh = None
        self.online = None
        self.error = None
        self.errorTrace = None
        id = str(ip).replace(".", "_")
        self.log = logging.getLogger(id+".connection")

    def connect(self, timeout=5):
        info, self.ssh = self.conBuilder.\
            getConnectionSafe(self.ip, self.username)

        self.online = info["online"]
        self.error = info["error"]
        self.errorTrace = info["errorTrace"]
        self.ip = info["ip"]
        self.dns = info["dns"]
        self.stderr = None
        self.stdout = None
        self.log.info("connection result: "+json.dumps(info))

        return self.online and self.error is None

    def testOS(self):
        # TODO: Test it!
        cmd = "cat /etc/issue"
        os_names = ["Linux", "Ubuntu", "Debian", "Fedora", "Red Hat", "CentOS"]
        result = {}

        try:
            outp, err = self.runCommand(cmd)
        except Exception:
            error_lines = traceback.format_exc().splitlines()
            result["error"] = error_lines[-1]
            return result

        if len(err) > 0:
            result["error"] = err
            return result

        result["outp"] = outp

        # Check for official distribution name in output
        if any([os_name.lower() in result["os"].lower()
                for os_name in os_names]):
            result["os"] = outp.split("\n")[0]

        return result

    def endCommand(self):

        self.disconnect()

        if self.stderr is not None and len(self.stderr) > 0:
            self.error = "RuntimeError"
            self.errorTrace = self.stderr

    def startCommand(self, script, timeout=None):
        if timeout is None:
            timeout = 1000*60*60*24  # one day

        if self.ssh is None:
            raise RuntimeWarning("Connection not alive!")

        def run(self):
            self.running = True
            self.ended = False
            self.startTime = time.time()
            try:
                self.stdout, self.stderr = \
                    self.runCommand(script, timeout=timeout)
            except Exception:
                self.errorTrace = traceback.format_exc()
                self.error = "ErrorExecutingRemoteCommand:"+\
                    self.errorTrace.splitlines()[-1]
            else:
                self.endTime = time.time()
                if "timeout: timed out" in self.stderr:
                    self.error = "SSH connection timeout. duration: %d" % (self.endTime - self.startTime)
            self.endTime = time.time()
            self.running = False
            self.ended = True

        self.thread = Thread(target=run, args=(self, ))

        self.thread.start()

    def runCommand(self, command, timeout=5):
        if self.ssh is None:
            raise RuntimeWarning("Connection not alive!")

        stdin, stdout, stderr = self.ssh.exec_command(command,
                                                      timeout=timeout,
                                                      get_pty=True)

        output = stdout.read()
        errors = stderr.read()
        return output, errors

    def disconnect(self):
        if self.ssh is not None:
            self.ssh.close()
        self.ssh = None
