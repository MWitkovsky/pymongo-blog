import web
import pymongo
from web.contrib.template import render_jinja
import sessionHandler
import usersHandler
import postHandler

#Web.py template setup
#"\/p\/(?!static).*", "viewpost",
urls = (
    "/", "index",
    "/signup", "signup",
    "/login", "login",
    "/logout", "logout",
    "/newpost", "newpost",
    "/p/.*", "viewpost",
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
        if newUser["errors"]:
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
        if not user["errors"]:
            #Success!
            sessionId = sessions.createSession(user["object"]["username"])
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
        username = getUsername()
        if username is None:
            return render.index(session_error = "Your session has timed out. Please log back in to make a post.")
        postData = posts.createPost(username, i.title, i.body, i.tags)
        if postData["errors"]:
            renderArgs = {"username" : username, 
                         "title" : i.title, 
                         "body" : i.body,
                         "tags" : i.tags}
            renderArgs.update(postData["errors"])
            return render.newpost(renderArgs)
        else:        
            raise web.seeother("/p/"+str(postData["permalink"]))
        
class viewpost:
    def GET(self):
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedPost = web.ctx.path[3:web.ctx.path.index("/", 3)]
        else:
            requestedPost = web.ctx.path[3:]
        renderArgs = posts.getPost(requestedPost)
        return render.viewpost(renderArgs)
        
class userpage:
    def GET(self):
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedUser = web.ctx.path[3:web.ctx.path.index("/", 3)]
        else:
            requestedUser = web.ctx.path[3:]
        requestedUser = users.checkExistence(requestedUser)
        renderArgs = {"userExists" : requestedUser is not None,
                     "requestedUser" : requestedUser,
                     "posts" : None,
                     "username" : getUsername()}
        if renderArgs["userExists"]:
            renderArgs["posts"] = posts.getMostRecentPosts(requestedUser, 10)
        return render.userpage(renderArgs)

#main
if __name__ == "__main__":
    #ensures usernames are unique, if index already exists then no-op
    database.users.create_index([("lowerUsername", pymongo.ASCENDING)], unique=True)
    #puts a lifespan on stored sessions so they're automatically purged from the database after the set lifespan
    database.sessions.create_index([("creationDate", pymongo.ASCENDING)], expireAfterSeconds = cookieLifespan)
    #sets up an index on post permalinks, post authors, and post dates
    database.posts.create_index([("permalink", pymongo.ASCENDING)])
    database.posts.create_index([("author", pymongo.ASCENDING)])
    database.posts.create_index([("date", pymongo.ASCENDING)])
    app.run()