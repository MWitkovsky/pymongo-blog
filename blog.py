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
    "/p/(?!edit/)(?!del/).*", "viewpost",
    "/p/edit/.*", "editpost",
    "/p/del/.*", "deletepost",
    "/t/.*", "viewtag",
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

def notFound():
    raise web.seeother("/")
        
#web.py webpage classes
class index:
    def GET(self):
        return render.index(username = getUsername(), posts = posts.getMostRecentPosts(10))
    
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
            raise web.seeother("/")
        postData = posts.createPost(username, i.title, i.body, i.tags)
        if postData["errors"]:
            renderArgs = {"username" : username, 
                         "title" : i.title, 
                         "body" : i.body,
                         "tags" : i.tags}
            renderArgs.update(postData["errors"])
            return render.newpost(renderArgs)
        else:        
            raise web.seeother("/p/"+str(postData["_id"]))
        
class viewpost:
    def GET(self):
        if len(web.ctx.path) <= 3:
             raise web.seeother("/")
            
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedPost = web.ctx.path[3:web.ctx.path.index("/", 3)]
        else:
            requestedPost = web.ctx.path[3:]
        renderArgs = posts.getPost(requestedPost)
        if renderArgs:
            renderArgs["username"] = getUsername()
            return render.viewpost(renderArgs)
        else:
            raise web.seeother("/")
    
class editpost:
    def GET(self):
        if len(web.ctx.path) <= 8:
             raise web.seeother("/")
            
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedPost = web.ctx.path[8:web.ctx.path.index("/", 8)]
        else:
            requestedPost = web.ctx.path[8:]
            
        renderArgs = posts.getPost(requestedPost)
        renderArgs["username"] = getUsername()
        #throws user away from edit page if they're not the author
        if renderArgs["author"] != renderArgs["username"]:
            raise web.seeother("/p/"+requestedPost)
        return render.editpost(renderArgs)
    
    def POST(self):
        i = web.input()
        if len(web.ctx.path) <= 8:
             raise web.seeother("/")
            
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedPost = web.ctx.path[8:web.ctx.path.index("/", 8)]
        else:
            requestedPost = web.ctx.path[8:]
            
        username = getUsername()
        if username is None:
            raise web.seeother("/")
        postData = posts.editPost(requestedPost, i.title, i.body, i.tags)
        if postData["errors"]:
            renderArgs = posts.getPost(requestedPost)
            renderArgs.update({"username" : username, 
                         "title" : i.title, 
                         "body" : i.body})
            renderArgs.update(postData["errors"])
            return render.editpost(renderArgs)
        else:
            raise web.seeother("/p/"+requestedPost)

class deletepost:
    def GET(self):
        if len(web.ctx.path) <= 7:
             raise web.seeother("/")
            
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedPost = web.ctx.path[7:web.ctx.path.index("/", 7)]
        else:
            requestedPost = web.ctx.path[7:]
        username = getUsername()
        post = posts.getPost(requestedPost)
        if not post:
            raise web.seeother("/p/"+requestedPost)
        elif username is None:
            raise web.seeother("/p/"+requestedPost)
        elif username != post["author"]:
            raise web.seeother("/p/"+requestedPost)
        return render.deletepost(username = username, _id = requestedPost)
    
    def POST(self):
        i = web.input()
        if len(web.ctx.path) <= 7:
             raise web.seeother("/p/"+requestedPost)
            
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedPost = web.ctx.path[7:web.ctx.path.index("/", 7)]
        else:
            requestedPost = web.ctx.path[7:]
        username = getUsername()
        if username is None:
            raise web.seeother("/p/"+requestedPost)
       
        elif username != posts.getPost(requestedPost)["author"]:
            raise web.seeother("/p/"+requestedPost)
        
        if i.response == "True":
            posts.deletePost(requestedPost)
            return render.deletepost(delete_success = "Post deleted.", username = username)
        elif i.response == "False":
            raise web.seeother("/p/"+requestedPost)
        

class viewtag:
    def GET(self):
        if len(web.ctx.path) <= 3:
             raise web.seeother("/")
            
        if web.ctx.path[len(web.ctx.path)-1] == "/":
            requestedTag = web.ctx.path[3:web.ctx.path.index("/", 3)]
        else:
            requestedTag = web.ctx.path[3:]
        renderArgs = {"tag" : requestedTag,
                     "posts" : posts.getMostRecentPostsByTag(requestedTag, 10),
                     "username" : getUsername()}
        return render.viewtag(renderArgs)
        
class userpage:
    def GET(self):
        if len(web.ctx.path) <= 3:
             return render.userpage(username = getUsername(), userExists = False)
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
            renderArgs["posts"] = posts.getMostRecentPostsByAuthor(requestedUser, 10)
        return render.userpage(renderArgs)

#main
if __name__ == "__main__":
    #ensures usernames are unique, if index already exists then no-op
    database.users.create_index([("lowerUsername", pymongo.ASCENDING)], unique=True)
    #puts a lifespan on stored sessions so they're automatically purged from the database after the set lifespan
    database.sessions.create_index([("creationDate", pymongo.ASCENDING)], expireAfterSeconds = cookieLifespan)
    #sets up an index on post authors, post tags, and post dates
    database.posts.create_index([("author", pymongo.ASCENDING)])
    database.posts.create_index([("tags", pymongo.ASCENDING)])
    database.posts.create_index([("date", pymongo.ASCENDING)])
    app.notfound = notFound
    app.run()