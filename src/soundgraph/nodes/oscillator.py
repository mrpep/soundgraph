import numpy as np
from soundgraph.graph import SoundNode

class Oscillator(SoundNode):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.state = dict(frequency=440,
                          phase=None,
                          initial_phase=0,
                          amplitude=1,
                          offset=0,
                          osc_type='sin',
                          sr=44100,
                          buffer_size=512)
        
        self.min_phase = 0
        self.max_phase = 2*np.pi

    def get_phase_increment(self, steps):
        return np.ones(steps)*2*np.pi*self.state['frequency']/self.state['sr']
        
    def process(self):
        self.state['phase'] = self.state['initial_phase'] + np.cumsum(self.get_phase_increment(self.state['buffer_size']))
        if self.max_phase:
            self.state['phase'] = self.state['phase'] % (self.max_phase - self.min_phase)
        self.state['phase'] += self.min_phase
        self.state['initial_phase'] = self.state['phase'][-1]
        
        if self.state['osc_type'] == 'sin':    
            output = self.state['offset'] + self.state['amplitude']*np.sin(self.state['phase'])
        elif self.state['osc_type'] == 'saw':
            output = self.state['offset'] + self.state['amplitude']*(1.0 - (self.state['phase']/np.pi))
        elif self.state['osc_type'] == 'square':
            output = self.state['offset'] + self.state['amplitude']*(1-2.0*(self.state['phase']<np.pi))
        elif self.state['osc_type'] == 'triangular':
            output = self.state['offset'] + self.state['amplitude']*(1.0 - 2.0*np.abs(self.state['phase']/np.pi - 1.0))
        
        return output