import threading
import pyaudio
import numpy as np

class AudioEngine(threading.Thread):
    def __init__(self, input_device=None, output_device=None, fs=44100, buffer_size=512):
        super(AudioEngine,self).__init__()
        self.input_device = input_device
        self.output_device = output_device
        self.fs = fs
        self.buffer_size = buffer_size
        self.is_playing = False
        self.is_running = True
        self.data = np.linspace(-1,1,buffer_size)
        self.sound_graph = None
        self.iter = 0
        
    def start(self):
        player = pyaudio.PyAudio()
        if self.input_device is None:
            self.input_device = player.get_default_input_device_info()['index']
        if self.output_device is None:
            self.output_device = player.get_default_output_device_info()['index']
            stream = player.open(format = pyaudio.paFloat32,
                                 channels=1,
                                 rate=self.fs, 
                                 output=True, 
                                 frames_per_buffer=self.buffer_size,
                                 input_device_index=self.input_device,
                                 output_device_index=self.output_device)
        while self.is_running:
            if self.is_playing:
                self.iter += 1
                if self.sound_graph is not None:
                    self.data = self.sound_graph.process()
                else:
                    self.data = np.zeros((self.buffer_size,))
                self.data = self.data.astype(np.float32)
                self.data = self.data.tobytes()
                stream.write(self.data)
                
    
    def set_input_device(self, device):
        self.input_device = device
        
    def set_output_device(self,device):
        self.output_device = device
        
    def stop(self):
        self.is_running = False
        
    def pause(self):
        self.is_playing = False
        
    def play(self):
        self.is_playing = True
        
    def set_graph(self,graph):
        self.sound_graph = graph