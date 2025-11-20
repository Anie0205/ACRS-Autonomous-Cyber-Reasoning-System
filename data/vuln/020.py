
import pickle
data = input("payload: ")
obj = pickle.loads(bytes(data, 'utf-8'))
