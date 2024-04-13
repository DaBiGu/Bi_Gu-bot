
class Steam_Data:
    def __init__(self):
        self.data = {"157563170":
                        {"76561198446560670": None, #zjh
                         "76561199115642793": None, #me
                        },
                     "858019358":
                        {"76561198893281622": None, #wj
                         "76561199115642793": None, #me
                         "76561198320837457": None, #yusudaye
                        },
                    }
    def get_data(self):
        return self.data
    
    def set_data(self, data):
        self.data = data