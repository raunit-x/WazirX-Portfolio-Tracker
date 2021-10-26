import pickle
import os


def save_to_pickle(payloads: dict, filename='payloads.pkl'):
    curr_dir = "/" + "/".join([f for f in __file__.split('/')[:-1] if f])
    with open(os.path.join(curr_dir, 'Previous Prices', filename), 'wb') as fp:
        pickle.dump(payloads, fp)  # , protocol=pickle.HIGHEST_PROTOCOL)


def load_from_pickle(filename='payloads.pkl') -> dict:
    curr_dir = "/" + "/".join([f for f in __file__.split('/')[:-1] if f])
    with open(os.path.join(curr_dir, 'Previous Prices', filename), 'rb') as f:
        return pickle.load(f)
