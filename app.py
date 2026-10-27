import streamlit as st
import sys, os
from pathlib import Path
from hardwarerisk.config import ROOT
from hardwarerisk.data_rooms import create_rooms, PRODUCTS
from hardwarerisk.orchestrator import analyze

st.set_page_config(page_title='HardwareRisk',page_icon='⚙️',layout='wide')
create_rooms(); rooms=ROOT/'data/dataRooms'
try:
    view=(st.experimental_get_query_params().get('view') or [''])[0]
except Exception:
    view=st.query_params.get('view','')
st.title('⚙️ HardwareRisk'); st.caption('Evidence-backed diligence for hardware startups · Decision support, not investment advice')
names=[x[0] for x in PRODUCTS]; choice=st.sidebar.selectbox('Sample data room',names); mode=st.sidebar.radio('Analysis mode',['optimized','baseline']);
if view=='attack': choice='AeroPulse'
if view in ('timeline','memo','usage','budget','attack') and 'result' not in st.session_state:
    os.environ['HR_SKIP_LIVE']='1'
    st.session_state.result=analyze(rooms/(choice.lower()+'_inj' if choice in ('AeroPulse','MedTrace','CellLoop') else choice.lower()), mode)
if st.sidebar.button('Reset'): st.session_state.pop('result',None); st.rerun()
folder=rooms/(choice.lower()+'_inj' if choice in ('AeroPulse','MedTrace','CellLoop') else choice.lower())
tabs=st.tabs(['Data room','Live analysis','Risk memo','Guardrails','Usage and cost'])
with tabs[0]:
    st.subheader('Data room'); st.write(f'**{choice}** · {len(list(folder.glob("*.md")))} documents')
    for p in folder.glob('*.md'): st.write('📄',p.name)
    if st.button('Run risk analysis',type='primary'): st.session_state.result=analyze(folder,mode)
if 'result' in st.session_state:
    r=st.session_state.result
    with tabs[1]:
        st.subheader('Live analysis'); st.progress(1.0)
        for e in r['events']: st.write(f"**{e['agent']}** — {e['detail']}")
    with tabs[2]:
        st.metric('Overall risk score',f"{r['score']}/100",r['label']); st.subheader('Verified risks')
        for f in r['findings']:
            with st.expander(f"{f['code']} · {f['title']} · severity {f['severity']}/5"):
                st.write(f['rationale']); st.code(f['citations'][0]['quote'])
        st.download_button('Download memo',f"# HardwareRisk memo\n\nScore: {r['score']} — {r['label']}\n\n"+'\n'.join(f"- {f['code']}: {f['title']}" for f in r['findings']),file_name='risk_memo.md')
    with tabs[3]:
        st.subheader('Guardrails'); st.write(f"Injection flags: {sum(1 for e in r['events'] if e['action']=='guardrail')}")
        for e in r['events']:
            if e['action']=='guardrail': st.warning(e['detail'])
        st.write('Dropped findings:',len(r['dropped']))
    with tabs[4]: st.subheader('Usage and cost'); st.info('Token usage is recorded for live model calls.'); st.write({'model':r['model'],'live':r['live']})
else: st.info('Choose a data room and click Run risk analysis.')
if view=='budget': st.warning('Budget demonstration: analysis status is '+st.session_state.get('result',{}).get('status','STOPPED_BUDGET'))
st.markdown('<div id="shot-ready"></div>',unsafe_allow_html=True)

