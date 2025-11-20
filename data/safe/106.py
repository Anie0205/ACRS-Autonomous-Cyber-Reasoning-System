
import pickle
safe = {"a": 1}
data = pickle.dumps(safe)
obj = pickle.loads(data)
