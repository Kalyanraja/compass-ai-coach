"""Command line entry point.

  python -m compass                 start the server and open the browser
  python -m compass --no-browser    start without opening a browser
  python -m compass --reset         rebuild the synthetic dataset and clear private data
  python -m compass eval            run the recommendation-quality evaluation
  python -m compass export-data     write the synthetic dataset to data/synthetic/*.csv
  python -m compass compliance      run data-minimization checks
"""

import argparse
import json
import sys

from . import config, db


def main(argv=None):
    ap = argparse.ArgumentParser(prog="compass", description="Compass AI Engineering Enablement Coach")
    ap.add_argument("command", nargs="?", default="serve", choices=["serve", "eval", "export-data", "compliance"])
    ap.add_argument("--host", default=config.HOST)
    ap.add_argument("--port", type=int, default=config.PORT)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args(argv)

    if args.reset:
        db.init(reset=True)
        if config.AUDIT_LOG.exists():
            config.AUDIT_LOG.unlink()
        print("Synthetic dataset rebuilt; private data cleared.")

    if args.command == "serve":
        from .server import serve
        serve(args.host, args.port, open_browser=not args.no_browser)
    elif args.command == "eval":
        from . import evaluation
        db.init()
        report = evaluation.run(write=True)
        s = report["summary"]
        print(f"Recommendation quality: {s['passed']}/{s['total']} scenarios passed ({s['pass_rate']:.0%}); "
              f"target {s['target']:.0%} -> {'PASS' if s['meets_target'] else 'FAIL'}")
        p = report["prompt_coach"]["summary"]
        print(f"Prompt coach routing: {p['passed']}/{p['total']} stories passed ({p['pass_rate']:.0%})")
        print("Reports written to reports/eval-report.md and reports/eval-report.json")
        sys.exit(0 if s["meets_target"] else 1)
    elif args.command == "export-data":
        from . import synth
        out = synth.export_csv(config.ROOT / "data" / "synthetic")
        print(f"Wrote CSV files to {out}")
    elif args.command == "compliance":
        from . import compliance
        db.init()
        r = compliance.run()
        print(json.dumps(r, indent=2))
        sys.exit(0 if r["passed"] else 1)


if __name__ == "__main__":
    main()
