class Mention:
    def __init__(self, id, name):
        self.id = id
        self.name = name


def check_mentions(data, mentions=None):
    mentions = []
    if "type" in data and data["type"] == "mention":
        mentions.append(
            Mention(
                id=data.get("mentionId", ""),
                name=data.get("mentionName", ""),
            )
        )
    for c in data.get("children", []):
        mentions.extend(check_mentions(c))
    return mentions
