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
3- (different role/alternate permissions). This will allow for changing permissions and simply adding new 
roles to a different integer.

Also in the _**UserPost**_ table there will be a 'pimary_owner' column that will accompany any post. So when looking at the
UserPost table there won't be any confusion about ownership(making sure there is always at least one owner), but the
_**Role**_ column also allow for other owners.

```python
class UserPost(db.Model):
    (...)
    role = db.Column(db.Integer, nullable=False)
    primary_owner =  db.Column(db.Integer, nullable=False)

```

For example a UserPost addition will look like this:

```python

  db.session.add(UserPost(user_id=santiago.id, post_id=post1.id, role=1, primary_owner= post1.owner))

```




```python
owner_id = db.Column(db.Integer, db.ForeignKey("post.owner"))
```

###  Question 2

How would you have to change the PATCH route given your answer above to handle roles?

### ANSWER:

To change the PATCH route we can keep the <postID> URL and also the (user.id) to get the Primary Key of the
UserPost table.  From there the permissions level will be accessed from the _**role**_ column.  Based on the permission 
level the User can access different columns in the _**Post**_ table to modify. For instance, if the user has 
a level 1 (owner) level they can also access all of columns in the _**Post**_ table as well as access to the 
_**UserPost**_ table.

```python

```

