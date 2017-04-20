import base64
import pymongo

class UsersHandler:
    def __init__(self, database):
        self.db = database
        self.users = database.users
        
    def checkExistence(self, username):
        try:
            user = self.users.find_one({"lowerUsername":username.lower()})
        except:
            print "An unknown error occurred when attempting to check for user's existence"
            return None
        if user is not None:
            return user["username"]
        else:
            return None
    
    #attempt to login with a given username and password
    def login(self, username, password):
        user = {"errors":None}
        #input sanitization
        if username == "":
            user["errors"] = {"username_error" : "Please enter a username"}
            
        try:
            user["object"] = self.users.find_one({"lowerUsername":username.lower()})
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
        else:
            print "Password provided for user", username, "does not match"
            user["errors"] = {"password_error":"incorrect password."}
        
        return user
        
    
    #attepmt to create a new account
    def createAccount(self, username, password, verify, email):
        newUser = {"errors":{}}
        #input sanitization
        if username == "":
            newUser["errors"].update({"username_error" : "Please enter a username"})
        elif len(username) < 3:
            newUser["errors"].update({"username_error" : "Username must be at least 3 characters long"})
        if len(password) < 3:
            newUser["errors"].update({"password_error" : "Password must be at least 3 characters long"})
        elif password != verify:
            newUser["errors"].update({"password_error" : "Passwords do not match."})
                
        if newUser["errors"]:
            return newUser
        
        #not actually effective, but "password encoding goes here"
        password = base64.b64encode(password)
        
        #make the newUser object, email is optional
        if email != "":
            newUser["object"] = {"lowerUsername": username.lower(), "username":username, "password":password, "email":email}
        else:
            newUser["object"] = {"lowerUsername": username.lower(), "username":username, "password":password}
        
        print "Attempting to create new user with username", username
        try:
            self.users.insert_one(newUser["object"])
        except pymongo.errors.DuplicateKeyError:
            print username, "already exists in the database"
            newUser["errors"] = {"username_error" : "Username already exists."}
            return newUser
        except:
            print "Error when attempting to add new user with username", username, "to the database."
            newUser["errors"] = {"username_error" : "Unknown database error."}
            return newUser
        
        print "Successfully created new user", username, "!"
        return newUser