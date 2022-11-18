#Roles Proposal
####Changes to be made:
Authors can be owners, editors, or viewers of a blog post. For any blog post, there must always be at least one owner of the blog post. 
Only owners of a blog post can modify the authors' list to a blog post (adding more authors, changing their role).

###  Question 1 
What database changes would be required to the starter code to allow for different roles for authors of a blog post? Imagine that we’d want to also be able to add custom roles and change the permission sets for certain roles on the fly without any code changes.

### ANSWER:


In the _**UserPost**_ table there will be a creation of a _**Role**_ column which will be an integer that is 
linked to a role/permissions level. For instance- 1-(owner/all permissions), 2- (author/limited permisions), 
3- (different role/alternate permissions). This will allow for changing permissions and also adding new custom
roles to a different integer that will be associated with relationship of the User and Post.

```python
class UserPost(db.Model):
    (...)
    role = db.Column(db.Integer, nullable=False)


```

###  Question 2

How would you have to change the PATCH route given your answer above to handle roles?

### ANSWER:
 

If the  (user_post.role == 1) -from UserPost table- which is the owner permissions then that user will get back all
fields from the post_to_change. As well as a list of different roles and users from the UserPost table they will get a list of user.id associated with each role. 
With the ability to change the role assignment for different users.

Else if the role of the User from the UserPost table with be accessed and returning 
whatever columns are editable to that User.

