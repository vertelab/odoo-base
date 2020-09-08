# Class that interfaces with Odoo
class odoointf(object):
    # Makes instance of class able to act as function to call method by name
    def __call__(self, method, key):
        return self.indirect(method, key)

    # Method calls another method by name.
    def indirect(self, method_name, key):
        method_name = str(method_name).lower()
        method_to_call = getattr(self, method_name, None)

        if not method_to_call or not callable(method_to_call):
            print("Method '{0}' not found".format(method_name))
            return None

        return method_to_call(key)

    # Methods based on categories from message
    # All methods needs to have the same parameters of the same types and the same return type
    # For now, just logging the call
    # TODO: actually call Odoo for each message type
    def nyttpnr(self, key):
        print("Nytt personnummer: ", key)
        return True

    def flyttat(self, key):
        print("Flyttat: ", key)
        return True

    def xyz(self, key):
        print("xyz: ", key)
        return False

