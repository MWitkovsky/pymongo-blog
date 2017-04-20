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

        for tag in tagsList:
            tag = tag.strip()
        
        #build the post object
        post = {"author" : author,
               "title" : title,
               "body" : body,
               "tags" : tagsList,
               "comments" : [],
               "date" : datetime.datetime.utcnow()}
        
        #put post in database
        try:
            print "Attempting to insert post by", author, "into the database"
            self.posts.insert_one(post)
            postData["permalink"] = post["_id"]
        except:
            "Unknown error while attempting to insert post by", author, "into the database"
        return postData
        
    
    #Attempts to get a post from the database with the provided permalink
    def getPost(self, permalink):
        post = self.posts.find_one({"_id": ObjectId(permalink)})
        #fix the date up to be pretty, ignoring time zones for now..
        if post is not None:
            post["date"] = post["date"].strftime("%m/%d/%y at %I:%M%p")
            
        return post
    
    #Attempts to get a specified number of posts from a specified author. 
    #If author is none, then gets the specified number of most recent posts on the entire website
    def getMostRecentPosts(self, author, amount):
        posts = None
        if author is not None:
            try:
                posts = self.posts.find({"author":author})
                posts.sort([("date", pymongo.DESCENDING)])
                posts.limit(amount)
            except:
                print "Unknown error while attempting to get posts by", author
        else:
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