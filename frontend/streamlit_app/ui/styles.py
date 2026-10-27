APP_CSS = """
<style>
:root {
  --cg-canvas:#F4F5F2; --cg-surface:#FFFFFF; --cg-muted:#EAEEE9;
  --cg-ink:#122028; --cg-ink-muted:#56636A; --cg-border:#CFD7D3;
  --cg-rail:#10232B; --cg-accent:#A55F16; --cg-focus:#126E82;
  --cg-low:#247A55; --cg-low-soft:#E3F1E9;
  --cg-watch:#855708; --cg-watch-soft:#F7ECD4;
  --cg-high:#B13A32; --cg-high-soft:#F8E5E2;
}
html { scroll-behavior:smooth; }
[data-testid="stAppViewContainer"] { background:var(--cg-canvas); color:var(--cg-ink); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"] { display:none !important; }
[data-testid="stSidebar"] { background:var(--cg-rail); border-right:0; }
[data-testid="stSidebarNav"] { display:none !important; }
[data-testid="stSidebar"] * { color:#F4F7F5; }
[data-testid="stSidebar"] .stCaption { color:#B9C6C3 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="select"] input {
  color:var(--cg-ink) !important;
}
.cg-nav { display:grid; gap:.35rem; margin:.2rem 0 .7rem; }
.cg-nav a { color:#F4F7F5 !important; min-height:44px; display:flex; align-items:center; padding:.35rem .45rem; border-left:2px solid transparent; text-decoration:none; font-weight:700; }
.cg-nav a:hover { border-left-color:var(--cg-accent); background:rgba(255,255,255,.05); }
.cg-nav a:focus-visible { outline:3px solid #62AFC0; outline-offset:2px; }
[data-testid="stMainBlockContainer"] { max-width:1280px; padding-top:2.5rem; padding-bottom:4rem; }
h1,h2,h3 { color:var(--cg-ink); letter-spacing:-0.025em; }
h1 { font-size:2rem !important; line-height:1.2 !important; }
h2 { font-size:1.35rem !important; margin-top:.35rem !important; }
h3 { font-size:1.05rem !important; }
p, label, .stCaption { color:var(--cg-ink-muted); }
.stButton > button, .stFormSubmitButton > button {
  min-height:44px; border-radius:6px; font-weight:700;
  border:1px solid var(--cg-ink); transition:transform 140ms ease, background 140ms ease;
}
.stFormSubmitButton > button { background:var(--cg-ink); color:white; }
.stFormSubmitButton > button p { color:white !important; }
[data-testid="stBaseButton-primary"] p { color:white !important; }
.stButton > button:hover, .stFormSubmitButton > button:hover { transform:translateY(-1px); border-color:var(--cg-accent); }
button:focus-visible, input:focus-visible, [data-baseweb="select"] *:focus-visible {
  outline:3px solid var(--cg-focus) !important; outline-offset:2px;
}
div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
  border-radius:6px !important; min-height:44px; background:var(--cg-surface);
}
[data-testid="stVerticalBlockBorderWrapper"] {
  background:var(--cg-surface); border-color:var(--cg-border) !important; border-radius:8px;
}
.cg-kicker { color:var(--cg-accent); font-size:.75rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin:0 0 .5rem; }
.cg-mobile-brand { display:none; color:var(--cg-ink); font-weight:800; padding-bottom:.75rem; border-bottom:1px solid var(--cg-border); margin-bottom:1rem; }
.cg-subhead { max-width:760px; font-size:1rem; line-height:1.55; color:var(--cg-ink-muted); margin-bottom:1.35rem; }
.cg-demo {
  border-left:3px solid var(--cg-accent); padding:.7rem .9rem; background:#FFF8EE;
  color:#674412; font-size:.86rem; margin:.3rem 0 1.25rem; border-radius:0 6px 6px 0;
}
.cg-field-error { color:#A52F2F; font-size:.8rem; font-weight:650; margin:-.25rem 0 .55rem; }
.cg-empty { padding:3rem 1.25rem; text-align:center; border:1px dashed #AAB7B2; border-radius:8px; background:rgba(255,255,255,.45); }
.cg-empty strong { display:block; color:var(--cg-ink); font-size:1.05rem; margin-bottom:.4rem; }
.cg-risk { padding:1.25rem 0 1rem; border-top:3px solid var(--risk); border-bottom:1px solid var(--cg-border); }
.cg-risk-head { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; }
.cg-score { font-size:3.25rem; line-height:1; font-weight:780; letter-spacing:-.055em; color:var(--cg-ink); font-variant-numeric:tabular-nums; }
.cg-score-label { font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; font-weight:800; color:var(--cg-ink-muted); margin-bottom:.45rem; }
.cg-band { display:inline-flex; align-items:center; min-height:32px; padding:.25rem .7rem; border:1px solid var(--risk); border-radius:999px; color:var(--risk); background:var(--risk-soft); font-weight:800; white-space:nowrap; }
.cg-meter { position:relative; height:10px; margin:1.2rem 0 .45rem; border-radius:2px; background:#DCE2DE; overflow:visible; }
.cg-meter-fill { width:var(--score); height:100%; background:var(--risk); border-radius:2px; }
.cg-threshold { position:absolute; left:50%; top:-5px; width:2px; height:20px; background:var(--cg-ink); }
.cg-meter-note { display:flex; justify-content:space-between; font-size:.76rem; color:var(--cg-ink-muted); }
.cg-brief { color:var(--cg-ink); font-size:.96rem; line-height:1.55; margin:.9rem 0 0; }
.cg-driver { display:grid; grid-template-columns:38px 1fr auto; gap:.8rem; padding:1rem 0; border-top:1px solid var(--cg-border); }
.cg-rank { color:var(--cg-ink-muted); font-size:.75rem; font-weight:800; letter-spacing:.08em; padding-top:.15rem; }
.cg-driver-title { color:var(--cg-ink); font-weight:750; margin-bottom:.2rem; }
.cg-driver-copy { color:var(--cg-ink-muted); font-size:.86rem; line-height:1.5; }
.cg-impact { font-variant-numeric:tabular-nums; font-weight:800; color:var(--direction); white-space:nowrap; }
.cg-action { border-left:4px solid var(--cg-accent); background:#FFF8EE; padding:1rem 1.1rem; margin-top:1rem; }
.cg-action-title { color:var(--cg-ink); font-weight:800; margin-bottom:.35rem; }
.cg-action ul { margin:.65rem 0 0; padding-left:1.15rem; color:#594728; }
.cg-meta { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; padding:.9rem 0; border-bottom:1px solid var(--cg-border); }
.cg-meta-item span { display:block; font-size:.7rem; text-transform:uppercase; letter-spacing:.07em; font-weight:800; color:var(--cg-ink-muted); }
.cg-meta-item strong { display:block; color:var(--cg-ink); font-size:.87rem; margin-top:.2rem; overflow-wrap:anywhere; }
.cc-statusline {
  display:grid; grid-template-columns:1.1fr 1.2fr 1fr; border-top:1px solid var(--cg-border);
  border-bottom:1px solid var(--cg-border); margin:1rem 0 1.5rem; padding:.8rem 0; gap:1rem;
}
.cc-statusline span, .cc-queue span {
  display:block; color:var(--cg-ink-muted); font-size:.68rem; line-height:1.35;
  font-weight:800; letter-spacing:.08em; text-transform:uppercase;
}
.cc-statusline strong { display:block; color:var(--cg-ink); font-size:.84rem; margin-top:.2rem; }
.cc-kpis {
  display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); border-top:3px solid var(--cg-ink);
  border-bottom:1px solid var(--cg-border); margin:0 0 1.2rem;
}
.cc-kpis > div { padding:1rem 1.1rem; border-right:1px solid var(--cg-border); }
.cc-kpis > div:last-child { border-right:0; }
.cc-kpis span { display:block; min-height:2.3em; color:var(--cg-ink-muted); font-size:.72rem; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }
.cc-kpis strong { display:block; color:var(--cg-ink); font-size:1.75rem; line-height:1.15; margin:.25rem 0; font-variant-numeric:tabular-nums; }
.cc-kpis small { color:var(--cg-ink-muted); font-size:.74rem; }
.cc-attention { padding:.7rem .9rem; border-left:3px solid var(--cg-high); background:var(--cg-high-soft); color:#64251F; margin:0 0 1.5rem; }
.cc-queue { border-top:1px solid var(--cg-ink); margin-bottom:2rem; }
.cc-queue-head, .cc-queue-row {
  display:grid; grid-template-columns:1.1fr .55fr .75fr 1.45fr .55fr .95fr 1fr .65fr;
  align-items:center; gap:.75rem; padding:.65rem .55rem;
}
.cc-queue-head { color:var(--cg-ink-muted); font-size:.67rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; border-bottom:1px solid var(--cg-border); }
.cc-queue-row { min-height:64px; border-bottom:1px solid var(--cg-border); font-size:.8rem; }
.cc-queue-row > div > span { display:none; }
.cc-queue-row strong { color:var(--cg-ink); font-size:.8rem; overflow-wrap:anywhere; }
.cc-customer strong { font-weight:800; }
.cc-risk { font-size:.76rem; white-space:nowrap; }
.cc-risk.high { color:var(--cg-high); }
.cc-risk.watch { color:var(--cg-watch); }
.cc-risk.low { color:var(--cg-low); }
.cc-inspect, .cc-review-item a, .cc-empty a {
  color:#115C6B; font-weight:800; text-decoration:underline; text-underline-offset:3px;
}
.cc-inspect:focus-visible, .cc-review-item a:focus-visible, .cc-empty a:focus-visible {
  outline:3px solid var(--cg-focus); outline-offset:3px; border-radius:2px;
}
.cc-distribution { border-top:1px solid var(--cg-border); padding-top:.35rem; }
.cc-dist-row { padding:.65rem 0; border-bottom:1px solid var(--cg-border); }
.cc-dist-row > div:first-child { display:flex; justify-content:space-between; gap:1rem; font-size:.8rem; margin-bottom:.4rem; }
.cc-dist-row span { color:var(--cg-ink-muted); }
.cc-dist-track { height:10px; background:#DCE2DE; border-radius:2px; overflow:hidden; }
.cc-dist-fill { height:100%; min-width:2px; }
.cc-dist-fill.high { background:var(--cg-high); }
.cc-dist-fill.watch { background:var(--cg-watch); }
.cc-dist-fill.low { background:var(--cg-low); }
.cc-distribution p { color:var(--cg-ink-muted); font-size:.8rem; margin:.75rem 0 0; }
.cc-review-list { border-top:1px solid var(--cg-border); }
.cc-review-item { display:grid; grid-template-columns:1fr 2fr; gap:.25rem 1rem; padding:.75rem 0; border-bottom:1px solid var(--cg-border); }
.cc-review-item > span { color:var(--cg-ink-muted); font-size:.65rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; }
.cc-review-item > strong { color:var(--cg-ink); }
.cc-review-item p { grid-column:2; font-size:.8rem; line-height:1.45; margin:0; }
.cc-review-item a, .cc-review-item em { grid-column:2; font-size:.78rem; }
.cc-review-item em { color:var(--cg-ink-muted); font-style:normal; }
.cc-activity-list, .cc-model-state { border-top:1px solid var(--cg-border); }
.cc-activity-row { display:grid; grid-template-columns:1.6fr .75fr .4fr .6fr; align-items:center; gap:.75rem; padding:.72rem 0; border-bottom:1px solid var(--cg-border); font-size:.78rem; }
.cc-activity-row > div span { display:block; color:var(--cg-ink-muted); margin-top:.15rem; }
.cc-activity-row time { color:var(--cg-ink-muted); font-variant-numeric:tabular-nums; }
.cc-model-state { padding-top:.75rem; }
.cc-model-state > strong { color:var(--cg-watch); }
.cc-model-state p { font-size:.82rem; line-height:1.45; }
.cc-model-state dl { margin:.75rem 0 0; }
.cc-model-state dl div { display:flex; justify-content:space-between; gap:1rem; padding:.45rem 0; border-top:1px solid var(--cg-border); font-size:.76rem; }
.cc-model-state dt { color:var(--cg-ink-muted); }
.cc-model-state dd { color:var(--cg-ink); text-align:right; margin:0; font-weight:700; }
.cc-empty { border:1px dashed #AAB7B2; padding:2rem; text-align:center; background:rgba(255,255,255,.45); }
.cc-empty strong { display:block; color:var(--cg-ink); font-size:1.05rem; }
.cc-empty p { margin:.4rem 0 .8rem; }
.ch-clear-label {
  min-height:1.62rem; display:flex; align-items:flex-end; padding-bottom:.3rem;
  color:var(--cg-ink-muted); font-size:.875rem;
}
.ch-results-summary {
  display:flex; align-items:baseline; gap:.35rem; padding:.65rem 0;
  border-top:1px solid var(--cg-ink); color:var(--cg-ink-muted); font-size:.8rem;
}
.ch-results-summary strong {
  color:var(--cg-ink); font-size:1.1rem; font-variant-numeric:tabular-nums;
}
.ch-table-wrap { width:100%; }
.ch-table {
  width:100%; border-collapse:collapse; table-layout:fixed; background:transparent;
  color:var(--cg-ink); font-size:.7rem; line-height:1.35;
}
.ch-table caption {
  position:absolute; width:1px; height:1px; padding:0; margin:-1px;
  overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
}
.ch-table th, .ch-table td {
  padding:.8rem .42rem; border-bottom:1px solid var(--cg-border);
  text-align:left; vertical-align:middle; overflow-wrap:anywhere;
}
.ch-table thead th {
  color:var(--cg-ink-muted); font-size:.63rem; letter-spacing:.055em;
  text-transform:uppercase; font-weight:800; border-bottom-color:var(--cg-ink);
}
.ch-table tbody th { font-weight:800; }
.ch-table th:nth-child(1) { width:11%; }
.ch-table th:nth-child(2) { width:8%; }
.ch-table th:nth-child(3) { width:10%; }
.ch-table th:nth-child(4) { width:14%; }
.ch-table th:nth-child(5) { width:7%; }
.ch-table th:nth-child(6) { width:10%; }
.ch-table th:nth-child(7) { width:14%; }
.ch-table th:nth-child(8) { width:15%; }
.ch-table th:nth-child(9) { width:8%; }
.ch-probability { font-weight:850; font-size:.84rem; font-variant-numeric:tabular-nums; }
.ch-mobile-list { display:none; list-style:none; margin:0; padding:0; }
.ch-card { padding:1rem 0 1.15rem; border-bottom:1px solid var(--cg-border); }
.ch-card:first-child { border-top:1px solid var(--cg-ink); }
.ch-card-head {
  display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;
}
.ch-card span, .ch-card dt {
  display:block; color:var(--cg-ink-muted); font-size:.65rem; font-weight:800;
  letter-spacing:.07em; text-transform:uppercase;
}
.ch-card-head strong { color:var(--cg-ink); font-size:.9rem; }
.ch-card-signal {
  display:grid; grid-template-columns:.8fr 1.2fr; gap:1rem; margin:.9rem 0;
}
.ch-card-signal strong {
  display:block; color:var(--cg-ink); font-size:.86rem; margin-top:.2rem;
}
.ch-card-signal > div:first-child strong {
  font-size:1.55rem; line-height:1; font-variant-numeric:tabular-nums;
}
.ch-card details { margin:.25rem 0 .9rem; }
.ch-card summary {
  min-height:44px; display:flex; align-items:center; color:#115C6B;
  font-size:.78rem; font-weight:800; cursor:pointer;
}
.ch-card summary:focus-visible { outline:3px solid var(--cg-focus); outline-offset:2px; }
.ch-card dl { margin:0 0 .75rem; }
.ch-card dl div {
  display:flex; justify-content:space-between; gap:1rem; padding:.45rem 0;
  border-top:1px solid var(--cg-border);
}
.ch-card dd {
  color:var(--cg-ink); font-size:.76rem; font-weight:700; text-align:right; margin:0;
}
.cd-actions {
  display:flex; align-items:center; flex-wrap:wrap; gap:.65rem 1.1rem;
  padding:.1rem 0 1rem; border-bottom:1px solid var(--cg-border); margin-bottom:1.25rem;
}
.cd-actions a, .cd-state a {
  color:#115C6B; font-size:.8rem; font-weight:800; text-decoration:underline;
  text-underline-offset:3px; min-height:44px; display:inline-flex; align-items:center;
}
.cd-actions a:focus-visible, .cd-state a:focus-visible {
  outline:3px solid var(--cg-focus); outline-offset:3px; border-radius:2px;
}
.cd-identity {
  display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); margin:1.1rem 0 1.5rem;
  border-top:1px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
}
.cd-identity > div { padding:.8rem .9rem; border-right:1px solid var(--cg-border); }
.cd-identity > div:last-child { border-right:0; }
.cd-identity span, .cd-risk-top span, .cd-driver-value span,
.cd-recommendation > span {
  display:block; color:var(--cg-ink-muted); font-size:.66rem; font-weight:800;
  letter-spacing:.07em; text-transform:uppercase;
}
.cd-identity strong { display:block; color:var(--cg-ink); font-size:.82rem; margin-top:.22rem; }
.cd-risk {
  --detail-risk:var(--cg-high); --detail-soft:var(--cg-high-soft);
  border-top:3px solid var(--detail-risk); border-bottom:1px solid var(--cg-border);
  padding:1rem 0;
}
.cd-risk.low { --detail-risk:var(--cg-low); --detail-soft:var(--cg-low-soft); }
.cd-risk.watch { --detail-risk:var(--cg-watch); --detail-soft:var(--cg-watch-soft); }
.cd-risk-top { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; }
.cd-risk-top > div > strong {
  display:block; color:var(--cg-ink); font-size:3.25rem; line-height:1; margin-top:.35rem;
  letter-spacing:-.055em; font-variant-numeric:tabular-nums;
}
.cd-risk-top > b {
  color:var(--detail-risk); background:var(--detail-soft); border:1px solid var(--detail-risk);
  border-radius:999px; padding:.35rem .7rem; font-size:.75rem; white-space:nowrap;
}
.cd-meter { height:10px; position:relative; background:#DCE2DE; margin:1.1rem 0 .4rem; }
.cd-meter > div { height:100%; background:var(--detail-risk); }
.cd-meter > i {
  position:absolute; top:-5px; width:2px; height:20px; background:var(--cg-ink);
}
.cd-meter-labels { display:flex; justify-content:space-between; gap:.5rem; color:var(--cg-ink-muted); font-size:.7rem; }
.cd-risk > p { color:var(--cg-ink); line-height:1.5; margin:.85rem 0 0; }
.cd-explanation {
  border-left:3px solid var(--cg-accent); background:#FFF8EE; padding:1rem 1.1rem;
  min-height:210px;
}
.cd-explanation > strong { color:var(--cg-ink); }
.cd-explanation p { color:#594728; line-height:1.55; }
.cd-explanation small { color:#6B583A; line-height:1.4; }
.cd-drivers { list-style:none; margin:0 0 1.5rem; padding:0; border-top:1px solid var(--cg-ink); }
.cd-driver {
  display:grid; grid-template-columns:42px minmax(0,1.7fr) .7fr .75fr;
  gap:1rem; align-items:center; padding:1rem .25rem; border-bottom:1px solid var(--cg-border);
}
.cd-driver-rank { color:var(--cg-ink-muted); font-size:.72rem; font-weight:850; letter-spacing:.08em; }
.cd-driver-main > strong { color:var(--cg-ink); }
.cd-driver-main p { margin:.2rem 0 0; font-size:.8rem; line-height:1.45; }
.cd-driver-signal span, .cd-driver-signal strong { display:block; font-size:.75rem; font-weight:800; }
.cd-driver.raises .cd-driver-signal { color:var(--cg-high); }
.cd-driver.lowers .cd-driver-signal { color:var(--cg-low); }
.cd-driver-value strong { display:block; color:var(--cg-ink); font-size:.77rem; margin-top:.2rem; }
.cd-recommendation {
  border-left:4px solid var(--cg-accent); background:#FFF8EE; padding:1rem 1.15rem;
  margin-bottom:1.5rem;
}
.cd-recommendation > strong { display:block; color:var(--cg-ink); margin:.35rem 0; }
.cd-recommendation ul { margin:.65rem 0; padding-left:1.2rem; color:#594728; }
.cd-recommendation small { color:#6B583A; }
.cd-context {
  display:grid; grid-template-columns:.8fr 1.1fr 1.1fr; border-top:1px solid var(--cg-ink);
  margin-bottom:1.6rem;
}
.cd-context section { padding:.9rem 1rem; border-right:1px solid var(--cg-border); }
.cd-context section:first-child { padding-left:0; }
.cd-context section:last-child { border-right:0; padding-right:0; }
.cd-context h3 { margin:.05rem 0 .75rem !important; }
.cd-context dl, .cd-prediction-context { margin:0; }
.cd-context dl > div, .cd-prediction-context > div {
  display:flex; justify-content:space-between; gap:1rem; padding:.42rem 0;
  border-top:1px solid var(--cg-border); font-size:.74rem;
}
.cd-context dt, .cd-prediction-context dt { color:var(--cg-ink-muted); }
.cd-context dd, .cd-prediction-context dd {
  color:var(--cg-ink); text-align:right; font-weight:700; margin:0; overflow-wrap:anywhere;
}
.cd-prediction-context {
  display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); border-top:1px solid var(--cg-ink);
}
.cd-prediction-context > div { padding:.7rem .8rem; }
.cd-state {
  border:1px dashed #AAB7B2; padding:2rem; background:rgba(255,255,255,.45);
  max-width:760px;
}
.cd-state > strong { color:var(--cg-ink); font-size:1.05rem; }
.cd-state p { margin:.4rem 0 .7rem; }
.bp-idle, .bp-source {
  border:1px dashed #AAB7B2; padding:1.15rem; background:rgba(255,255,255,.45);
  margin:.2rem 0 1rem;
}
.bp-source { border-style:solid; border-left:3px solid var(--cg-accent); }
.bp-idle strong, .bp-source strong { color:var(--cg-ink); }
.bp-idle p, .bp-source p { margin:.3rem 0 0; }
.bp-validation {
  --bp-status:var(--cg-watch); --bp-soft:var(--cg-watch-soft);
  display:grid; grid-template-columns:1.05fr 1.4fr; gap:1.5rem;
  border-top:3px solid var(--bp-status); border-bottom:1px solid var(--cg-border);
  padding:1rem 0; margin-bottom:1rem;
}
.bp-validation.valid { --bp-status:var(--cg-low); --bp-soft:var(--cg-low-soft); }
.bp-validation.invalid { --bp-status:var(--cg-error); --bp-soft:var(--cg-high-soft); }
.bp-validation.empty { --bp-status:var(--cg-watch); --bp-soft:var(--cg-watch-soft); }
.bp-validation > div > span, .bp-summary span, .bp-result-signal span {
  display:block; color:var(--cg-ink-muted); font-size:.66rem; font-weight:800;
  letter-spacing:.07em; text-transform:uppercase;
}
.bp-validation > div > strong { display:block; color:var(--bp-status); font-size:1.05rem; margin:.25rem 0; }
.bp-validation > div > p { margin:.2rem 0; line-height:1.45; }
.bp-validation dl {
  display:grid; grid-template-columns:1fr 1fr; margin:0; border-left:1px solid var(--cg-border);
}
.bp-validation dl > div { padding:.45rem .8rem; border-bottom:1px solid var(--cg-border); }
.bp-validation dt { color:var(--cg-ink-muted); font-size:.67rem; text-transform:uppercase; font-weight:800; }
.bp-validation dd { color:var(--cg-ink); font-weight:800; margin:.15rem 0 0; }
.bp-issues { list-style:none; padding:0; margin:0 0 1rem; border-top:1px solid var(--cg-border); }
.bp-issues li {
  display:grid; grid-template-columns:.45fr 2fr; gap:.3rem 1rem;
  padding:.7rem 0; border-bottom:1px solid var(--cg-border);
}
.bp-issues li strong { color:var(--cg-error); font-size:.76rem; }
.bp-issues li span { color:var(--cg-ink); font-size:.8rem; }
.bp-preview table, .bp-results-table table { width:100%; border-collapse:collapse; table-layout:fixed; }
.bp-preview caption, .bp-results-table caption {
  position:absolute; width:1px; height:1px; padding:0; margin:-1px;
  overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
}
.bp-preview th, .bp-preview td, .bp-results-table th, .bp-results-table td {
  padding:.7rem .5rem; border-bottom:1px solid var(--cg-border);
  text-align:left; font-size:.75rem; overflow-wrap:anywhere;
}
.bp-preview th, .bp-results-table thead th {
  color:var(--cg-ink-muted); font-size:.64rem; font-weight:800;
  letter-spacing:.06em; text-transform:uppercase; border-bottom-color:var(--cg-ink);
}
.bp-summary {
  display:grid; grid-template-columns:repeat(5,minmax(0,1fr));
  border-top:3px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
  margin-bottom:1.2rem;
}
.bp-summary > div { padding:.9rem 1rem; border-right:1px solid var(--cg-border); }
.bp-summary > div:last-child { border-right:0; }
.bp-summary strong {
  display:block; color:var(--cg-ink); font-size:1.55rem; margin-top:.25rem;
  font-variant-numeric:tabular-nums;
}
.bp-distribution {
  display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem;
  margin-bottom:1.4rem;
}
.bp-dist-row { padding:.65rem 0; border-top:1px solid var(--cg-border); }
.bp-dist-row > div:first-child {
  display:flex; justify-content:space-between; gap:.8rem; font-size:.78rem; margin-bottom:.4rem;
}
.bp-dist-row span { color:var(--cg-ink-muted); }
.bp-dist-track { height:10px; background:#DCE2DE; }
.bp-dist-fill { height:100%; min-width:2px; }
.bp-dist-fill.high { background:var(--cg-high); }
.bp-dist-fill.watch { background:var(--cg-watch); }
.bp-dist-fill.low { background:var(--cg-low); }
.bp-results-table { margin-bottom:1rem; }
.bp-results-table th:nth-child(1) { width:16%; }
.bp-results-table th:nth-child(2) { width:10%; }
.bp-results-table th:nth-child(3) { width:15%; }
.bp-results-table th:nth-child(4) { width:27%; }
.bp-results-table th:nth-child(5) { width:10%; }
.bp-results-table th:nth-child(6) { width:20%; }
.bp-results-table tbody th { font-size:.76rem; }
.bp-probability { font-size:.9rem !important; font-weight:850; font-variant-numeric:tabular-nums; }
.bp-mobile-results { display:none; list-style:none; margin:0 0 1rem; padding:0; }
.bp-result-card { padding:1rem 0; border-bottom:1px solid var(--cg-border); }
.bp-result-card:first-child { border-top:1px solid var(--cg-ink); }
.bp-result-head { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; }
.bp-result-head > strong { color:var(--cg-ink); }
.bp-result-signal { display:grid; grid-template-columns:.7fr 1.3fr; gap:1rem; margin:.8rem 0; }
.bp-result-signal strong { display:block; color:var(--cg-ink); margin-top:.2rem; }
.bp-result-signal > div:first-child strong {
  font-size:1.5rem; line-height:1; font-variant-numeric:tabular-nums;
}
.bp-result-card p { font-size:.76rem; margin:.2rem 0 .7rem; }
.an-summary {
  display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
  border-top:3px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
  margin-bottom:1.35rem;
}
.an-summary > div { padding:.9rem 1rem; border-right:1px solid var(--cg-border); }
.an-summary > div:last-child { border-right:0; }
.an-summary span, .an-segment-card dt {
  display:block; color:var(--cg-ink-muted); font-size:.66rem; font-weight:800;
  letter-spacing:.07em; text-transform:uppercase;
}
.an-summary strong {
  display:block; color:var(--cg-ink); font-size:1.6rem; line-height:1.1;
  margin:.3rem 0; font-variant-numeric:tabular-nums;
}
.an-summary small { color:var(--cg-ink-muted); }
.an-panel {
  display:block; border-top:1px solid var(--cg-ink); min-height:150px;
  padding-top:.4rem; margin-bottom:1.2rem;
}
.an-bar-row { padding:.55rem 0; border-bottom:1px solid var(--cg-border); }
.an-bar-row > div:first-child {
  display:flex; justify-content:space-between; gap:1rem; font-size:.78rem; margin-bottom:.42rem;
}
.an-bar-row span { color:var(--cg-ink-muted); }
.an-bar-track, .an-volume-track { height:10px; background:#DCE2DE; }
.an-bar-fill { height:100%; min-width:2px; }
.an-bar-fill.high { background:var(--cg-high); }
.an-bar-fill.watch { background:var(--cg-watch); }
.an-bar-fill.low { background:var(--cg-low); }
.an-volume-row {
  display:grid; grid-template-columns:100px 1fr 28px; gap:.8rem; align-items:center;
  padding:.76rem 0; border-bottom:1px solid var(--cg-border); font-size:.78rem;
}
.an-volume-row time { color:var(--cg-ink); font-weight:750; }
.an-volume-row strong { color:var(--cg-ink); text-align:right; font-variant-numeric:tabular-nums; }
.an-volume-track > div { height:100%; background:var(--cg-focus); min-width:2px; }
.an-unavailable {
  display:grid; grid-template-columns:.38fr 1.62fr; gap:1rem;
  border-top:1px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
  padding:.85rem 0; margin-bottom:1.4rem;
}
.an-unavailable strong { color:var(--cg-watch); }
.an-unavailable p { margin:0; line-height:1.45; }
.an-insight {
  display:grid; grid-template-columns:.38fr 1.62fr; gap:1rem;
  border-left:3px solid var(--cg-accent); background:#FFF8EE; padding:.8rem 1rem;
  margin:.5rem 0 1rem;
}
.an-insight strong {
  color:#6B430E; font-size:.68rem; letter-spacing:.06em; text-transform:uppercase;
}
.an-insight span { color:#594728; font-size:.8rem; line-height:1.45; }
.an-segment-table table { width:100%; border-collapse:collapse; table-layout:fixed; }
.an-segment-table caption {
  position:absolute; width:1px; height:1px; padding:0; margin:-1px;
  overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
}
.an-segment-table th, .an-segment-table td {
  padding:.78rem .55rem; border-bottom:1px solid var(--cg-border);
  text-align:left; font-size:.76rem; overflow-wrap:anywhere;
}
.an-segment-table thead th {
  color:var(--cg-ink-muted); font-size:.64rem; font-weight:800;
  letter-spacing:.06em; text-transform:uppercase; border-bottom-color:var(--cg-ink);
}
.an-segment-table tbody th { color:var(--cg-ink); font-size:.78rem; }
.an-probability { font-size:.94rem !important; font-weight:850; font-variant-numeric:tabular-nums; }
.an-mobile-segments { display:none; list-style:none; padding:0; margin:0; }
.an-segment-card { padding:1rem 0; border-bottom:1px solid var(--cg-border); }
.an-segment-card:first-child { border-top:1px solid var(--cg-ink); }
.an-segment-card > div {
  display:flex; justify-content:space-between; gap:1rem; align-items:baseline;
}
.an-segment-card > div strong { color:var(--cg-ink); }
.an-segment-card > div span { color:var(--cg-ink-muted); font-size:.75rem; }
.an-segment-card dl { display:grid; grid-template-columns:repeat(3,1fr); gap:.8rem; margin:.8rem 0 0; }
.an-segment-card dd { margin:.22rem 0 0; color:var(--cg-ink); font-weight:800; }
.mo-status {
  --mo-status:var(--cg-accent);
  display:grid; grid-template-columns:1.25fr .9fr; gap:2rem;
  border-top:3px solid var(--mo-status); border-bottom:1px solid var(--cg-border);
  padding:1rem 0; margin-bottom:1.4rem;
}
.mo-status.unavailable { --mo-status:var(--cg-watch); }
.mo-status > div > span, .mo-threshold > div:first-child > span {
  display:block; color:var(--cg-ink-muted); font-size:.66rem; font-weight:800;
  letter-spacing:.07em; text-transform:uppercase;
}
.mo-status > div > strong {
  display:block; color:var(--cg-ink); font-size:1.1rem; margin:.3rem 0;
}
.mo-status > div > p { margin:.2rem 0; line-height:1.5; }
.mo-status dl { margin:0; border-left:1px solid var(--cg-border); }
.mo-status dl > div {
  display:flex; justify-content:space-between; gap:1rem; padding:.45rem .8rem;
  border-bottom:1px solid var(--cg-border); font-size:.76rem;
}
.mo-status dt { color:var(--cg-ink-muted); }
.mo-status dd { color:var(--cg-ink); font-weight:800; margin:0; text-align:right; }
.mo-identity {
  display:grid; grid-template-columns:repeat(5,minmax(0,1fr));
  border-top:1px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
  margin:0 0 1.4rem;
}
.mo-identity > div { padding:.8rem .75rem; border-right:1px solid var(--cg-border); }
.mo-identity > div:last-child { border-right:0; }
.mo-identity dt {
  color:var(--cg-ink-muted); font-size:.65rem; font-weight:800;
  letter-spacing:.06em; text-transform:uppercase;
}
.mo-identity dd {
  color:var(--cg-ink); font-weight:800; margin:.28rem 0 0; overflow-wrap:anywhere;
}
.mo-threshold {
  display:grid; grid-template-columns:.42fr 1.58fr; gap:1.5rem;
  border-top:1px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
  padding:1rem 0; margin-bottom:1.4rem;
}
.mo-threshold > div:first-child { border-right:1px solid var(--cg-border); }
.mo-threshold > div:first-child > strong {
  display:block; color:var(--cg-ink); font-size:2rem; margin:.3rem 0;
  font-variant-numeric:tabular-nums;
}
.mo-threshold > div:first-child > small { color:var(--cg-ink-muted); }
.mo-threshold-track { position:relative; height:8px; background:#DCE2DE; margin:.4rem 0; }
.mo-threshold-track i {
  position:absolute; top:-5px; width:2px; height:18px; background:var(--cg-accent);
}
.mo-threshold-labels {
  display:flex; justify-content:space-between; color:var(--cg-ink-muted);
  font-size:.66rem; font-weight:750;
}
.mo-threshold p { margin:.7rem 0 0; line-height:1.5; }
.mo-configuration {
  display:grid; grid-template-columns:1fr 1fr; border-top:1px solid var(--cg-ink);
}
.mo-configuration section { padding:.9rem 1rem; border-right:1px solid var(--cg-border); }
.mo-configuration section:first-child { padding-left:0; }
.mo-configuration section:last-child { padding-right:0; border-right:0; }
.mo-configuration h3, .mo-data-source h3 { margin:.05rem 0 .7rem !important; }
.mo-configuration dl { margin:0; }
.mo-configuration dl > div {
  display:flex; justify-content:space-between; gap:1rem; padding:.45rem 0;
  border-top:1px solid var(--cg-border); font-size:.75rem;
}
.mo-configuration dt { color:var(--cg-ink-muted); }
.mo-configuration dd {
  color:var(--cg-ink); font-weight:750; margin:0; text-align:right; max-width:62%;
}
.mo-data-source {
  border-top:1px solid var(--cg-border); border-bottom:1px solid var(--cg-border);
  padding:.9rem 0; margin-bottom:1.4rem;
}
.mo-data-source p { color:var(--cg-ink); line-height:1.5; margin:.2rem 0; }
.mo-data-source small { color:var(--cg-ink-muted); }
.mo-candidate-table table { width:100%; border-collapse:collapse; table-layout:fixed; }
.mo-candidate-table caption {
  position:absolute; width:1px; height:1px; padding:0; margin:-1px;
  overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
}
.mo-candidate-table th, .mo-candidate-table td {
  padding:.72rem .45rem; border-bottom:1px solid var(--cg-border);
  text-align:left; font-size:.7rem; overflow-wrap:anywhere;
}
.mo-candidate-table thead th {
  color:var(--cg-ink-muted); font-size:.59rem; font-weight:800;
  letter-spacing:.05em; text-transform:uppercase; border-bottom-color:var(--cg-ink);
}
.mo-candidate-table th:first-child { width:18%; }
.mo-candidate-table th:nth-child(2) { width:16%; }
.mo-candidate-table tbody th { color:var(--cg-ink); font-size:.73rem; }
.mo-mobile-candidates { display:none; list-style:none; padding:0; margin:0 0 1.4rem; }
.mo-candidate { padding:.9rem 0; border-bottom:1px solid var(--cg-border); }
.mo-candidate:first-child { border-top:1px solid var(--cg-ink); }
.mo-candidate strong { display:block; color:var(--cg-ink); }
.mo-candidate span {
  display:block; color:var(--cg-watch); font-size:.7rem; font-weight:800;
  letter-spacing:.05em; text-transform:uppercase; margin:.2rem 0;
}
.mo-candidate p { margin:.3rem 0 0; font-size:.76rem; }
.mo-boundary {
  border-left:3px solid var(--cg-accent); background:#FFF8EE; padding:1rem 1.15rem;
}
.mo-boundary > strong { color:#6B430E; }
.mo-boundary ul { margin:.6rem 0; padding-left:1.2rem; color:#594728; }
.mo-boundary li { margin:.3rem 0; line-height:1.45; }
.mo-boundary p { color:#6B583A; margin:.5rem 0 0; }
.mo-boundary a { display:inline-block; margin-top:.7rem; font-weight:800; color:#0F6072; }
.ex-state, .ex-idle {
  border:1px dashed #AAB7B2; padding:1.25rem; background:rgba(255,255,255,.45);
  margin:.4rem 0 1.2rem;
}
.ex-state strong, .ex-idle strong { color:var(--cg-ink); }
.ex-state p, .ex-idle p { margin:.35rem 0 0; line-height:1.5; }
.ex-honesty {
  display:grid; grid-template-columns:.35fr 1.65fr; gap:1rem;
  border-left:3px solid var(--cg-accent); background:#FFF8EE;
  padding:.75rem 1rem; margin:.45rem 0 .9rem;
}
.ex-honesty strong {
  color:#6B430E; font-size:.68rem; letter-spacing:.06em; text-transform:uppercase;
}
.ex-honesty span { color:#594728; font-size:.8rem; }
.ex-global-list { list-style:none; padding:0; margin:0 0 1rem; border-top:1px solid var(--cg-ink); }
.ex-global-driver { padding:.72rem 0; border-bottom:1px solid var(--cg-border); }
.ex-global-label {
  display:grid; grid-template-columns:34px 1fr auto; gap:.7rem; align-items:center;
  margin-bottom:.45rem;
}
.ex-global-label > b { color:var(--cg-ink-muted); font-size:.68rem; letter-spacing:.08em; }
.ex-global-label strong { display:block; color:var(--cg-ink); }
.ex-global-label span { display:block; color:var(--cg-ink-muted); font-size:.7rem; margin-top:.1rem; }
.ex-global-label em {
  color:var(--cg-ink); font-size:.68rem; font-style:normal; font-weight:800;
  letter-spacing:.05em; text-transform:uppercase;
}
.ex-global-track { height:8px; background:#DCE2DE; margin-left:34px; }
.ex-global-track > div { height:100%; min-width:2px; background:var(--cg-focus); }
.ex-global-table table { width:100%; border-collapse:collapse; table-layout:fixed; }
.ex-global-table caption {
  position:absolute; width:1px; height:1px; padding:0; margin:-1px;
  overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
}
.ex-global-table th, .ex-global-table td {
  padding:.68rem .45rem; border-bottom:1px solid var(--cg-border);
  text-align:left; font-size:.71rem; overflow-wrap:anywhere; vertical-align:top;
}
.ex-global-table thead th {
  color:var(--cg-ink-muted); font-size:.6rem; font-weight:800;
  letter-spacing:.05em; text-transform:uppercase; border-bottom-color:var(--cg-ink);
}
.ex-global-table th:nth-child(1) { width:6%; }
.ex-global-table th:nth-child(2) { width:14%; }
.ex-global-table th:nth-child(3) { width:15%; }
.ex-global-table th:nth-child(4) { width:14%; }
.ex-global-table th:nth-child(5) { width:10%; }
.ex-global-table tbody th { color:var(--cg-ink); }
.ex-method {
  border-bottom:1px solid var(--cg-border); margin:0 0 1.5rem; padding:.7rem 0;
}
.ex-method summary, .ex-local-driver summary {
  color:#0F6072; font-size:.74rem; font-weight:800; cursor:pointer;
}
.ex-method p { font-size:.76rem; line-height:1.5; max-width:900px; }
.ex-local-head {
  display:grid; grid-template-columns:repeat(4,minmax(0,1fr));
  border-top:1px solid var(--cg-ink); border-bottom:1px solid var(--cg-border);
  margin:.4rem 0 1rem;
}
.ex-local-head > div { padding:.8rem .75rem; border-right:1px solid var(--cg-border); }
.ex-local-head > div:last-child { border-right:0; }
.ex-local-head span, .ex-risk > div span {
  display:block; color:var(--cg-ink-muted); font-size:.65rem; font-weight:800;
  letter-spacing:.06em; text-transform:uppercase;
}
.ex-local-head strong { display:block; color:var(--cg-ink); margin-top:.25rem; overflow-wrap:anywhere; }
.ex-risk {
  --ex-risk:var(--cg-watch); --ex-soft:var(--cg-watch-soft);
  display:grid; grid-template-columns:.35fr .25fr 1.4fr; gap:1.2rem;
  align-items:center; border-left:4px solid var(--ex-risk);
  background:var(--ex-soft); padding:1rem 1.1rem; margin-bottom:1rem;
}
.ex-risk.low { --ex-risk:var(--cg-low); --ex-soft:var(--cg-low-soft); }
.ex-risk.high { --ex-risk:var(--cg-high); --ex-soft:var(--cg-high-soft); }
.ex-risk > div strong { display:block; color:var(--cg-ink); font-size:2rem; line-height:1; margin-top:.25rem; }
.ex-risk > b { color:var(--ex-risk); }
.ex-risk p { color:var(--cg-ink); margin:0; line-height:1.5; }
.ex-mixed {
  display:grid; grid-template-columns:.3fr 1.7fr; gap:1rem;
  border-top:1px solid var(--cg-watch); border-bottom:1px solid var(--cg-border);
  padding:.75rem 0; margin-bottom:1rem;
}
.ex-mixed strong { color:var(--cg-watch); }
.ex-mixed span { color:var(--cg-ink); line-height:1.45; }
.ex-local-drivers { list-style:none; padding:0; margin:0 0 1.2rem; border-top:1px solid var(--cg-ink); }
.ex-local-driver {
  display:grid; grid-template-columns:42px 1fr; gap:.8rem;
  padding:1rem .2rem; border-bottom:1px solid var(--cg-border);
}
.ex-local-driver > b { color:var(--cg-ink-muted); font-size:.7rem; letter-spacing:.08em; }
.ex-driver-copy > strong { color:var(--cg-ink); font-size:.92rem; }
.ex-driver-copy > span {
  display:block; font-size:.72rem; font-weight:850; margin:.18rem 0;
}
.ex-local-driver.raises .ex-driver-copy > span { color:var(--cg-high); }
.ex-local-driver.lowers .ex-driver-copy > span { color:var(--cg-low); }
.ex-driver-copy > p { margin:.3rem 0 .55rem; line-height:1.5; }
.ex-local-driver details { border-top:1px solid var(--cg-border); padding-top:.45rem; }
.ex-local-driver dl { display:grid; grid-template-columns:repeat(2,1fr); gap:.35rem 1rem; margin:.55rem 0; }
.ex-local-driver dl > div { display:flex; justify-content:space-between; gap:.5rem; font-size:.7rem; }
.ex-local-driver dt { color:var(--cg-ink-muted); }
.ex-local-driver dd { color:var(--cg-ink); font-weight:800; margin:0; text-align:right; }
.ex-local-driver small { color:var(--cg-ink-muted); }
.ex-balancing { list-style:none; padding:0; margin:0 0 1.2rem; border-top:1px solid var(--cg-ink); }
.ex-balancing li {
  display:grid; grid-template-columns:.45fr 1.55fr; gap:1rem;
  padding:.72rem 0; border-bottom:1px solid var(--cg-border);
}
.ex-balancing strong { color:var(--cg-low); }
.ex-balancing span { color:var(--cg-ink); line-height:1.45; }
.ex-no-balance {
  border-top:1px solid var(--cg-border); border-bottom:1px solid var(--cg-border);
  padding:.8rem 0; margin-bottom:1.2rem;
}
.ex-no-balance strong { color:var(--cg-ink); }
.ex-no-balance p { margin:.3rem 0 0; font-size:.76rem; }
.ex-operator {
  border-left:4px solid var(--cg-accent); background:#FFF8EE; padding:1rem 1.15rem;
}
.ex-operator > strong { color:var(--cg-ink); }
.ex-operator ul { margin:.55rem 0; padding-left:1.2rem; color:#594728; }
.ex-operator small { color:#6B583A; }
.ex-actions {
  display:flex; flex-wrap:wrap; gap:.5rem 1.2rem; padding:.8rem 0 1.5rem;
  border-bottom:1px solid var(--cg-border);
}
.ex-actions a { color:#0F6072; font-weight:800; }
@keyframes cgReveal { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
.cg-result { animation:cgReveal 220ms cubic-bezier(.2,.8,.2,1); }
@media (max-width:1100px) {
  [data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
  [data-testid="stMainBlockContainer"] { padding-left:1.5rem; padding-right:1.5rem; }
  .cg-mobile-brand { display:block; }
  .ch-table-wrap { display:none; }
  .ch-mobile-list { display:block; }
  .bp-results-table { display:none; }
  .bp-mobile-results { display:block; }
  .an-segment-table { display:none; }
  .an-mobile-segments { display:block; }
  .mo-candidate-table { display:none; }
  .mo-mobile-candidates { display:block; }
  .ex-global-table { display:none; }
}
@media (max-width:900px) {
  [data-testid="stHorizontalBlock"] { flex-direction:column !important; gap:1rem !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width:100% !important; flex:1 1 auto !important;
  }
  .cc-kpis { grid-template-columns:1fr 1fr; }
  .cc-kpis > div:nth-child(2) { border-right:0; }
  .cc-kpis > div:nth-child(-n+2) { border-bottom:1px solid var(--cg-border); }
  .cc-queue-head { display:none; }
  .cc-queue { border-top:0; }
  .cc-queue-row {
    grid-template-columns:1.2fr .7fr .8fr; align-items:start; padding:1rem 0; gap:.8rem 1rem;
  }
  .cc-queue-row > div > span { display:block; margin-bottom:.18rem; }
  .cc-driver-cell { grid-column:1 / span 2; }
  .cc-queue-row > div:last-child { grid-column:3; grid-row:2; align-self:end; }
}
@media (max-width:767px) {
  [data-testid="stMainBlockContainer"] { padding:1.25rem 1rem 3rem; }
  h1 { font-size:1.65rem !important; }
  .cg-score { font-size:2.7rem; }
  .cg-risk-head { align-items:center; }
  .cg-meta { grid-template-columns:1fr 1fr; }
  .cg-driver { grid-template-columns:30px 1fr; }
  .cg-impact { grid-column:2; }
  .cc-statusline { grid-template-columns:1fr; gap:.7rem; }
  .cc-kpis { grid-template-columns:1fr 1fr; }
  .cc-kpis > div { padding:.8rem; }
  .cc-kpis span { min-height:3.2em; }
  .cc-kpis strong { font-size:1.4rem; }
  .cc-queue-row { grid-template-columns:1fr 1fr; }
  .cc-driver-cell { grid-column:1 / -1; }
  .cc-queue-row > div:last-child { grid-column:2; grid-row:auto; }
  .cc-review-item { grid-template-columns:1fr; }
  .cc-review-item p, .cc-review-item a, .cc-review-item em { grid-column:1; }
  .cc-activity-row { grid-template-columns:1.5fr .8fr .45fr; }
  .cc-activity-row time { grid-column:1 / -1; }
  .ch-card-signal { grid-template-columns:1fr 1.35fr; }
  .cd-identity { grid-template-columns:1fr 1fr; }
  .cd-identity > div:nth-child(2) { border-right:0; }
  .cd-identity > div:nth-child(-n+2) { border-bottom:1px solid var(--cg-border); }
  .cd-driver { grid-template-columns:32px 1fr; gap:.45rem .75rem; align-items:start; }
  .cd-driver-signal, .cd-driver-value { grid-column:2; }
  .cd-context { grid-template-columns:1fr; }
  .cd-context section, .cd-context section:first-child, .cd-context section:last-child {
    padding:.9rem 0; border-right:0; border-bottom:1px solid var(--cg-border);
  }
  .cd-prediction-context { grid-template-columns:1fr; }
  .cd-actions { gap:.25rem .9rem; }
  .cd-risk-top > div > strong { font-size:2.8rem; }
  .bp-validation { grid-template-columns:1fr; gap:.5rem; }
  .bp-validation dl { border-left:0; border-top:1px solid var(--cg-border); }
  .bp-summary { grid-template-columns:1fr 1fr; }
  .bp-summary > div { border-bottom:1px solid var(--cg-border); }
  .bp-summary > div:nth-child(2), .bp-summary > div:nth-child(4) { border-right:0; }
  .bp-summary > div:last-child { grid-column:1 / -1; border-bottom:0; }
  .bp-distribution { grid-template-columns:1fr; gap:0; }
  .bp-preview th:nth-child(n+3), .bp-preview td:nth-child(n+3) { display:none; }
  .bp-issues li { grid-template-columns:1fr; }
  .an-summary { grid-template-columns:1fr; }
  .an-summary > div { border-right:0; border-bottom:1px solid var(--cg-border); }
  .an-summary > div:last-child { border-bottom:0; }
  .an-unavailable, .an-insight { grid-template-columns:1fr; gap:.35rem; }
  .an-segment-card dl { grid-template-columns:1fr 1fr; }
  .an-segment-card dl > div:first-child { grid-column:1 / -1; }
  .mo-status, .mo-threshold { grid-template-columns:1fr; gap:.7rem; }
  .mo-status dl, .mo-threshold > div:first-child {
    border-left:0; border-right:0; border-top:1px solid var(--cg-border);
    padding-top:.7rem;
  }
  .mo-identity { grid-template-columns:1fr 1fr; }
  .mo-identity > div { border-bottom:1px solid var(--cg-border); }
  .mo-identity > div:nth-child(2), .mo-identity > div:nth-child(4) { border-right:0; }
  .mo-identity > div:last-child { grid-column:1 / -1; border-bottom:0; }
  .mo-configuration { grid-template-columns:1fr; }
  .mo-configuration section, .mo-configuration section:first-child, .mo-configuration section:last-child {
    padding:.9rem 0; border-right:0; border-bottom:1px solid var(--cg-border);
  }
  .ex-honesty, .ex-mixed { grid-template-columns:1fr; gap:.3rem; }
  .ex-local-head { grid-template-columns:1fr 1fr; }
  .ex-local-head > div:nth-child(2) { border-right:0; }
  .ex-local-head > div:nth-child(-n+2) { border-bottom:1px solid var(--cg-border); }
  .ex-risk { grid-template-columns:1fr 1fr; gap:.7rem; }
  .ex-risk p { grid-column:1 / -1; }
  .ex-local-driver { grid-template-columns:32px 1fr; }
  .ex-local-driver dl { grid-template-columns:1fr; }
  .ex-balancing li { grid-template-columns:1fr; gap:.25rem; }
  .ex-global-label { grid-template-columns:28px 1fr; }
  .ex-global-label em { grid-column:2; }
  .ex-global-track { margin-left:28px; }
}
@media (prefers-reduced-motion:reduce) {
  *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; scroll-behavior:auto !important; }
}
</style>
"""
