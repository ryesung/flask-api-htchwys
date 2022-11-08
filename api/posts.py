from flask import jsonify, request, g, abort

from api import api
from db.shared import db
from db.models.user_post import UserPost
from db.models.post import Post

from db.utils import row_to_dict
from middlewares import auth_required

@api.get("/posts")
@auth_required
def get_posts():
    # validation
    user = g.get("user")
    print(user.id)
    if user is None:
        return abort(401)

    # access query values or insert default values, validate the fields are correct entries
    queries = request.args.to_dict()
    authorString = queries.get("authorIds", None)
    if not authorString:
        return jsonify({"error": "Need to specify Authors"}), 400

    sortBy = queries.get("sortBy", "id")
    valid_sortBy_queries =  [ "id", "reads", "likes", "popularity"]
    if sortBy not in valid_sortBy_queries:
        return  jsonify({"error": "Not a valid sortBy query"}), 404


    direction = queries.get("direction", "asc")
    valid_direction_queries = ["asc", "desc"]
    if direction not in valid_direction_queries:
        return jsonify({"error": "Not a valid direction query"}), 404

    sortReverse = False
    if direction == "desc":
        sortReverse = True

    #create master list of posts- no duplicates and make the posts in dict format
    post_list = []
    if (',' in authorString):
        authorIds = [int(i) for i in authorString.split(',')]
        for author in authorIds:
            post_response = Post.get_posts_by_user_id(author)
            for p in post_response:
                item = row_to_dict(p)
                if item not in post_list:
                    post_list.append(item)
    else:
        authorId = int(authorString)
        post_response = Post.get_posts_by_user_id(authorId)
        for p in post_response:
            item = row_to_dict(p)
            if item not in post_list:
                post_list.append(item)


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
        return abort(401)

    linked_post_user = db.session.get(UserPost, (user.id, postId))
    if not (linked_post_user):
        return jsonify({"error": "User can't edit post or post doesn't exist"}), 404


    post_to_change = db.session.get(Post, postId)


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




