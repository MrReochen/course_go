from model import load_latest_model, load_best_model
from keras import backend as K
from evaluator import evaluate
import tensorflow as tf
from conf import conf
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
K.set_session(tf.Session(config=config))

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        time.sleep(30)
        model = load_latest_model()
        best_model = load_best_model()
        evaluate(best_model, model)
        K.clear_session()


def main():
    
    
    model = load_latest_model()
    best_model = load_best_model()
    evaluate(best_model, model)
    K.clear_session()
    
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.join(conf['MODEL_DIR']), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()



if __name__ == "__main__":
    main()
