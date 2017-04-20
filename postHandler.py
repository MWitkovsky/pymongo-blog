import datetime

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
            
        if post["errors"]:
            return postData
        
        #build the post object
        post = {"author" : author,
               "title" : title,
               "body" : body,
               "tags" : tags,
               "comments" : [],
               "date" : datetime.datetime.utcnow()}
        
        #put post in database
        try:
            print "Attempting to insert post by", author, "into the database"
            postData["permalink"] = self.posts.insert_one(post)
            return postData
        except:
            "Unknown error while attempting to insert post by", author, "into the database"
            return postData
        
    
    #Attempts to get a post from the database with the provided permalink
    def getPost(self, permalink):
        post = self.posts.find_one({"_id":permalink})
        
        if post is not None:
            post["date"] = post['date'].strftime("%-m/%-d/%y at %-I:%M%p")
            
        return post