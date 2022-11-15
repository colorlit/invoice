gl_var = "Global Variable"

class TestFlight:
    cl_var = "Class Variable"
    def __init__(self):
        self.se_var = "Instance Variable"
        self.se_id = 0

    def __del__(self):
        pass
    def set_id(self, sid):
        self.se_id = sid
    def make_ivar(self, uin):
        self.newinput = uin
    def display_id(self):
        print(self.se_id)
    def display_ivar(self):
        print(self.newinput)
    def alter_ivar(self, newinput):
        print("Current self.newinput :")
        print(self.newinput)
        print(type(self.newinput))
        self.newinput = newinput
        print("New self.newinput :")
        print(self.newinput)
        print(type(self.newinput))
    def access_var(self):
        print(gl_var)
        print(TestFlight.cl_var)
        print(self.se_var)
        if(1):
            print("TRUE STATEMENT")
        if(0):
            print("FALSE STATEMENT")
        
        
tf1 = TestFlight()
tf2 = TestFlight()
tf1.set_id(3)
tf1.display_id()
TestFlight.display_id(tf2)
tf1.access_var()
tf2.make_ivar("MSG")
tf2.display_ivar()
tf2.alter_ivar(231.124)