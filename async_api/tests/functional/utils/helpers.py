import gzip
import pickle


def extract_obj(compressed_data):
    pickled_data = gzip.decompress(compressed_data)
    obj = pickle.loads(pickled_data)
    return obj