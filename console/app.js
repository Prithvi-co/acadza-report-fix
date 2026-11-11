/* Acadza report review console - static, loads precomputed triage results. */
let DATA=null, cases=[], selected=null, filter='all', query='';
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

const URGENCY={defect:100,syllabus:0,app_issue:10,display_issue:10,language_mode:10,already_fixed:5,not_actionable:0,no_error:0};
const REPAIR_W={answer_key:50,wrong_question:45,unsound:45,option_repair:40,identical_options:35,diagram:35,stem_data:30,type_mismatch:30,wrong_chapter:25,solution_fix:20,solution_missing:20,syllabus:25,spelling:5,noise:5,exam_reference:5,markup_leak:10,notation:10,answer_form:10};

function urgency(c){
  let s=URGENCY[c.results[0].verdict]||0;
  if(c.results[0].repair) s+=REPAIR_W[c.results[0].repair]||0;
  if(c.results.some(r=>r.route==='faculty_review')) s+=20;
  s+=15*(c.reports.length-1);
  return s;
}
function auditKey(rid){return 'acadza_audit_'+rid}
function getAudit(rid){try{return JSON.parse(localStorage.getItem(auditKey(rid))||'[]')}catch(e){return[]}}
function logAudit(rid,action,note){
  const a=getAudit(rid); a.push({action,note:note||'',at:new Date().toISOString(),by:'faculty (local demo)'});
  localStorage.setItem(auditKey(rid),JSON.stringify(a));
}
function statusOf(rid){const a=getAudit(rid);return a.length?a[a.length-1].action:null}
function patchKey(qid){return 'acadza_patch_'+qid}
function getPatch(qid){try{return JSON.parse(localStorage.getItem(patchKey(qid))||'null')}catch(e){return null}}
function setPatch(qid,p){localStorage.setItem(patchKey(qid),JSON.stringify(p))}
function clearPatch(qid){localStorage.removeItem(patchKey(qid))}

fetch('data.json').then(r=>r.json()).then(d=>{
  DATA=d;
  const byQ={};
  d.reports.forEach(r=>{(byQ[r.questionId]=byQ[r.questionId]||[]).push(r)});
  const resByR={}; d.results.forEach(r=>resByR[r.reportId]=r);
  cases=Object.entries(byQ).map(([qid,reps])=>({
    qid, q:d.questions.find(q=>q._id===qid), reports:reps,
    results:reps.map(r=>resByR[r.reportId])
  }));
  cases.forEach(c=>c.urg=urgency(c));
  cases.sort((a,b)=>b.urg-a.urg);
  const h=location.hash.match(/q=([a-f0-9]+)/);
  if(h) selected=cases.find(c=>c.qid.includes(h[1]))||cases[0];
  renderStats(); renderQueue();
  if(selected) renderDetail();
});

function renderStats(){
  const R=DATA.results;
  const nDef=R.filter(r=>r.verdict==='defect').length;
  const nRev=R.filter(r=>r.route==='faculty_review').length;
  const nAuto=R.filter(r=>r.route==='auto_apply').length;
  const nDone=R.filter(r=>statusOf(r.reportId)).length;
  $('#stats').innerHTML=`<span><b>${cases.length}</b> of ${DATA.questions.length} questions reported</span><span><b>${R.length}</b> reports</span><span><b>${nDef}</b> defects</span><span><b>${nRev}</b> need review</span><span><b>${nAuto}</b> auto-eligible</span><span><b>${nDone}</b> actioned</span>`;
}
const ROUTE_LABEL={auto_apply:'auto-eligible',faculty_review:'faculty review',no_change:'no change'};

function renderQueue(){
  const el=$('#cases'); el.innerHTML='';
  cases.forEach(c=>{
    const r0=c.results[0];
    if(filter==='review'&&!c.results.some(r=>r.route==='faculty_review'))return;
    if(filter==='auto'&&!c.results.some(r=>r.route==='auto_apply'))return;
    if(filter==='defect'&&r0.verdict!=='defect')return;
    const hay=(c.q.chapter+' '+c.qid+' '+c.reports.map(r=>r.comment).join(' ')).toLowerCase();
    if(query&&!hay.includes(query))return;
    const st=statusOf(c.reports[0].reportId);
    const div=document.createElement('div');
    div.className='case'+(selected===c?' sel':'');
    div.innerHTML=`<div class="top"><span class="q">${esc(c.q.chapter||c.q.subject)}</span><span class="chap">${c.qid.slice(-6)} · ${c.reports.length} report${c.reports.length>1?'s':''}</span></div>
    <div class="comment">"${esc(c.reports[0].comment)}"</div>
    <div class="chips">
      <span class="chip ${r0.verdict==='defect'?'defect':'no_error'}">${esc(r0.verdict)}</span>
      ${r0.repair?`<span class="chip">${esc(r0.repair)}</span>`:''}
      <span class="chip ${r0.route==='faculty_review'?'review':r0.route==='auto_apply'?'auto':''}">${ROUTE_LABEL[r0.route]}</span>
      ${st?`<span class="chip no_error">${esc(st)}</span>`:''}
    </div>`;
    div.onclick=()=>{selected=c;renderQueue();renderDetail()};
    el.appendChild(div);
  });
}

function fieldRaw(q,field,usePatch){
  const b=q[q.questionType]||{};
  let v;
  if(field==='question'||field==='solution')v=b[field]||'';
  else if(field==='answer')v=JSON.stringify(b.answer);
  else v=q[field]??'';
  const p=usePatch===false?null:getPatch(q._id);
  if(p&&p.field===field&&p.find!=null)v=v.split(p.find).join(p.replace);
  return v;
}
function applyEdit(raw,edit){
  if(!edit||edit.find==null)return raw;
  return raw.split(edit.find).join('<mark>'+esc(edit.replace)+'</mark>');
}

function renderDetail(){
  const d=$('#detail'); const c=selected; if(!c)return;
  const q=c.q, r0=c.results[0];
  const b=q[q.questionType]||{};
  const st=statusOf(c.reports[0].reportId);
  const patch=getPatch(q._id);
  const qHtml=fieldRaw(q,'question');
  const solHtml=fieldRaw(q,'solution');
  let diffHtml='<div class="ev">No edit proposed - nothing to apply.</div>';
  if(r0.edit){
    const raw=fieldRaw(q,r0.edit.field,false);
    const after=raw.split(r0.edit.find).join('<mark>'+esc(r0.edit.replace)+'</mark>');
    if(r0.edit.field==='answer'||r0.edit.field==='questionType'){
      diffHtml=`<div class="diff"><div class="col"><h4>Original (${esc(r0.edit.field)})</h4><div class="rendered before">${esc(raw)}</div></div>
      <div class="col"><h4>Proposed</h4><div class="rendered after"><mark>${esc(r0.edit.replace)}</mark></div></div></div>`;
    }else{
      diffHtml=`<div class="diff"><div class="col"><h4>Original (${esc(r0.edit.field)})</h4><div class="rendered before">${raw}</div></div>
      <div class="col"><h4>Proposed</h4><div class="rendered after">${after}</div></div></div>`;
    }
    diffHtml+='<div class="audit" style="margin-top:6px">Proposal only - applying writes to a local sandbox copy in this browser, never to Acadza.</div>';
  }
  const audit=c.reports.flatMap(r=>getAudit(r.reportId).map(a=>({...a,rid:r.reportId})));
  const canApply=!!r0.edit;
  d.innerHTML=`
  <div class="card"><h3>Question ${patch?'<span class="patched-badge">PATCHED - sandbox copy</span> <button class="toggle" id="bOrig">view original</button>':''}</h3>
    <div class="meta"><span>${esc(q.subject)} · ${esc(q.chapter)}</span><span>type: ${esc(q.questionType)}</span><span>level: ${esc(q.level||'-')}</span><span>key: <b>${esc(fieldRaw(q,'answer'))}</b></span>${st?`<span class="badge-done">${esc(st.toUpperCase())}</span>`:''}</div>
    <div class="rendered">${qHtml}</div>
    ${solHtml?`<h3 style="margin-top:12px">Stored solution</h3><div class="rendered" style="max-height:220px;overflow:auto">${solHtml}</div>`:''}
  </div>
  <div class="card"><h3>Reports (${c.reports.length})</h3>
    ${c.reports.map(r=>`<div class="rep"><div class="who">${esc(r.reportId)} · ${esc(r.source)} · ${new Date(r.reportedAt).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})} IST</div><div class="c">"${esc(r.comment)}"</div></div>`).join('')}
  </div>
  <div class="card"><h3>AI triage</h3>
    <div class="chips" style="margin-bottom:10px">
      <span class="chip ${r0.verdict==='defect'?'defect':'no_error'}">verdict: ${esc(r0.verdict)}</span>
      ${r0.repair?`<span class="chip">repair: ${esc(r0.repair)}</span>`:''}
      <span class="chip ${r0.route==='faculty_review'?'review':r0.route==='auto_apply'?'auto':''}">${ROUTE_LABEL[r0.route]}</span>
      <span class="chip conf">heuristic confidence ${Math.round(r0.confidence*100)}%</span>
    </div>
    <div class="confbar"><i style="width:${Math.round(r0.confidence*100)}%"></i></div>
    <p class="ev" style="margin-top:10px">${esc(r0.evidence)}</p>
  </div>
  <div class="card"><h3>Proposed edit - original / proposed</h3>${diffHtml}</div>
  <div class="card"><h3>Student reply - preview only</h3><div class="reply"><div class="to">Not sent. This text goes out only AFTER a faculty decision${r0.edit?' and after the edit is actually applied':''} - right now nothing has been fixed or sent.</div>${esc(r0.student_reply)}</div></div>
  <div class="card"><h3>Decision</h3>
    <div class="actions">
      <button class="approve" id="bApprove">${canApply?'Approve - apply to sandbox copy':'Close case (no change)'}</button>
      ${canApply?'<button class="editb" id="bEdit">Edit then approve</button>':''}
      <button class="reject" id="bReject">Reject</button>
    </div>
    <div id="editBox"></div>
    ${audit.length?`<h3 style="margin-top:12px">Audit trail</h3><ul class="audit">${Object.values(audit.reduce((g,a)=>{const k=a.action+'|'+a.note+'|'+a.at;(g[k]=g[k]||{...a,rids:[]}).rids.push(a.rid);return g},{})).map(a=>`<li>${esc(new Date(a.at).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'}))} IST - ${esc(a.action)} (${a.rids.map(esc).join(', ')})${a.note?': '+esc(a.note):''}</li>`).join('')}</ul>`:''}
  </div>`;
  const origBtn=$('#bOrig');
  if(origBtn)origBtn.onclick=()=>{clearPatch(q._id);c.reports.forEach(r=>logAudit(r.reportId,'reverted to original'));renderStats();renderQueue();renderDetail()};
  $('#bApprove').onclick=()=>{
    if(canApply)setPatch(q._id,{field:r0.edit.field,find:r0.edit.find,replace:r0.edit.replace});
    c.reports.forEach(r=>logAudit(r.reportId,canApply?'approved - edit applied to local sandbox copy':'closed - no change'));
    renderStats();renderQueue();renderDetail();
  };
  $('#bReject').onclick=()=>{const n=prompt('Reject reason (recorded in audit):');if(n!==null){c.reports.forEach(r=>logAudit(r.reportId,'rejected',n));renderStats();renderQueue();renderDetail()}};
  const eb=$('#bEdit');
  if(eb)eb.onclick=()=>{
    $('#editBox').innerHTML=`<textarea id="editNote" placeholder="Adjust the replacement text, then approve...">${r0.edit?esc(r0.edit.replace):''}</textarea><button class="approve" id="bSave" style="margin-top:8px">Save edited approval</button>`;
    $('#bSave').onclick=()=>{
      setPatch(q._id,{field:r0.edit.field,find:r0.edit.find,replace:$('#editNote').value});
      c.reports.forEach(r=>logAudit(r.reportId,'approved (edited) - applied to local sandbox copy',$('#editNote').value));
      renderStats();renderQueue();renderDetail();
    };
  };
}

$('#filters').addEventListener('click',e=>{
  if(e.target.dataset.f){filter=e.target.dataset.f;
    document.querySelectorAll('#filters button').forEach(b=>b.classList.toggle('on',b===e.target));
    renderQueue();}
});
$('#search').addEventListener('input',e=>{query=e.target.value.toLowerCase();renderQueue()});
