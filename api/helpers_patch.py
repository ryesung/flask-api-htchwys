def validate_authorIds(authorIds):
    if type(authorIds) != list:
        return False

    for authorId in authorIds:
        if type(authorId) != int:
            return False
    else:
        return True


def validate_tags(tags):
    if type(tags) != list:
        return False

    for tag in tags:
        if type(tag) != str:
            return False
    else:
        return True


