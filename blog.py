import web
import pymongo
from web.contrib.template import render_jinja
import sessionHandler
import usersHandler
import postHandler

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
posts = postHandler.PostHandler(database)

#website parameters
cookieLifespan = 86400

#helper functions
def getUsername():
    return sessions.validateSession(web.cookies().get('session'))
        
#web.py webpage classes
class index:
    def GET(self):
        return render.index(username = getUsername())
    
class signup:
    def GET(self):
        return render.signup()
    
    def POST(self):
        i = web.input()
        newUser = users.createAccount(i.username, i.password, i.verify, i.email)
        #attepmt to insert new user into database
        if newUser["errors"] is not None:
            #failed with errors
            renderArgs = {"username":i.username}
            renderArgs.update(newUser["errors"])
            return render.signup(renderArgs)
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
        
class newpost:
    def GET(self):
        cookie = web.cookies().get('session')
        if cookie is not None:
            username = sessions.validateSession(cookie)
            return render.newpost(username = username)
        else:
            raise web.seeother("/")
            
    def POST(self):
        i = web.input()
        #input sanitization
        if i.title == "":
            return render.newpost(username = getUsername(), title_error = "title can't be blank")
        if i.body == "":
            return render.newpost(username = getUsername(), title_error = "title can't be blank")
        
class userpage:
    def GET(self):
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedUser = web.ctx.path[3:web.ctx.path.index("/", 3)]
        else:
            requestedUser = web.ctx.path[3:]
        renderArgs = {}
        renderArgs["userExists"] = users.checkExistence(requestedUser)
        renderArgs["requestedUser"] = requestedUser
        renderArgs["posts"] = None
        cookie = web.cookies().get('session')
        if cookie is not None:
            renderArgs["username"] = sessions.validateSession(cookie)
        return render.userpage(renderArgs)
        
#main
if __name__ == "__main__":
    #ensures usernames are unique, if index already exists then no-op
    database.users.create_index([("username", pymongo.ASCENDING)], unique=True)
    #puts a lifespan on stored sessions so they're automatically purged from the database after the set lifespan
    database.sessions.create_index([("creationDate", pymongo.ASCENDING)], expireAfterSeconds = cookieLifespan)
    app.run()