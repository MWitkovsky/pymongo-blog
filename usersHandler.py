import base64
import pymongo

class UsersHandler:
    def __init__(self, database):
        self.db = database
        self.users = database.users
        
    #attempt to login with a given username and password
    def login(self, username, password):
        user = {}
        #input sanitization
        if username == "":
            user["errors"] = {"username_error" : "Please enter a username"}
            
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
        
        if password == "":
            user["errors"] = {"password_error" : "Please enter a password"}
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
    def createAccount(self, username, password, verify, email):
        newUser = {}
        #input sanitization
        if username == "":
            newUser["errors"] = {"username_error" : "Please enter a username"}
        elif len(username) < 3:
            newUser["errors"] = {"username_error" : "Username must be at least 3 characters long"}
        if len(password) < 3:
            newUser["errors"] = {"password_error" : "Password must be at least 3 characters long"}
        elif password != verify:
            newUser["errors"] = {"password_error" : "Passwords do not match."}
                
        if newUser["errors"] is not None:
            return newUser
        
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