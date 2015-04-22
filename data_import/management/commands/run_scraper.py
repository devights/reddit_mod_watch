from daemon_command import DaemonCommand
from data_import import importer
from data_import.models import User, Subreddit
import logging
import_log = logging.getLogger('import_status')


class Command(DaemonCommand):
    def loop_callback(self):
        importer.priority_import_user_subs(10)
        importer.priority_import_sub_mods(10)

        user_count = User.objects.all().count()
        sub_count = Subreddit.objects.all().count()
        import_log.info("%s users\n%s subs" % (user_count, sub_count))
