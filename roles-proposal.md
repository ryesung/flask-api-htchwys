#Roles Proposal
####Changes to be made:
Authors can be owners, editors, or viewers of a blog post. For any blog post, there must always be at least one owner of the blog post. 
Only owners of a blog post can modify the authors' list to a blog post (adding more authors, changing their role).

###  Question 1 
What database changes would be required to the starter code to allow for different roles for authors of a blog post? Imagine that we’d want to also be able to add custom roles and change the permission sets for certain roles on the fly without any code changes.

### ANSWER:

In order to _**always be at least one owner of a blog post**_ there will have to be an 
assignment of ownership upon creation of a Post(). Therefore I will add another column 'owner' in Post() 
in which a valid "user.id" from the _**User**_ table must be added in the Post creation.

```python
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    (...)
    owner =  db.Column(db.Integer, db.ForeignKey("user.id"))

```

Then in the _**UserPost**_ table there will be a creation of a _**Role**_ column which will be an integer that is 
linked to a role/permissions level. For instance- 1-(owner/all permissions), 2- (author/limited permisions), 
3- (different role/alternate permissions). This will allow for changing permissions and also adding new custom
roles to a different integer.

```python
class UserPost(db.Model):
    (...)
    role = db.Column(db.Integer, nullable=False)


```

For example a UserPost addition will look like this:

```python

  db.session.add(UserPost(user_id=santiago.id, post_id=post1.id, role=1))

```

###  Question 2

How would you have to change the PATCH route given your answer above to handle roles?

### ANSWER:
 

If the (user.id == post.owner) -from Post table- or has a (user_post.role == 1) -from UserPost table- which is an owner then that user will get back all
fields from the post_to_change. As well as a list of different roles and users from the UserPost table they will get a list of user.id associated with each role. 
With the ability to change the role assignment for different users.

Else if the role of the User from the UserPost table with be accessed and returning 
whatever columns are editable to that User.

