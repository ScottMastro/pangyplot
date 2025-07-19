import pickle

def load_pickle(pickle_path):
    with open(pickle_path, 'rb') as f:
        return pickle.load(f)
    
def dump_pickle(object, pickle_path):
    with open(pickle_path, 'wb') as f:
        pickle.dump(object, f)
