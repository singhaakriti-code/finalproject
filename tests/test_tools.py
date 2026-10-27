from hardwarerisk.tools import calc_unit_economics,calc_runway,lookup_regulatory
def test_calculators():
    assert calc_unit_economics(100,60)['gross_margin_pct']==40
    assert calc_runway(1000,200)['runway_months']==5
def test_lookup(): assert 'certifications' in lookup_regulatory('drone')

