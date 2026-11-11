"""Autonomous publishing. Requires OPENAI_API_KEY; API usage may cost money."""
import os, re, json, sys, datetime, pathlib, hashlib
from zoneinfo import ZoneInfo
import feedparser, yaml
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOW = datetime.datetime.now(ZoneInfo('Europe/Oslo'))
TOPIC = os.getenv('TOPIC', '').strip()
MANUAL = os.getenv('MANUAL', 'false').lower() == 'true'
if not MANUAL and (NOW.weekday() >= 5 or NOW.hour != 10):
    print('Not scheduled Oslo publication time'); sys.exit(0)
if not os.getenv('OPENAI_API_KEY'):
    print('OPENAI_API_KEY missing: no publication'); sys.exit(0)
if not TOPIC:
    feeds = [s.strip() for s in (os.getenv('RSS_FEEDS') or 'https://www.nrk.no/toppsaker.rss').split(',') if s.strip()]
    items=[]
    for url in feeds:
        parsed=feedparser.parse(url)
        for item in parsed.entries[:15]:
            if item.get('title') and item.get('link'):
                items.append({'title':item.title,'url':item.link,'summary':re.sub('<[^>]*>','',item.get('summary',''))[:350]})
    if not items:
        print('No RSS items; skipping');sys.exit(0)
else:
    items=[]

posts=ROOT/'_posts'
existing='\n'.join(p.read_text(encoding='utf-8')[:400] for p in posts.glob('*.md'))[-12000:]
count=sum(1 for p in posts.glob(f'{NOW:%Y-%m-%d}-*.md') if '-ekstra-' not in p.name)
remaining=(1 if MANUAL else max(0,3-count))
if remaining == 0:
    print('Daily quota reached');sys.exit(0)

prompt=f'''Du er en nøktern norsk redaktør. Dato {NOW.isoformat()}.
Oppgave: {('Ekstraordinær sak: '+TOPIC) if TOPIC else 'Velg inntil '+str(remaining)+' vesentlige nyheter fra RSS-listen.'}
RSS-kandidater: {json.dumps(items,ensure_ascii=False)[:15000]}
Allerede publisert: {existing}
IKKE dikt opp fakta, sitater, hendelser, datoer eller kildehenvisninger.
Du har ingen egen nettsøktilgang i dette programmet. RSS er bare innspill, ikke bekreftelse.
Publiser bare dersom det foreligger tilstrekkelig konkret, etterprøvbar dokumentasjon i innspillene.
Hvis du ikke kan kontrollere faktapåstander mot minst to uavhengige dokumenterte kilder, returner tom articles-liste.
Hvis manuell TOPIC mangler dokumenterte kilder, returner tom liste. Ikke fabrikkér.
Returner gyldig JSON-objekt med articles: liste (maks {remaining}) av objekter med title, description, category, tags (liste), body_markdown, sources (liste av https-URLer).
Body skal være på norsk bokmål, saklig og selvstendig, med kildelenker. Ingen markedsføring.'''
client=OpenAI()
res=client.responses.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),input=prompt)
raw=res.output_text.strip()
if raw.startswith('```'):
    raw=re.sub(r'^```(?:json)?\s*|\s*```$','',raw)
try: data=json.loads(raw)
except json.JSONDecodeError:
    print('Invalid model JSON; skipping');sys.exit(0)
for article in data.get('articles',[])[:remaining]:
    if not all(article.get(k) for k in ('title','description','body_markdown','sources')):continue
    sources=article['sources']
    if not isinstance(sources,list) or len(set(sources))<2 or not all(isinstance(s,str) and s.startswith('https://') for s in sources):continue
    # Automatic mode must reference provided RSS source URLs; source URLs alone are not verification.
    if not TOPIC and not any(s in {i['url'] for i in items} for s in sources):continue
    slug=re.sub(r'[^a-z0-9]+','-',article['title'].lower().replace('æ','ae').replace('ø','o').replace('å','a')).strip('-')[:65]
    slug=slug or hashlib.sha256(article['title'].encode()).hexdigest()[:12]
    filename=posts/f'{NOW:%Y-%m-%d}-{"ekstra-" if MANUAL else ""}{slug}.md'
    if filename.exists():continue
    category=re.sub('[^a-z0-9-]','',str(article.get('category','samfunn')).lower()) or 'samfunn'
    front={'layout':'post','title':article['title'],'description':article['description'],'date':NOW.isoformat(),'categories':[category],'tags':article.get('tags',[])[:12]}
    body=article['body_markdown']+'\n\n## Kilder\n'+''.join(f'\n- {s}' for s in sources)+'\n'
    filename.write_text('---\n'+yaml.safe_dump(front,allow_unicode=True,sort_keys=False)+'---\n\n'+body,encoding='utf-8')
    print('Created',filename.name)
