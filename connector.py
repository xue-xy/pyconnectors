PORT_IO_IN = 0
PORT_IO_OUT = 1


class Port:
    def __init__(self, _parent, _io, _name):
        assert isinstance(_parent, Connector)

        self.parent = _parent
        self.io = _io
        self.name = _name
        self.idleDurationClock = None

    def __str__(self):
        return self.name

class Node:
    def __init__(self, _parent, _name):
        assert isinstance(_parent, Connector)
        self.parent = _parent
        self.name = _name

    def __str__(self):
        return self.name


class Connection:
    def __init__(self):
        self.ref = None
        self.params = []
        self.connected = []

    def __str__(self):
        return "%s%s(%s)" % (
            str(self.ref),
            "" if self.params is None else ("<%s>" % ",".join(map(lambda p: str(p), self.params))),
            ",".join(map(lambda p:str(p), self.connected))
        )


class Connector:
    def __init__(self, _name):
        self.ports = []
        self.isChannel = False
        self.params = []
        self.nodes = []
        self.connections = []
        self.name = _name
        self.properties = {}
        self.resetClocks = {}

    def connect(self, *ports, params=None):
        assert len(ports) > 0
        assert len(ports) == len(self.ports)
        for i in range(len(ports)):
            assert ports[i].parent == ports[0].parent
            if not isinstance(ports[i], Node):
                assert ports[i].io == self.ports[i].io

        # if len(self.params) > 0:
        #     assert params is not None
        #     for paramname in self.params:
        #         assert paramname in params

        conn = Connection()
        conn.ref = self
        conn.connected += ports
        conn.params = params

        ports[0].parent.connections.append(conn)
        return self


    def getSemantics(self):
        pass

    def createInstance(self):
        pass

    def createPort(self, io, name):
        p = Port(self, io, "P" + name)
        for existing_port in self.ports:
            if p.name == existing_port.name:
                raise KeyError("cannot create two ports with the same name %s" % p.name)
        self.ports.append(p)
        return p

    def createPorts(self, io, *names):
        return (self.createPort(io, name) for name in names)

    def createNode(self):
        n = Node(self, "N%d" % len(self.nodes))
        self.nodes.append(n)
        return n

    def createNodes(self, numNodes):
        return (self.createNode() for _ in range(numNodes))

    def setTypeChannel(self):
        self.isChannel = True

    def setTypeConnector(self):
        self.isChannel = False

    def createParam(self, paramName):
        self.params.append(paramName)
        pass

    def createResetClockAt(self, name, *ports):
        for presentclk in self.resetClocks:
            assert presentclk.name != name
        for p in ports:
            assert p in self.ports

        from semantics.STAr.expression import Variable
        clk = Variable(name=name)
        clk.isClock = True
        self.resetClocks[clk] = ports
        return clk

    def __str__(self):
        return self.name

    def addProperty(self, name, prop):
        assert name not in self.properties
        self.properties[name] = prop