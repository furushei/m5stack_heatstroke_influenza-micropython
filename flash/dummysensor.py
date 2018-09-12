import urandom

class DummySensor:
    def __init__(self, temperature=None, humidity=None):
        self._temperature = temperature
        self._humidity = humidity

    def measure(self):
        pass
    
    def temperature(self):
        return self._temperature
    
    def humidity(self):
        return self._humidity

class RandomSensor:
    def __init__(self, temperature_range=(10, 50), humidity_range=(20, 100)):
        self._temperature_range = temperature_range
        self._humidity_range = humidity_range
        self._temperature = None
        self._humidity = None
    
    def measure(self):
        self._temperature = urandom.uniform(*self._temperature_range)
        self._humidity = urandom.uniform(*self._humidity_range)
    
    def temperature(self):
        return self._temperature
    
    def humidity(self):
        return self._humidity
