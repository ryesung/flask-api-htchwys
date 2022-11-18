from flask import jsonify, request, g, abort
from api import api
from db.shared import db
from sqlalchemy.orm.exc import UnmappedInstanceError
from db.models.user_post import UserPost
from db.models.post import Post

from db.utils import row_to_dict
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
    post_list = []
    if authorString:
        try:
            if (',' in authorString):
                author_ids = [int(i) for i in authorString.split(',')]
            else:
                author_ids = [int(authorString)]

            for authorId in author_ids:
                post_response = Post.get_posts_by_user_id(authorId)
                for p in post_response:
                    item = row_to_dict(p)
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
    if direction not in valid_direction_queries:
        return jsonify({"error": "Not a valid direction query"}), 400

    sortReverse = False
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
        return abort(401)

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


    print(user.id, postId)
    post_to_change = db.session.get(UserPost, (user.id, postId))
    if not post_to_change:
         return jsonify({"error": "User does not have permissions to edit post."}), 401

    #get list of author IDs associated with postID
    authors = Post.get_authors_by_post(postId)
    post_authors = [i.id for i in authors]

    data = request.json


    for data_key, data_value in data.items():
        if data_key == "authorIds":
            if type(data_value) == list and type(data_value[0]) == int:
                #delete any extraneous authors in previous record
                for a in post_authors:
                    if a not in data_value:
                        delete_post = UserPost.query.get((a, postId))
                        db.session.delete(delete_post)
            else:
                return jsonify({"error": "Invalid input for 'authorIds'. "}), 400

            #add any new Authors
            for authorId in data_value:
                if authorId not in post_authors:
                    db.session.add(UserPost(user_id=authorId, post_id=postId))

            # reassign value to authorIds list if in PATCH request
            post_authors = data_value

        if data_key == "tags":
            if type(data_value) == list and type(data_value[0]) == str:
                post_to_change.tags = data_value
            else:
                jsonify({"error": "Invalid input for 'tags'."}), 400

        if data_key == "text":
            if type(data_value) == str:
                post_to_change.text = data_value
            else:
                jsonify({"error": "Invalid input for 'text'. "}), 400
    db.session.commit()

    updated_post = db.session.get(Post, postId)
    json_response = row_to_dict(updated_post)
    json_response['authorIds'] = post_authors
    return jsonify({'post': json_response}), 200




