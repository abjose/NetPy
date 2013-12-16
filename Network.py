

class Network:
    def __init__(self):
        self.nodes = set()

    def step(self):
        for n in self.nodes:
            n.send()
    
    def add_node(self, n):
        self.nodes |= {n}

    def connect(self, n1,n2):
        self.nodes |= {n1,n2}
        a.add_neighbor(n1)
        b.add_neighbor(n2) 

class Node:
    # maybe assume links
    def __init__(self, name, host=False, ack_timeout=10):
        self.name = name
        self.neighbors = set()
        self.host = host
        self.ack_timeout = ack_timeout
        self.routing = dict()
        self.unack_queue = []
        self.curr_queue  = []
        self.next_queue  = []

    def receive(self, m):
        if self.host and m.dest == self.name:
            if not m.ack:
                print self.name,"recieved message as dest, sending ack!"
                ack = Message(m.uid, m.dest, m.src, ack=True)
                self.next_queue.append(ack)
            else:
                print self.name,"recieved ack as dest!"
                self.unack_queue = [(m2,t) for m2,t in self.unack_queue 
                                    if m2.uid!=m.uid]
        else:
            print self.name,"recieved message as router!"
            self.next_queue.append(m)

    def send(self):
        # send message to some adjacent target
        if self.curr_queue != []:
            m = self.curr_queue.pop(0) # eww
            if self.host and not m.ack:
                self.unack_queue.append((m,0))
            print self.name,"transmitting message on way to",m.dest
            self.routing[m.dest].receive(m)
        if self.host:
            new_queue = []
            for m,t in self.unack_queue:
                if t >= self.ack_timeout:
                    new_queue.append((m,0))
                    self.next_queue.append(m)
                    print 'Ack timeout! Retransmitting message to',m.dest
                else:
                    print 'Incrementing away time for message to',m.dest
                    new_queue.append((m,t+1))
            self.unack_queue = new_queue[:]
        self.curr_queue += self.next_queue
        self.next_queue = []

    def add_neighbor(self, node):
        self.neighbors |= {node}


class Message:
    def __init__(self, uid, src, dest, ack=False):
        self.uid  = uid
        self.src  = src
        self.dest = dest
        self.ack  = ack




if __name__=='__main__':
    N = Network()
    a = Node("node1", host=True)
    b = Node("node2")
    c = Node("node3", host=True)
    N.connect(a,b)    
    N.connect(b,c)
    a.routing[c.name] = b
    b.routing[c.name] = c
    b.routing[a.name] = a
    c.routing[a.name] = b
    
    # probably easier if figure out routing...

    m1 = Message("msg1", "node1", "node3")
    a.receive(m1)


    for i in range(100):
        raw_input()
        print "step",i+1
        N.step()
