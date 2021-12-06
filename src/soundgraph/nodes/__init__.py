from soundgraph.graph import SoundNode
import soundfile as sf
import librosa
import numpy as np

from .oscillator import *

class AudioReader(SoundNode):
    def __init__(self, filename, buffer_size=512, name=None):
        super().__init__(name)
        self.state = dict(filename = filename,
                          buffer_size = buffer_size,
                          position = 0,
                          last_filename = filename)
        
        self.file_object = sf.SoundFile(self.state['filename'],'r+')
        
    def process(self):
        if self.state['filename'] != self.state['last_filename']:
            self.file_object = sf.SoundFile(self.state['filename'],'r+')
            self.state['last_filename'] = self.state['filename']
            self.state['position'] = 0
        
        return self.file_object.read(self.state['buffer_size'])

class Sampler(SoundNode):
    def __init__(self, name):
        super().__init__(name)
        self.state = dict(
            samples = {},
            bpm = 120,
            sr = 44100,
            beat = None,
            position = 0,
            sample_position = {},
            bars = 4,
            divisions_per_bar = 4,
            loop = True,
            buffer_size=512)
        
    def update_sample(self, name, filename):
        x,fs = librosa.core.load(filename,sr=self.state['sr'])
        if name not in self.state['sample_position']:
            self.state['sample_position'][name] = -1
        self.state['samples'][name] = x
        
    def process(self):
        samples_per_beat = int(self.state['bars']*self.state['sr']*60/self.state['bpm'])
        total_notes = self.state['bars']*self.state['divisions_per_bar']
        samples_per_note = int(self.state['sr']*60/(self.state['bpm']*self.state['divisions_per_bar']))
        
        out = np.zeros((self.state['buffer_size'],))
        
        #trigger notes
        actual_note = self.state['position']//samples_per_note
        #print('Position: {}, Note: {}'.format(self.state['position'],actual_note))
        if ((self.state['position']//samples_per_note) != (self.state['position'] + self.state['buffer_size'])//samples_per_note) or (self.state['position']%samples_per_note == 0):
            if self.state['position']%samples_per_note != 0:
                actual_note += 1
            trigger_position = actual_note*samples_per_note - self.state['position']
            #print('Triggering note {} at position {}'.format(actual_note, trigger_position))
            
            for k,v in self.state['samples'].items():
                if self.state['beat'][k][actual_note%total_notes] == 1:
                    sample_pos = self.state['buffer_size'] - trigger_position
                    out[trigger_position:] += v[:sample_pos]
                    self.state['sample_position'][k] = sample_pos
        
        #continue triggered notes
        for k,v in self.state['sample_position'].items():
            if v>=0:
                sample_i = self.state['samples'][k][v:v+self.state['buffer_size']]
                out[:sample_i.shape[0]] += sample_i
                end_pos = v + self.state['buffer_size']
                if end_pos > self.state['samples'][k].shape[0]:
                    end_pos = -1
                self.state['sample_position'][k] = end_pos
                
        #Update position:
        self.state['position'] += self.state['buffer_size']
        if self.state['position'] > samples_per_beat:
            self.state['position'] -= samples_per_beat
            
        return np.tanh(out)

class Mixer(SoundNode):
    def __init__(self,name=None):
        super().__init__(name)
        
    def process(self):
        out = 0
        for k,v in self.state.items():
            if k.startswith('in'):
                out += self.state[k]*self.state['volume_{}'.format(k.split('in_')[-1])]
        return out

class Scaler(SoundNode):
    def __init__(self, name=None):
        super().__init__(name)
        self.state = dict(scale = 1,
                          input = None)

    def process(self):
        return self.state['input']*self.state['scale']
