from database import Database
from media import Media

class MediaRepository:

    def __init__(self):
        self.database = Database()

    def update_latest(self, media):
        self.database.save("latest-media", media)
        print("%s - saved as lastest media" % media.id)

    def latest(self):
        if not self.database.has_key("latest-media"):
            return Media.EMPTY()

        return self.database.retrieve("latest-media")

    def update_new_ids(self, media):
        new_media = self.new_media_ids()
        new_media.insert(0, media.id)
        self.database.save("new-media", new_media)
        print("%s - registered as new media" % media.id)


    def update_non_new_id(self, media):
        def not_media(this_media_id): return this_media_id != media.id
        self.database.save("new-media", filter(not_media, self.new_media_ids()))
        print("%s - deregistered as new media" % media.id)

    def new_media_ids(self):
        if not self.database.has_key("new-media"):
            return []

        return self.database.retrieve("new-media")

    def has_new_media(self):
        return len(self.new_media_ids()) > 0

    def peek_new_media(self):
        new_media_ids = self.new_media_ids()

        if len(new_media_ids) == 0:
            raise RuntimeError("failed to peek new media as there is no new media to peek")

        return self.retrieve(new_media_ids.pop())

    def save(self, media):
        if (media.is_new()):
            self.update_latest(media)
            self.update_new_ids(media)
        else:
            self.update_non_new_id(media)

        self.database.save(media.id, { "id": media.id, "url": media.url, "status": media.status })
        print("%s - saved to database with status %s" % (media.id, media.status))
        return media

    def retrieve(self, media_id):
        if not self.database.has_key(media_id):
            raise RuntimeError("Failed to retrieve media with id %s, it was not found in the database." % media_id)

        marshalled_media = self.database.retrieve(media_id)
        return Media(id = marshalled_media["id"], url = marshalled_media["url"], status = marshalled_media["status"])
