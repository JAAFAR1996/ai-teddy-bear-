# Observer pattern implementation
class Observer:
    def update(self, data):
        raise NotImplementedError

class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data) 