import csv, io, json, uuid
from pathlib import Path
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .analysis import analyse

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data'
ACTIONS_FILE = STORE / 'actions.json'
REPORTS_FILE = STORE / 'structured_reports.json'


def _load(path, default):
    try:
        if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    except Exception: pass
    return default

def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')

def index(request):
    return render(request,'detector/index.html')

def analyze(request):
    text = request.POST.get('report','').strip()
    result = analyse(text) if text else {'valid':False,'message':'Please enter a safety report.'}
    return render(request,'detector/index.html',{'result':result,'report':text})

def _risk(likelihood, severity):
    score = int(likelihood) * int(severity)
    if score >= 16: level = 'Critical'
    elif score >= 10: level = 'High'
    elif score >= 5: level = 'Medium'
    else: level = 'Low'
    return score, level

def report(request):
    result=None
    if request.method == 'POST':
        text=request.POST.get('description','').strip()
        result=analyse(text) if text else {'valid':False,'message':'Add a report description.'}
        likelihood=int(request.POST.get('likelihood','3') or 3); severity=int(request.POST.get('severity','4') or 4)
        score,level=_risk(likelihood,severity)
        if result.get('valid'):
            reports=_load(REPORTS_FILE,[])
            reports.append({'id':uuid.uuid4().hex[:8].upper(),'created':datetime.now().isoformat(timespec='minutes'),'title':request.POST.get('title','Untitled report'),'type':request.POST.get('event_type','Near Miss'),'location':request.POST.get('location','Not specified'),'description':text,'likelihood':likelihood,'severity':severity,'risk_score':score,'risk_level':level,'classification':result['label']})
            _save(REPORTS_FILE,reports)
            result['risk_score']=score; result['risk_level']=level; result['saved']=True
    return render(request,'detector/report.html',{'result':result})

def actions(request):
    actions=_load(ACTIONS_FILE,[])
    if request.method=='POST':
        item={'id':uuid.uuid4().hex[:7].upper(),'action':request.POST.get('action','').strip(),'owner':request.POST.get('owner','HSE Team'),'due':request.POST.get('due',''),'priority':request.POST.get('priority','High'),'status':'Open','created':date.today().isoformat()}
        if item['action']:
            actions.append(item); _save(ACTIONS_FILE,actions)
    if request.GET.get('complete'):
        for a in actions:
            if a['id']==request.GET['complete']: a['status']='Completed'
        _save(ACTIONS_FILE,actions)
    return render(request,'detector/actions.html',{'actions':actions})

def controls(request):
    controls=[
        ('Energy isolation / LOTO','Isolation verified before breaking containment or starting work.'),
        ('Gas testing','Atmosphere tested and continuously monitored where required.'),
        ('Permit to work','Correct permit issued, understood and displayed.'),
        ('Line-of-fire / exclusion zone','People kept outside credible struck-by or dropped-object zones.'),
        ('Fall protection','Anchorage, harness and edge protection verified for work at height.'),
        ('Machine guarding / interlocks','Guards and safety interlocks intact and functional.'),
        ('Critical lifting controls','Lift plan, competent operator, rigging and exclusion zone verified.'),
        ('Vehicle / pedestrian segregation','Route, spotter and speed controls verified where applicable.'),
    ]
    submitted=False
    if request.method=='POST': submitted=True
    return render(request,'detector/controls.html',{'controls':controls,'submitted':submitted})

def inspections(request):
    checks=['Housekeeping and access','PPE compliance','Emergency equipment','Machine guarding','Electrical isolation','Fire prevention','Permit compliance','Lifting controls','Confined-space controls','Vehicle movement controls']
    submitted=False
    if request.method=='POST': submitted=True
    return render(request,'detector/inspections.html',{'checks':checks,'submitted':submitted})

def rca(request):
    saved=False
    if request.method=='POST':
        saved=True
    categories=['Human factors','Procedure / work instruction','Equipment / engineering','Supervision / assurance','Planning / scheduling','Environment / workplace','Management system']
    return render(request,'detector/rca.html',{'categories':categories,'saved':saved})

def export_reports(request):
    rows=_load(REPORTS_FILE,[])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename="sif_structured_reports.csv"'
    writer=csv.writer(response); writer.writerow(['ID','Title','Type','Location','Classification','Likelihood','Severity','Risk Score','Risk Level','Created'])
    for r in rows: writer.writerow([r.get('id'),r.get('title'),r.get('type'),r.get('location'),r.get('classification'),r.get('likelihood'),r.get('severity'),r.get('risk_score'),r.get('risk_level'),r.get('created')])
    return response

def analytics(request):
    rows=_load(REPORTS_FILE,[])
    counts={x:0 for x in ['SIF Potential','Needs HSE Review','Non-SIF']}
    risks={'Critical':0,'High':0,'Medium':0,'Low':0}
    for r in rows:
        counts[r.get('classification','Needs HSE Review')]=counts.get(r.get('classification','Needs HSE Review'),0)+1
        risks[r.get('risk_level','Medium')]=risks.get(r.get('risk_level','Medium'),0)+1
    return render(request,'detector/analytics.html',{'rows':rows,'counts':counts,'risks':risks,'total':len(rows),'sif_count':counts.get('SIF Potential',0),'review_count':counts.get('Needs HSE Review',0),'non_sif_count':counts.get('Non-SIF',0),'critical_count':risks.get('Critical',0),'high_count':risks.get('High',0),'medium_count':risks.get('Medium',0),'low_count':risks.get('Low',0)})

def dashboard(request):
    actions=_load(ACTIONS_FILE,[]); reports=_load(REPORTS_FILE,[])
    return render(request,'detector/dashboard.html',{'open_actions':sum(a.get('status')!='Completed' for a in actions),'reports':len(reports),'completed_actions':sum(a.get('status')=='Completed' for a in actions)})

def batch_analyze(request):
    rows=None; error=None
    if request.method=='POST':
        upload=request.FILES.get('csv_file')
        if not upload: error='Please choose a CSV file.'
        else:
            try:
                decoded=upload.read().decode('utf-8-sig'); reader=csv.DictReader(io.StringIO(decoded))
                if 'report' not in (reader.fieldnames or []): raise ValueError("CSV must contain a column named 'report'.")
                rows=[]
                for row in reader:
                    text=(row.get('report') or '').strip(); r=analyse(text)
                    rows.append({'report':text,'classification':r.get('label','Needs Input') if r.get('valid') else 'Needs Input','probability':f"{r.get('sif_probability','-')}%" if r.get('valid') else '-','rule':', '.join(r.get('life_saving_rules',[])) if r.get('valid') else '-','barrier':', '.join(r.get('entities',{}).get('Barrier Failure',[])) or '—' if r.get('valid') else '-'})
            except Exception as exc: error=str(exc)
    return render(request,'detector/batch.html',{'rows':rows,'error':error})
