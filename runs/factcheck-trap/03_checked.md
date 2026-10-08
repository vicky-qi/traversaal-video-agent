# Checked facts: Fact-checker trap test

Research: `runs/factcheck-trap/02_research.md` · Checked: 2026-10-07
Verified: 6 · Overstated: 0 · Unsupported: 2 · Unreachable: 0

Only the facts below may be used in the script.

## Q1. What moves inside a cell?

- **Q1-F1** A lithium-ion cell has a negative electrode (anode), a positive electrode (cathode), an electrolyte, and a thin porous separator between the two electrodes that lithium ions can pass through.
  - Source: [Clean Energy Institute, University of Washington – Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/) · academic · published undated · scope: global (general science)
  - Quote: "The lithium ions are small enough to be able to move through a micro-permeable separator between the anode and cathode."
  - Flags: none
  - Check: VERIFIED (CEI: names the anode, cathode, electrolyte and a "micro-permeable separator between the anode and cathode" that lithium ions move through. The page does not use the word "thin" or the labels "negative/positive electrode"; these are descriptors, not figures.)
- **Q1-F2** When the battery powers the car (discharge), lithium atoms in the negative electrode give up an electron, and the lithium ions travel through the electrolyte and separator to the positive electrode.
  - Source: [Clean Energy Institute, University of Washington – Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/) · academic · published undated · scope: global
  - Quote: "During a discharge cycle, lithium atoms in the anode are ionized and separated from their electrons."
  - Source 2: [Technical University of Munich, Chair of Electrical Energy Storage Technology – Discharge and charge process of a conventional lithium-ion battery cell](https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell) · academic · published undated · scope: global
  - Quote 2: "Li+ ions move to the positive electrode diffusing through the electrolyte and the separator."
  - Flags: none
  - Check: VERIFIED (TUM verifies it fully: during discharge lithium atoms "oxidize by forming Li+ ions and electrons" and the ions move to the positive electrode through the electrolyte and the separator. CEI supports the same in anode/cathode terms.)
- **Q1-F3** While the ions move inside the cell, the electrons travel the other way round, through the outside circuit from the negative to the positive side; that flow of electrons is the electric current the car uses.
  - Source: [Technical University of Munich – Discharge and charge process of a conventional lithium-ion battery cell](https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell) · academic · published undated · scope: global
  - Quote: "The electrons flow from the negative electrode to the positive on the external circuitry."
  - Flags: none
  - Check: VERIFIED (TUM: electrons flow negative to positive on the external circuit, "where the resulting current flow can be used for an application". Ions and electrons both go negative to positive, by different routes, so "the other way round" can only mean "by the other route", not "in the opposite direction".)

## Q6. Battery pack cost

- **Q6-F1** The average lithium-ion battery pack (all uses) cost $108 per kWh in 2025, a record low and 8% less than in 2024.
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour despite rising metal prices](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: global
  - Quote: "lithium-ion battery pack prices have dropped 8% since 2024 to a record low of $108 per kilowatt-hour"
  - Source 2: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote 2: "Average battery prices declined by 8% in 2025"
  - Flags: none for the 8% fall (two sources); SINGLE SOURCE for $108/kWh
  - Check: VERIFIED (BNEF verifies it fully: $108/kWh, record low, down 8% since 2024. It is the overall pack price, given next to the segment prices (BEV $99, stationary storage $70). IEA confirms the 8% fall.)
- **Q6-F2** Battery packs for battery-electric cars were the cheapest in transport, at an average of $99 per kWh in 2025.
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: global
  - Quote: "Battery electric vehicles (BEVs) packs were the cheapest in the transport segment at $99/kWh"
  - Flags: SINGLE SOURCE
  - Check: VERIFIED (BNEF: $99/kWh for BEV packs in 2025, cheapest in the transport segment. The page's term is "battery electric vehicles (BEVs)".)
- **Q6-F3** In 2015, the US Department of Energy estimated the cost of an electric car battery at about $268 per kWh (in 2014 dollars, modelled cost at 100,000 packs a year).
  - Source: [U.S. DOE Vehicle Technologies Office – Overview of the DOE VTO Advanced Battery R&D Program (Howell et al.)](https://www.energy.gov/sites/prod/files/2016/06/f32/es000_howell_2016_o_web.pdf) · official · published 2016-06 · scope: US
  - Quote: "2015 DOE cost $268/kWh"
  - Flags: SINGLE SOURCE (modelled production cost in 2014 dollars; not the same method as BNEF's 2025 market survey)
  - Check: VERIFIED (DOE PDF slide 3: chart label "2015 DOE cost $268/kWh" on a "2014 US$/kWh" axis. Slide 9, "EV Battery Performance Status": "Production Cost at 100,000 units/year", current "< $268", and "Cost projection by using the BatPaC model".)

## Q3. Battery chemistries

No verified facts for this question. Q3-F9 was rejected (see below).

## Rejected facts (do not use)

| ID | Verdict | Reason | Narrower wording the source does support |
|---|---|---|---|
| Q6-F9 | UNSUPPORTED | BNEF gives $99/kWh for BEV packs in 2025. $85/kWh appears nowhere on the page. The research quote stops just before "at $99/kWh". | "Battery packs for battery-electric vehicles were the cheapest in transport, at $99 per kWh in 2025." (already Q6-F2) |
| Q3-F9 | UNSUPPORTED | The page's "over 55%" is the global LFP share of EV batteries deployed in 2025 (by battery capacity of new EVs registered), not a share of US car sales. For the US the page says something different: the LFP share of EV batteries "almost halved in 2025 from an already low base in 2024". The IEA page is global, not "scope: US", and the one-word quote "LFP" does not point to any claim. | "In 2025, LFP batteries made up over 55% of EV batteries deployed worldwide, up from nearly 50% in 2024." Or, for the US: "In the US, the LFP share of EV batteries almost halved in 2025, from an already low base." |

## Sources

| URL | Status |
|---|---|
| https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/ | loaded (University of Washington Clean Energy Institute; no publication date on the page, which matches "undated") |
| https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell | loaded (TUM Chair of Electrical Energy Storage Technology; undated, which matches) |
| https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/ | loaded (BloombergNEF press release dated 9 December 2025, which matches 2025-12) |
| https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries | loaded (IEA, Global EV Outlook 2026. The page shows the year 2026 but no month, so "2026-05" is not confirmed. The page is global, not US as Q3-F9 says.) |
| https://www.energy.gov/sites/prod/files/2016/06/f32/es000_howell_2016_o_web.pdf | loaded (DOE VTO slide deck by Howell, Cunningham, Duong and Faguy, dated June 6, 2016, which matches. WebFetch returned no readable text from the PDF on two tries, so the copy that WebFetch saved was read with Read.) |
