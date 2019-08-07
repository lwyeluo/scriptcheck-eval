Modify Chrome's source code in `tools/perf/contrib/cros_benchmarks/page_cycler_v2.py`

```
"""
Added by Luo Wu.
To test the top_10 using page_sets/top_10.py
"""
@benchmark.Owner(emails=['kouhei@chromium.org', 'ksakamoto@chromium.org'])
class PageCyclerV2Top10(_PageCyclerV2):
  """Page load time benchmark for a top 10 web pages.

  Designed to represent typical, not highly optimized or highly popular web
  sites. Runs against pages recorded in June, 2014.
  """

  @classmethod
  def Name(cls):
    return 'page_cycler_v2.top_10'

  def CreateStorySet(self, options):
    return page_sets.Top10PageSet()
```

The steps to run telemetry are shown in `cmd`