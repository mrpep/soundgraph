from soundgraph.graph import SoundNode
import mido

class MidiInput(SoundNode):
    def __init__(self,name):
        super().__init__(name=name)
        self.state = dict(port=None,
                          last_port=None)
        self.inport = None
        
    def process(self):
        if self.state['port'] != self.state['last_port']:
            self.state['last_port'] = self.state['port']
            self.inport = mido.open_input(self.state['port'])
        
        return [msg for msg in self.inport.iter_pending()]
            
class MidiMapper(SoundNode):
    def __init__(self, name):
        super().__init__(name=name)
        self.state = dict(midi_in=None,
                          mapping=None,
                          keep_last_state=True,
                          last_state=100)
        
    def filter_msg(self,msg):
        if msg is not None:
            matches = True
            for k, v in self.state['mapping'].items():
                if k not in ['map_parameter','mapping','last_state']:
                    if hasattr(msg,k) and getattr(msg,k) == v:
                        pass
                    else:
                        matches = False
            return matches
        else:
            return False
                
    def process(self):
        filtered_msgs = [msg for msg in self.state['midi_in'] if self.filter_msg(msg)]
        if len(filtered_msgs) > 0:
            last_msg = filtered_msgs[-1]
            if hasattr(last_msg,self.state['mapping']['map_parameter']):
                val = self.state['mapping']['mapping'][int(last_msg.value)]
                self.state['last_state'] = val
            else:
                val = self.state['last_state']
            return val

        else:
            return self.state['last_state']