#!/usr/bin/env python
from lib.system import System
from lib.media_repository import MediaRepository
from lib.media_server import MediaServer
from lib.support_team import SupportTeam
import signal
import traceback
import time
import os

class InstagramPrinter:

    def __init__(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.running = False
        self.system = System()
        self.media_repository = MediaRepository()
        self.media_server = MediaServer(self.media_repository)

    def start(self):
        self.running = True
        self.run()

    def run(self):

        if self.system.has_printer():
            SupportTeam.notify("using system default printer %s" % self.system.printer().printer_name)

        while self.running:
            try:
                if not self.system.has_printer():
                    SupportTeam.notify("failure - system has no default printer, skipping print")

                    # wait a bit longer than normal, so that the printer doesn't smash the log failed
                    time.sleep(20)
                    continue

                media = self.media_server.next()

                if media and self.running:
                    SupportTeam.notify("%s - preparing to print" % media.id)
                    self.system.printer().send(media.download())
                    self.media_repository.update_media_status(media, "printed")
                    SupportTeam.notify("%s - print complete." % media.id)

            except:
                exceptiondata = traceback.format_exc().splitlines()
                SupportTeam.notify("failure - uncaught error, %s. skipping print" % (exceptiondata[-1]))

            finally:
                if "DEBUG" in os.environ and os.environ["DEBUG"] == "true":
                    SupportTeam.notify("debug: end loop, %s" % self.media_repository)

                time.sleep(5)

        SupportTeam.notify("safely exiting process.")

    def stop(self, signum, frame):
        SupportTeam.notify("shutdown hook received, will stop at the end of print loop")
        self.running = False

if __name__ == '__main__':
    SupportTeam.notify("startup hook received")
    InstagramPrinter().start()
