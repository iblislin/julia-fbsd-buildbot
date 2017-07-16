--- github.py.orig	2017-07-15 11:58:37.892774000 +0800
+++ github.py	2017-07-16 15:20:26.987372000 +0800
@@ -24,10 +24,12 @@
 
 from dateutil.parser import parse as dateparse
 
+from twisted.internet import defer
 from twisted.python import log
 
 from buildbot.changes.github import PullRequestMixin
 from buildbot.util import bytes2NativeString
+from buildbot.util import httpclientservice
 from buildbot.util import unicode2bytes
 from buildbot.www.hooks.base import BaseHookHandler
 
@@ -135,6 +137,9 @@
         commits = payload['pull_request']['commits']
         title = payload['pull_request']['title']
         comments = payload['pull_request']['body']
+        head_sha = payload['pull_request']['head']['sha']
+        head_commit_url = '{}/commits/{}'.format(
+            payload['repository']['url'], head_sha)
 
         log.msg('Processing GitHub PR #{}'.format(number),
                 logLevel=logging.DEBUG)
@@ -144,6 +149,9 @@
             log.msg("GitHub PR #{} {}, ignoring".format(number, action))
             return changes, 'git'
 
+        if self._check_head_commit_skip(head_commit_url):
+            return changes, 'git'
+
         properties = self.extractProperties(payload['pull_request'])
         properties.update({'event': event})
         change = {
@@ -172,6 +180,32 @@
             len(changes), number))
         return changes, 'git'
 
+    def _check_head_commit_skip(self, url):
+        import requests
+
+        res = requests.get(url)
+
+        if res.status_code != 200:
+            return True  # skip this change
+
+        d = res.json()
+        msg = d['commit']['message']
+        return self._has_skip(msg)
+
+    def _has_skip(self, msg):
+        """
+        Checking the skip pattern is in commit message or not
+        """
+        if re.search(r'\[ *skip *ci *\]', msg):
+            return True
+        elif re.search(r'\[ *ci *skip *\]', msg):
+            return True
+        elif re.search(r'\[ *skip *bsd *\]', msg):
+            return True
+        elif re.search(r'\[ *bsd *skip *\]', msg):
+            return True
+        return False
+
     def _process_change(self, payload, user, repo, repo_url, project, event,
                         properties):
         """
@@ -196,6 +230,12 @@
             log.msg("Branch `{}' deleted, ignoring".format(branch))
             return changes
 
+        # check [ci skip] or [skip ci]
+        head_msg = payload['head_commit']['message']
+        log.msg("Head commit msg: {}".format(head_msg))
+        if self._has_skip(head_msg):
+            return changes
+
         for commit in payload['commits']:
             files = []
             for kind in ('added', 'modified', 'removed'):
