import base64

class UsersHandler:
    def __init__(self, database):
        self.db = database
        self.users = database.users
        
    #attempt to login with a given username and password
    def login(self, username, password):
        try:
            user = self.users.find_one({"username":username})
        except:
            print "Error when attempting to retrieve username", username, "from the database."
            return None
        
        if user is None:
            print username, "doesn't exist in the database."
            return None
        
        #decrypt password from database and see if it is a match
        if password == base64.b64decode(user["password"]):
            print "Succsefully logged in user", username
            return user
        else:
            print "Password provided for user", username, "does not match"
            return None
        
    
    #attepmt to create a new account
    def createAccount(self, username, password, email):
        #not actually effective, but "password encoding goes here"
        password = base64.b64encode(password)
        
        #make the newUser object, email is optional
        if email != "":
            newUser = {"username": username, "password":password, "email":email}
        else:
            newUser = {"username": username, "password":password}
        
        print "Attempting to create new user with username", username
        try:
            self.users.insert_one(newUser)
        except:
            print "Error when attempting to add new user with username", username, "to the database."
            return False
        
        print "Successfully created new user", username, "!"
        return True