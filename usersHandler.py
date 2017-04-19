import base64

class UsersHandler:
    def __init__(self, database):
        self.db = database
        self.users = database.users
        
    def checkExistence(self, username):
        try:
            user = self.users.find_one({"username":username})
        except:
            print "An unknown error occurred when attempting to check for user's existence"
            return False
        
        return user is not None
        
    #attempt to login with a given username and password
    def login(self, username, password):
        user = {"object":None, "errors":None}
        try:
            user["object"] = self.users.find_one({"username":username})
        except:
            print "An unknown error occurred when attempting to login"
            user["errors"] = {"unknown_error":"an unknown error has occurred."}
            return user
        
        if user["object"] is None:
            print username, "doesn't exist in the database."
            user["errors"] = {"username_error":"that username doesn't exist."}
            return user
        
        #decrypt password from database and see if it is a match
        if password == base64.b64decode(user["object"]["password"]):
            print "Succsefully logged in user", username
            return user
        else:
            print "Password provided for user", username, "does not match"
            user["errors"] = {"password_error":"incorrect password."}
            return user
        
    
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
        except pymongo.errors.DuplicateKeyError:
            print username, "already exists in the database"
            return False
        except:
            print "Error when attempting to add new user with username", username, "to the database."
            return False
        
        print "Successfully created new user", username, "!"
        return True