import datetime
import pymongo
from bson.objectid import ObjectId

class PostHandler:
    def __init__(self, database):
        self.db = database
        self.posts = database.posts
        
    #Puts new post into the database and returns its _id to use as a permalink
    def createPost(self, author, title, body, tags):
        postData = {"errors":{}}
        #input sanitization
        if title == "":
            postData["errors"].update({"title_error" : "Post title must not be blank."})
        if body == "":
            postData["errors"].update({"body_error" : "Post body must not be blank."})
        if tags == "":
            postData["errors"].update({"tag_error" : "There must be at least one tag for your post."})
            
        if postData["errors"]:
            return postData
        
        tagsList = tags.split(",")
        strippedTagsList = []
        for tag in tagsList:
            tag = tag.strip()
            strippedTagsList.append(tag)
        
        #build the post object
        post = {"author" : author,
               "title" : title,
               "body" : body,
               "tags" : strippedTagsList,
               "comments" : [],
               "date" : datetime.datetime.utcnow()}
        
        #put post in database
        try:
            print "Attempting to insert post by", author, "into the database"
            self.posts.insert_one(post)
        except:
            "Unknown error while attempting to insert post by", author, "into the database"
        return postData
        
    def editPost(self, _id, title, body, tags):
        postData = {"errors":{}}
        #input sanitization
        if title == "":
            postData["errors"].update({"title_error" : "Post title must not be blank."})
        if body == "":
            postData["errors"].update({"body_error" : "Post body must not be blank."})
        if tags == "":
            postData["errors"].update({"tag_error" : "There must be at least one tag for your post."})
            
        if postData["errors"]:
            return postData
        
        tagsList = tags.split(",")
        strippedTagsList = []
        for tag in tagsList:
            tag = tag.strip()
            strippedTagsList.append(tag)
        
        #build the post object
        post = {"title" : title,
               "body" : body,
               "tags" : strippedTagsList,
               "date" : datetime.datetime.utcnow(),
               "edited" : True}
        
        #put post in database
        try:
            print "Attempting to update post", _id
            self.posts.update_one({"_id":ObjectId(_id)}, {"$set":{post}})
        except:
            "Unknown error while attempting to update post", _id
        return postData
    
    #Attempts to get a post from the database with the provided permalink
    def getPost(self, permalink):
        try:
            post = self.posts.find_one({"_id": ObjectId(permalink)})
        except:
            print "invalid permalink, aborting"
            post = None
            
        #fix the date up to be pretty, ignoring time zones for now..
        if post is not None:
            post["date"] = post["date"].strftime("%m/%d/%y at %I:%M%p")
        else:
            post = {}
            
        return post
    
    #Attempts to get the specified number of most recent posts site-wide
    def getMostRecentPosts(self, amount):
        posts = None
        try:
            posts = self.posts.find("date", pymongo.DESCENDING)
            posts.limit(amount)
        except:
            print "Unknown error while attempting to get most recent posts" 
            
        postsToReturn = []
        for post in posts:
            post["date"] = post["date"].strftime("%m/%d/%y at %I:%M%p")
            if "comments" not in post:
                post["comments"] = []
            postsToReturn.append(post)
        
        return postsToReturn
    
    #Attempts to get a specified number of posts from a specified author
    def getMostRecentPostsByAuthor(self, author, amount):
        posts = None
        try:
            posts = self.posts.find({"author":author})
            posts.sort([("date", pymongo.DESCENDING)])
            posts.limit(amount)
        except:
            print "Unknown error while attempting to get posts by author", author
            
        postsToReturn = []
        for post in posts:
            post["date"] = post["date"].strftime("%m/%d/%y at %I:%M%p")
            if "comments" not in post:
                post["comments"] = []
            postsToReturn.append(post)
        
        return postsToReturn
    
    #Attempts to get a specified number of posts from a specified tag
    def getMostRecentPostsByTag(self, tag, amount):
        posts = None
        try:
            posts = self.posts.find({"tags":tag})
            posts.sort([("date", pymongo.DESCENDING)])
            posts.limit(amount)
        except:
            print "Unknown error while attempting to get posts tag", author
            
        postsToReturn = []
        for post in posts:
            post["date"] = post["date"].strftime("%m/%d/%y at %I:%M%p")
            if "comments" not in post:
                post["comments"] = []
            postsToReturn.append(post)
        
        return postsToReturn