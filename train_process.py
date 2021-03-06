from model import create_initial_model, load_latest_model, load_best_model
from keras import backend as K
from conf import conf
from evaluator import evaluate
from train import train
from self_play import self_play
import tensorflow as tf
import os

def init_directories():
    try:
        os.mkdir(conf['MODEL_DIR'])
    except:
        pass
    try:
        os.mkdir(conf['LOG_DIR'])
    except:
        pass

def main():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    K.set_session(tf.Session(config=config))
    init_directories()


    while True:
        model = load_latest_model()
        best_model = load_best_model()
        evaluate(best_model, model)
        train(model, game_model_name=best_model.name)
        K.clear_session()

if __name__ == "__main__":
    main()
