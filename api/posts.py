from flask import jsonify, request, g, abort
from api import api
from db.shared import db
from sqlalchemy.orm.exc import UnmappedInstanceError
from db.models.user_post import UserPost
from db.models.post import Post
from api.helpers_patch import validate_authorIds, validate_tags
from db.utils import row_to_dict, rows_to_list
from middlewares import auth_required


valid_sortBy_queries = ["id", "reads", "likes", "popularity"]
valid_direction_queries = ["asc", "desc"]


@api.get("/posts")
@auth_required
def get_posts():
    # validation
    user = g.get("user")
    if user is None:
        return jsonify("error: Request Requires Authorization"), 401

    # access query values
    queries = request.args.to_dict()

    # AuthorIds - make sure they in correct format and are valid posts
    authorString = queries.get("authorIds", None)

    ## post_list to add posts
    post_list = []
    if authorString:
        try:
            if (',' in authorString):
                author_ids = [int(i) for i in authorString.split(',')]
            else:
                author_ids = [int(authorString)]

            for authorId in author_ids:
                post_response = Post.get_posts_by_user_id(authorId)
                for post in post_response:
                    item = row_to_dict(post)
                    if item not in post_list:
                        post_list.append(item)

        except ValueError:
            return jsonify({"error": "authorIds must be a string of integer separated by commas"}), 400

        except UnmappedInstanceError:
            return jsonify({"error": "authorId not in the database"}), 400

    else:
        return jsonify({"error": "Need to specify Authors"}), 400

    sortBy = queries.get("sortBy", "id")
    if sortBy not in valid_sortBy_queries:
        return jsonify({"error": "Not a valid sortBy query"}), 400

    direction = queries.get("direction", "asc")
    sortReverse = False
    if direction not in valid_direction_queries:
        return jsonify({"error": "Not a valid direction query"}), 400

    if direction == "desc":
        sortReverse = True


    #use all query parameters to get final sorted list and jsonify for response
    master_list = sorted(post_list, key=lambda d: d[sortBy], reverse=sortReverse)
    final_json = {"posts": master_list}

    return jsonify(final_json), 200


@api.post("/posts")
@auth_required
def posts():
    # validation
    user = g.get("user")
    if user is None:
        return jsonify("error: Request Requires Authorization"), 401

    data = request.get_json(force=True)
    text = data.get("text", None)
    tags = data.get("tags", None)
    if text is None:
        return jsonify({"error": "Must provide text for the new post"}), 400

    # Create new post
    post_values = {"text": text}
    if tags:
        post_values["tags"] = tags

    post = Post(**post_values)
    db.session.add(post)
    db.session.commit()

    user_post = UserPost(user_id=user.id, post_id=post.id)
    db.session.add(user_post)
    db.session.commit()

    return row_to_dict(post), 200

@api.patch("/posts/<int:postId>")
@auth_required
def update(postId):
    # validation
    user = g.get("user")
    if user is None:
        return jsonify("error: Request Requires Authorization"), 401

    post_is_valid = db.session.get(UserPost, (user.id, postId))

    if not post_is_valid:
         return jsonify({"error": "User does not have permissions to edit post."}), 401

    # get data from PATCH request
    data = request.get_json(force=True)
    authorIds = data.get("authorIds", None)
    text = data.get("text", None)
    tags = data.get("tags", None)

    post_to_change = db.session.get(Post, (postId))

    if authorIds:
        if validate_authorIds(authorIds):

            #get all user_posts associated with the post and a list of userIds o
            user_posts = Post.get_user_posts_by_post_id(postId)
            userPost_userIds = [userPost.user_id for userPost in user_posts]

            #removing user_posts that are not on the Author list
            for userPost in user_posts:
                if userPost.user_id not in authorIds:
                    db.session.delete(userPost)


            # add User_Post for Authors not previous in database
            for authorId in authorIds:
                if authorId not in userPost_userIds:
                    db.session.add(UserPost(user_id=authorId, post_id=postId))
        else:
             return jsonify({"error": "Invalid input for 'authorIds'. "}), 400

    if tags:
        if validate_tags(tags):
            post_to_change.tags = tags
        else:
            return jsonify({"error": "Invalid input for 'tags'."}), 400

    if text:
        if type(text) == str:

            post_to_change.text = text
        else:
            jsonify({"error": "Invalid input for 'text'."}), 400

    db.session.add(post_to_change)
    db.session.commit()

    updated_post = db.session.get(Post, postId)
    json_response = row_to_dict(updated_post)
    json_response['authorIds'] = [userPost.user_id for userPost in Post.get_user_posts_by_post_id(postId)]
    return jsonify({'post': json_response}), 200




