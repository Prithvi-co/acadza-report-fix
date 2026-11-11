"""Hard guards between the LLM and the database. The model proposes; these decide.
Anything that fails a guard is demoted to faculty_review, never silently applied."""
import json, os

_tax = os.environ.get('TRIAGE_TAXONOMY', os.path.join(os.path.dirname(__file__), '..', 'data', 'taxonomy.json'))
TAXONOMY = json.load(open(_tax))

class Reject(Exception):
    pass

def _field_text(q, field):
    body = q.get(q.get('questionType')) or {}
    if field in ('question', 'solution'):
        return body.get(field, '') or ''
    if field in ('answer', 'questionType'):
        v = body.get(field) if field == 'answer' else q.get(field)
        return json.dumps(v)
    return ''

def validate_result(res, q):
    v = res.get('verdict')
    if v not in TAXONOMY['verdicts']:
        raise Reject(f"{res['reportId']}: unknown verdict {v!r}")
    repair = res.get('repair')
    if v == 'defect' and not repair:
        raise Reject(f"{res['reportId']}: defect without repair")
    if v != 'defect':
        res['repair'] = None
        res['edit'] = None
        res['route'] = 'no_change' if res.get('route') != 'faculty_review' else 'faculty_review'
        return res
    if repair not in TAXONOMY['repairs']:
        raise Reject(f"{res['reportId']}: unknown repair {repair!r}")
    spec = TAXONOMY['repairs'][repair]
    edit = res.get('edit')
    if edit:
        if edit.get('field') not in spec['fields']:
            # scope guard: repair may only touch its own fields
            res['route'] = 'faculty_review'
            res['edit'] = None
            res['evidence'] += ' | edit rejected: field outside repair scope'
        elif edit.get('find') is not None and edit['field'] in ('question', 'solution'):
            if edit['find'] not in _field_text(q, edit['field']):
                res['route'] = 'faculty_review'
                res['evidence'] += ' | find string not present verbatim - needs human edit'
    if not spec['fields'] and edit:
        res['edit'] = None
    if not spec['auto'] and res.get('route') == 'auto_apply':
        res['route'] = 'faculty_review'
        res['evidence'] += ' | auto:false repair demoted to faculty_review'
    if res.get('route') == 'auto_apply' and not res.get('edit'):
        res['route'] = 'faculty_review'
    return res
