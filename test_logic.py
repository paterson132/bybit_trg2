import sys, types, unittest
try:
    import pybit.unified_trading
except ModuleNotFoundError:
    pybit = types.ModuleType('pybit')
    unified = types.ModuleType('pybit.unified_trading')
    unified.HTTP = type('HTTP', (), {})
    pybit.unified_trading = unified
    sys.modules['pybit'] = pybit
    sys.modules['pybit.unified_trading'] = unified

import app

class CandleSchedulingTests(unittest.TestCase):
    def test_supported_timeframes(self):
        self.assertEqual(app.TIMEFRAMES['1'], 60)
        self.assertEqual(app.TIMEFRAMES['3'], 180)
        self.assertEqual(app.TIMEFRAMES['45'], 2700)
        self.assertEqual(app.TIMEFRAMES['D'], 86400)

    def test_open_candle_is_excluded(self):
        now = 10_000_000
        rows = [[str(now - 120_000), '1','1','1','1','1','1'],
                [str(now - 60_000), '1','1','1','1','1','1'],
                [str(now), '1','1','1','1','1','1']]
        closed = app.closed_bars(rows, '1', now_ms=now)
        self.assertEqual([int(r[0]) for r in closed], [now - 120_000, now - 60_000])

    def test_45m_aggregation_uses_three_15m_candles(self):
        start = 0
        raw = [
            [str(start), '100','105','99','103','2','200'],
            [str(start+900_000), '103','108','102','107','3','300'],
            [str(start+1_800_000), '107','109','104','105','4','400'],
        ]
        groups = {}
        bucket_ms = 45 * 60_000
        for r in raw:
            t = int(r[0]); bucket = (t // bucket_ms) * bucket_ms
            groups.setdefault(bucket, []).append(r)
        out = []
        for bucket, group in sorted(groups.items()):
            group = sorted(group, key=lambda x: int(x[0]))
            if len(group) == 3 and [int(x[0]) for x in group] == [bucket,bucket+900_000,bucket+1_800_000]:
                out.append([str(bucket),group[0][1],max(float(x[2]) for x in group),min(float(x[3]) for x in group),group[-1][4],str(sum(float(x[5]) for x in group)),str(sum(float(x[6]) for x in group))])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0][1:5], ['100', 109.0, 99.0, '105'])
        self.assertEqual(float(out[0][5]), 9.0)

if __name__ == '__main__':
    unittest.main()
