"""Render Acadza's production-format records (HTML + inline MathML) to plain text
for the LLM steps. Lossy on purpose: the console renders the raw HTML/MathML natively;
the LLM only needs to read the math."""
import re, html
from xml.etree import ElementTree as ET

MML = '{http://www.w3.org/1998/Math/MathML}'

def _mml(el):
    tag = el.tag.replace(MML, '')
    if tag in ('math', 'mrow', 'mstyle', 'mpadded', 'semantics'):
        return ''.join(_mml(c) for c in el if 'annotation' not in c.tag)
    if tag in ('mn', 'mi', 'mo', 'mtext'):
        return el.text or ''
    if tag == 'msup':
        return f'{_mml(el[0])}^({_mml(el[1])})'
    if tag == 'msub':
        return f'{_mml(el[0])}_({_mml(el[1])})'
    if tag == 'msubsup':
        return f'{_mml(el[0])}_({_mml(el[1])})^({_mml(el[2])})'
    if tag == 'mfrac':
        return f'(({_mml(el[0])})/({_mml(el[1])}))'
    if tag == 'msqrt':
        return 'sqrt(' + ''.join(_mml(c) for c in el) + ')'
    if tag == 'mroot':
        return f'root[{_mml(el[1])}]({_mml(el[0])})'
    if tag == 'mspace':
        return ' '
    if tag == 'annotation':
        return ''
    return (el.text or '') + ''.join(_mml(c) for c in el)

def html_to_text(s):
    if not s:
        return ''
    def repl(m):
        # production data has stray '&' artifacts and HTML entities inside MathML
        frag = html.unescape(m.group(0)).replace('&', ' and ')
        try:
            return ' ' + _mml(ET.fromstring(frag)).strip() + ' '
        except Exception:
            return ' [unparsed-math] '
    s = re.sub(r'<math[\s>].*?</math>', repl, s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</(p|div|h[1-6]|li|tr)>', '\n', s, flags=re.I)
    s = re.sub(r'<img[^>]*>', ' [IMG] ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t ]+', ' ', s)
    return re.sub(r'\n\s*\n+', '\n', s).strip()

def question_body(q):
    return q.get(q.get('questionType')) or {}

def render_question(q):
    b = question_body(q)
    return {'question': html_to_text(b.get('question', '')),
            'solution': html_to_text(b.get('solution', '')),
            'answer': b.get('answer')}
