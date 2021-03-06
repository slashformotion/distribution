import pathlib as pl
import Logger
import time
import Config
import Event_Handler
import time
import shutil
from watchdog.observers import Observer 

config_folder = pl.Path("..") / pl.Path("configs")
config_classic = config_folder / pl.Path("Configuration_Classic.json")
origin = pl.Path("..") / pl.Path("TEST") / pl.Path("origin")
print(origin.resolve())
destination = pl.Path("..") / pl.Path("TEST") / pl.Path("destination")

class Trieur():
    def __init__(self, config = config_classic, origin = origin, destination = destination):
        self.logger = Logger.Logger()
        self.observer = Observer()
        self.config = Config.Config(config)
        self.origin = origin
        self.destination = destination
        self._running = False
        Event_Handler.Handler.patterns = self.config.get_patterns()
        self.handler = Event_Handler.Handler()
        self.watch = None


    @property
    def running(self):
        return self.running

 

    def start(self):
       #check destination and origin
        if not self.origin.exists() or not self.origin.is_dir() or not self.destination.exists() or not self.destination.is_dir() :
            return False
            print("EROOR")

        #update of the patterns and process
        self.handler.set_process(config = self.config, logger = self.logger, destination = self.destination)
        self.watch = self.observer.schedule(self.handler, str(origin.resolve()))
        self.config.deploy(self.destination)

        #start observer
        self.observer.start()

        self.logger.debug("Distribution started")

    def stop(self):
        self.observer.stop()
        self.handler.unset_process()
        self.observer.join()
        self.observer.unschedule_all()
        self.logger.debug("Distribution stopped")

    
    def move(self,event):
        old_path = pl.Path(event.src_path)
        new_path = self.destination / self.config.build_file_path(event, self.logger)
        try:
            assert not new_path.exists(), f"New path for file ({old_path.name}) already exist"
        except AssertionError as error:
            self.logger.warning(error)
        else :
            shutil.move(old_path,new_path) 
    




if __name__ == "__main__":
    trieur = Trieur()
    trieur.start()
    try:
        while 1:
            time.sleep(0.0001)
    except KeyboardInterrupt:
        trieur.stop()