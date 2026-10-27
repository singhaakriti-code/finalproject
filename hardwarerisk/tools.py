import json
from pathlib import Path
from pydantic import BaseModel, Field
from .config import ROOT

class SearchArgs(BaseModel): query:str; k:int=Field(8, ge=1, le=20)
class EconArgs(BaseModel): price:float; bom_at_scale:float; units:int=1; tooling_cost:float=0; other_cogs:float=0
class RunwayArgs(BaseModel): cash:float; monthly_burn:float; raise_amount:float=0

def search_dataroom(chunks, query, k=8):
    terms=set(query.lower().split()); ranked=sorted(chunks, key=lambda c:sum(t in c.text.lower() for t in terms), reverse=True)
    return [{'chunk_id':c.id,'doc':c.doc,'text':c.text,'flagged':c.flagged} for c in ranked[:k]]
def calc_unit_economics(price,bom_at_scale,units=1,tooling_cost=0,other_cogs=0):
    per=bom_at_scale+other_cogs+(tooling_cost/units if units else tooling_cost); return {'gross_margin_pct':round((price-per)/price*100,2) if price else 0,'gross_profit_per_unit':round(price-per,2),'cogs_per_unit':round(per,2)}
def calc_runway(cash,monthly_burn,raise_amount=0): return {'runway_months':round((cash+raise_amount)/monthly_burn,2) if monthly_burn else 999}
def lookup_regulatory(category): return json.loads((ROOT/'data/regulatory_requirements.json').read_text()).get(category, {'certifications':[],'notes':'No lookup entry.'})
def lookup_supply_risk(component):
    data=json.loads((ROOT/'data/component_risk.json').read_text()); key=next((k for k in data if k in component.lower()), None)
    return data.get(key, {'lead_time_weeks':None,'single_source_risk':None,'notes':'No lookup entry.'})

