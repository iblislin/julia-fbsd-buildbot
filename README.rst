Julia FreeBSD Buildbot
===============================================================================

Setup master
----------------------------------------------------------------------

::

    pip install -r requirements.txt
    buildbot upgrade-master /path/to/repo/master
    biuldbot start /path/to/repo/master


Setup worker
----------------------------------------------------------------------

::

    pip install -r requirements.txt
    buildbot-worker start /path/to/repo/worker
