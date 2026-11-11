"""Bundle console/data.json from the assignment dataset (not committed - see .gitignore).
Usage: python build_console_data.py --data /path/to/acadza-report-fix/data --results ../results.json"""
import argparse, json, os
ap = argparse.ArgumentParser(); ap.add_argument('--data', required=True); ap.add_argument('--results', required=True)
a = ap.parse_args()
out = {k: json.load(open(os.path.join(a.data, k + '.json'))) for k in ('questions', 'reports', 'taxonomy')}
out['results'] = json.load(open(a.results))
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'console', 'data.json'), 'w'))
print('console/data.json written', sum(len(v) for v in out.values()), 'records')
