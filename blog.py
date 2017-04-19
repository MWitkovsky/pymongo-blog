import web
import pymongo
from web.contrib.template import render_jinja
import sessionHandler
import usersHandler

#Web.py template setup
urls = (
    "/", "index",
    "/signup", "signup",
    "/login", "login",
    "/logout", "logout",
    "/newpost", "newpost",
    "/u/.*", "userpage"
)
app = web.application(urls, globals())

#Jinja setup
render = render_jinja("templates", encoding = "utf-8")

#Mongodb setup
connection_location = "mongodb://localhost"
connection = pymongo.MongoClient(connection_location)
database = connection.blog

#handler setup
sessions = sessionHandler.SessionHandler(database)
users = usersHandler.UsersHandler(database)

#website parameters
cookieLifespan = 86400

class index:
    def GET(self):
        cookie = web.cookies().get('session')
        username = sessions.validateSession(cookie)
        return render.index(username = username)
    
class signup:
    def GET(self):
        return render.signup()
    def POST(self):
        i = web.input()
        #input sanitization
        if i.username == "":
            return render.signup(username_error = "Please enter a username")
        if i.password != i.verify:
            return render.signup(verify_error = "Passwords do not match.")
        
        #attepmt to insert new user into database
        if users.createAccount(i.username, i.password, i.email) == False:
            return render.signup(username_error = "Username already in use")
        else:
            #Success!
            sessionId = sessions.createSession(i.username)
            web.setcookie("session", sessionId, expires = cookieLifespan)
            raise web.seeother("/")
                
class login:
    def GET(self):
        return render.login()
    def POST(self):
        i = web.input()
        #input sanitization
        if i.username == "":
            return render.login(username_error = "Please enter a username")
        if i.password == "":
            return render.login(username = i.username, password_error = "Please enter a password")
        
        #attempt to login as user
        user = users.login(i.username, i.password)
        if user["errors"] is None:
            #Success!
            sessionId = sessions.createSession(i.username)
            web.setcookie("session", sessionId, expires = cookieLifespan)
            raise web.seeother("/")
        #login failed
        renderArgs = {"username":i.username}
        renderArgs.update(user["errors"])
        return render.login(renderArgs)
    
class logout:
    def GET(self):
        cookie = web.cookies().get('session')
        if cookie is not None:
            sessions.endSession(cookie)
            web.setcookie("session", cookie, expires=-1)
        raise web.seeother("/")
        
class userpage:
    def GET(self):
        requestedUser = web.ctx.path[3:]
        return render.userpage(userExists = users.checkExistence(requestedUser), username = requestedUser)
        
if __name__ == "__main__":
    #ensures usernames are unique, if index already exists then no-op
    database.users.create_index([("username", pymongo.ASCENDING)], unique=True)
    #puts a lifespan on stored sessions so they're automatically purged from the database after the set lifespan
    database.sessions.create_index([("creationDate", pymongo.ASCENDING)], expireAfterSeconds = cookieLifespan)
    app.run()