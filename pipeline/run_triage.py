"""Report-to-fix triage pipeline.

Flow per question (reports are grouped by question first - duplicates get one analysis):
  1. solver pass (prompts/solver.md) - solves the question blind, without the key.
  2. triage pass (prompts/triage.md) - gets question + reports + solver result, decides
     verdict / repair / edit / route / confidence / evidence / student_reply.
  3. validators (validate.py) - hard guards that reject or demote anything unsafe:
     taxonomy membership, repair-scope (a repair may only touch its own fields),
     find-string must exist in the field, auto:false repairs can never be auto_apply.

LLM backend: any OpenAI-compatible chat endpoint (TRIAGE_BASE_URL / TRIAGE_API_KEY /
TRIAGE_MODEL). With no key, --offline replays a precomputed analysis file, which is how
results.json in this repo was produced (no API credits; the same prompts were run in an
AI assistant session and the raw outputs are committed under analysis/).

Usage:
  python run_triage.py --data ../data --out ../results.json
  python run_triage.py --data ../data --offline analysis/triage_outputs.json --out ../results.json
"""
import argparse, collections, json, os, sys, urllib.request

from normalize import render_question
from validate import validate_result

PROMPT_DIR = os.path.join(os.path.dirname(__file__), 'prompts')

def load_prompt(name):
    return open(os.path.join(PROMPT_DIR, name)).read()

def llm(system, user):
    base = os.environ['TRIAGE_BASE_URL'].rstrip('/')
    req = urllib.request.Request(
        base + '/chat/completions',
        data=json.dumps({'model': os.environ.get('TRIAGE_MODEL', 'gpt-4o-mini'),
                         'messages': [{'role': 'system', 'content': system},
                                      {'role': 'user', 'content': user}],
                         'response_format': {'type': 'json_object'},
                         'temperature': 0}).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['TRIAGE_API_KEY'],
                 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(json.load(r)['choices'][0]['message']['content'])

def solver_user(q, text):
    return json.dumps({'questionType': q['questionType'], 'question': text['question']})

def triage_user(q, text, reports, solved):
    return json.dumps({
        'questionType': q['questionType'], 'question': text['question'],
        'stored_answer': text['answer'], 'stored_solution': text['solution'],
        'independent_solve': solved,
        'reports': [{'reportId': r['reportId'], 'source': r['source'],
                     'comment': r['comment']} for r in reports]})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--offline', help='precomputed triage outputs keyed by reportId')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    questions = {q['_id']: q for q in json.load(open(os.path.join(a.data, 'questions.json')))}
    reports = json.load(open(os.path.join(a.data, 'reports.json')))
    by_q = collections.defaultdict(list)
    for r in reports:
        by_q[r['questionId']].append(r)

    offline = json.load(open(a.offline)) if a.offline else None
    out = []
    for qid, reps in sorted(by_q.items()):
        q = questions[qid]
        text = render_question(q)
        if offline:
            per_report = {rid: offline[rid] for rid in (r['reportId'] for r in reps)}
        else:
            solved = llm(load_prompt('solver.md'), solver_user(q, text))
            triaged = llm(load_prompt('triage.md'), triage_user(q, text, reps, solved))
            per_report = {r['reportId']: dict(triaged) for r in reps}
        for r in reps:
            res = {'reportId': r['reportId'], 'questionId': qid, **per_report[r['reportId']]}
            out.append(validate_result(res, q))

    out.sort(key=lambda r: r['reportId'])
    json.dump(out, open(a.out, 'w'), indent=2)
    print(f'wrote {len(out)} results to {a.out}')

if __name__ == '__main__':
    sys.exit(main())
