import json
import hikari


def copy(obj):
    return json.loads(json.dumps(obj))

def get_member_str(member: hikari.Member):
    return f"{member.nickname}' ({member.username}#{member.discriminator})"