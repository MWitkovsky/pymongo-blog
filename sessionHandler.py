import uuid
import datetime

class SessionHandler:
    def __init__(self, database):
        self.db = database
        self.sessions = database.sessions
        
    def createSession(self, username):
        sessionId = str(uuid.uuid4())
        session = {"_id":sessionId, "username":username, "creationDate":datetime.datetime.utcnow()}
        
        print "Attempting to create new user session with id", sessionId
        try:
            self.sessions.insert_one(session)
        except:
            print "Error when attempting to create new session with id", sessionId
            return None
        return sessionId
    
    def endSession(self, sessionId):
        print "Attempting to end user session with id", sessionId
        try:
            self.sessions.delete_one({"_id":sessionId})
        except:
            print "Error when attempting to remove session id", sessionId
        return
    
    def getSession(self, sessionId):
        print "Attempting to get session with session id", sessionId
        try:
            session = self.sessions.find_one({"_id":sessionId})
        except:
            print "Error when attempting to get session with id", sessionId
            return None
        return session

    def validateSession(self, sessionId):
        print "Attempting to validate session with session id", sessionId
        try:
            session = self.sessions.find_one({"_id":sessionId})
            return session["username"]
        except:
            print "Error when attempting to validate session with id", sessionId