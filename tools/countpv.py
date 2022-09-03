#!/bin/env python
# Count page views by nginx logs, and output json format.

import sys
import re
import json
import os
import gzip

if len(sys.argv) != 2:
    print('Usage: %s <nginx_log_dir>' % sys.argv[0])
    sys.exit(1)

logdir = sys.argv[1]
pageviews = {}
for log in os.listdir(logdir):
    if log.startswith('access.log'):
        openfunc = gzip.open if log.endswith('.gz') else open
        with openfunc(os.path.join(logdir, log)) as fp:
            for line in fp.readlines():
                m = re.search(r'GET (/posts/\S+/)', line)
                if m and 'Baiduspider' not in line:
                    post_path = m.group(1)
                    if post_path not in pageviews:
                        pageviews[post_path] = 1
                    else:
                        pageviews[post_path] += 1

pageviews_for_chirpy = {'rows': []}
for k, v in pageviews.items():
    pageviews_for_chirpy['rows'].append([k, str(v)])

print(json.dumps(pageviews_for_chirpy, indent=2))
