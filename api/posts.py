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
    # user = g.get("user")
    # if user is None:
    #     return abort(401)

    # access query values or insert default values
    queries = request.args.to_dict()
    authorString = queries.get("authorIds", None)

    if not authorString:
        return jsonify({"error": "Need to specify Authors"}), 400

    sortBy = queries.get("sortBy", "id")
    direction = queries.get("direction", "asc")
    sortReverse = False
    if direction == "desc":
        sortReverse = True

    #create master list of posts- no duplicates and dictionary posts
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