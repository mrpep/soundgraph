class SoundNode:
    def __init__(self, name):
        self.state = {}
        self.parents = []
        self.children = []
        self.name = name
        self.output_names = ['out']
    
    def update(self, property_name, property_value):
        self.state[property_name] = property_value
        
    def get_parents(self):
        return self.parents
        
    def get_children(self):
        return self.children
    
    def get_output_names(self):
        return self.output_names

class SoundGraph(SoundNode):
    def __init__(self):
        self.nodes = {}
        self.connections = []
    
    def add(self,node):
        self.nodes[node.name] = node
        
    def connect(self, from_node, to_node):
        self.connections = [conn for conn in self.connections if conn[1] != to_node] #Remove existing connections to to_node
        self.connections.append((from_node,to_node)) #Add new connection
            
    def disconnect(self, from_node, to_node):
        for conn in self.connections:
            if conn == (from_node,to_node):
                self.connections.remove(conn)
    
    def _find_root_nodes(self):
        nodes_with_parent = [conn[1].split('.')[0] for conn in self.connections if '.' in conn]
        return [node for node in self.nodes if node not in nodes_with_parent]
            
    def _find_parents(self,node):
        return {conn[0]: conn[1] for conn in self.connections if conn[1].split('.')[0] == node.name}
    
    def set_output(self,node_name):
        self.output = node_name
        
    def process(self):
        to_do_tasks = [node_name for node_name in self.nodes]
        done_tasks = []
        tasks_io = {}
        while len(to_do_tasks) > 0:
            for task_name in to_do_tasks:
                task = self.nodes[task_name]
                parents = self._find_parents(task)
                non_available_parents = [par for par in parents if par.split('.')[0] not in done_tasks]
                if len(non_available_parents) == 0:
                    out_names = task.get_output_names()
                    for io_name, io in tasks_io.items():
                        if io_name in parents:
                            task.update(parents[io_name].split('.')[-1],io)
                    outs = task.process()
                    if len(out_names) > 1:
                        for i, out_name in enumerate(out_names):
                            tasks_io['{}.{}'.format(task.name,out_name)] = outs[i]
                    else:
                        tasks_io['{}.{}'.format(task.name,out_names[0])] = outs
                    done_tasks.append(task.name)
                    to_do_tasks.remove(task.name)
        

        return tasks_io[self.output]