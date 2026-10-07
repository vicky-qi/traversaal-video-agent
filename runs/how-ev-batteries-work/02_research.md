# Research: How Electric Car Batteries Work

Brief: `runs/how-ev-batteries-work/01_brief.md` · Researched: 2026-10-07 · Facts: 54

Note for the fact-checker: pages were read through a fetch tool that returns processed text. Quotes are copied from that output; please re-check exact wording on the live page. Where a fact has two sources, both are listed.

## Q1. Inside a single electric car battery cell, what are the main parts, and what physically moves between them when the battery charges and when it powers the car?

**Short answer:** A cell has two electrodes (a negative one, usually graphite, and a positive one made of a lithium metal oxide), a liquid electrolyte between them, and a thin porous separator. When the car drives, lithium ions travel inside the cell from the negative side to the positive side while electrons go the long way round through the outside circuit; charging pushes both back. Which way the ions move decides whether the cell is storing or releasing energy.

- **Q1-F1** A lithium-ion cell has a negative electrode (anode), a positive electrode (cathode), an electrolyte, and a thin porous separator between the two electrodes that lithium ions can pass through.
  - Source: [Clean Energy Institute, University of Washington – Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/) · academic · published undated · scope: global (general science)
  - Quote: "The lithium ions are small enough to be able to move through a micro-permeable separator between the anode and cathode."
  - Flags: none
- **Q1-F2** When the battery powers the car (discharge), lithium atoms in the negative electrode give up an electron, and the lithium ions travel through the electrolyte and separator to the positive electrode.
  - Source: [Clean Energy Institute, University of Washington – Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/) · academic · published undated · scope: global
  - Quote: "During a discharge cycle, lithium atoms in the anode are ionized and separated from their electrons."
  - Source 2: [Technical University of Munich, Chair of Electrical Energy Storage Technology – Discharge and charge process of a conventional lithium-ion battery cell](https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell) · academic · published undated · scope: global
  - Quote 2: "Li+ ions move to the positive electrode diffusing through the electrolyte and the separator."
  - Flags: none
- **Q1-F3** While the ions move inside the cell, the electrons travel the other way round, through the outside circuit from the negative to the positive side; that flow of electrons is the electric current the car uses.
  - Source: [Technical University of Munich – Discharge and charge process of a conventional lithium-ion battery cell](https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell) · academic · published undated · scope: global
  - Quote: "The electrons flow from the negative electrode to the positive on the external circuitry."
  - Flags: none
- **Q1-F4** Charging reverses the trip: lithium leaves the positive electrode's metal-oxide structure, the ions travel back to the negative (graphite) electrode, and there they rejoin electrons and are stored again.
  - Source: [Technical University of Munich – Discharge and charge process of a conventional lithium-ion battery cell](https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell) · academic · published undated · scope: global
  - Quote: "the Li+ ions and electrons recombine with each other forming neutral lithium atoms."
  - Flags: none
- **Q1-F5** In the graphite electrode, lithium is stored by slipping in between the stacked carbon layers, a process called intercalation.
  - Source: [Clean Energy Institute, University of Washington – Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/) · academic · published undated · scope: global
  - Quote: "Lithium ions are stored within graphite anodes through a mechanism known as" (page continues "intercalation", ions inserted between graphene layers)
  - Flags: none
- **Q1-F6** Whether the battery is storing energy or releasing it depends only on which direction the lithium ions are moving through the electrolyte.
  - Source: [U.S. DOE Office of Electricity / Pacific Northwest National Laboratory – Lithium-Ion Batteries for Stationary Energy Storage (fact sheet)](https://www.energy.gov/sites/default/files/Li-ion.pdf) · official · published 2012-10 · scope: global (general science)
  - Quote: "which either stores or discharges energy, depending on the direction of the flow."
  - Flags: none
- **Q1-F7** The liquid electrolyte in today's lithium-ion cells is made with flammable organic solvents, which is one reason cells need protection from overheating.
  - Source: [U.S. DOE Office of Electricity / PNNL – Lithium-Ion Batteries for Stationary Energy Storage](https://www.energy.gov/sites/default/files/Li-ion.pdf) · official · published 2012-10 · scope: global
  - Quote: "Current electrolytes are unstable and potentially flammable at high voltages"
  - Source 2: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote 2: "(flammable) organic solvents"
  - Flags: none
- **Q1-F8** The classic lithium-ion pairing is a lithium cobalt oxide positive electrode with a graphite negative electrode; other common positive-electrode materials include lithium manganese oxide and lithium iron phosphate. (In cars today, nickel-based NMC and lithium iron phosphate dominate; see Q3.)
  - Source: [Clean Energy Institute, University of Washington – Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/) · academic · published undated · scope: global
  - Quote: "The most common combination is that of lithium cobalt oxide (cathode) and graphite (anode)."
  - Flags: none

## Q2. How are individual cells grouped and wired into modules and a full pack in a typical passenger electric car, and what do the battery management system and the cooling system monitor and control?

**Short answer:** Cells are joined into modules and modules into a pack; wiring cells end-to-end (series) raises the voltage, wiring them side-by-side (parallel) adds capacity. Newer "cell-to-pack" designs skip the module step. The battery management system (BMS) watches each cell's voltage, temperature and the pack current, protects against over- and under-charging and keeps cells balanced; the cooling system keeps the pack in a narrow temperature band, roughly 15–35 °C.

- **Q2-F1** A conventional car battery pack is built in three levels: cells are connected together, placed in a module case, and the modules are connected to form the pack.
  - Source: [LG Energy Solution – Battery Glossary: Cell to Pack](https://inside.lgensol.com/en/2025/12/battery-glossary-cell-to-pack/) · company · published 2025-12 · scope: global
  - Quote: "Conventional battery packs are assembled in the order of cell–module–pack."
  - Flags: none
- **Q2-F2** Wiring cells end-to-end (series) adds up their voltages while capacity stays the same; wiring them side-by-side (parallel) adds up capacity while voltage stays the same.
  - Source: [Ionworks – Batteries 101: Battery packs](https://docs.ionworks.com/guide/batteries-101/battery-packs) · company · published undated · scope: global
  - Quote: "Cells connected positive-to-negative. Voltages add, capacity stays the same."
  - Flags: none
- **Q2-F3** Besides the cells and modules, a full pack includes the battery management system, a cooling system, contactors (heavy-duty on/off switches) and a protective enclosure.
  - Source: [Ionworks – Batteries 101: Battery packs](https://docs.ionworks.com/guide/batteries-101/battery-packs) · company · published undated · scope: global
  - Quote: "The complete battery system including modules, the BMS, cooling system, contactors, and enclosure."
  - Flags: none
- **Q2-F4** Newer "cell-to-pack" designs skip the module step and mount cells directly in the pack.
  - Source: [LG Energy Solution – Battery Glossary: Cell to Pack](https://inside.lgensol.com/en/2025/12/battery-glossary-cell-to-pack/) · company · published 2025-12 · scope: global
  - Quote: "CTP eliminates the modularization step and mounts individual battery cells directly into the pack."
  - Flags: none
- **Q2-F5** The battery management system (BMS) keeps the pack safe and healthy by measuring temperature, each cell's voltage and the pack current, and it controls cell balancing and charging and discharging.
  - Source: [Itagi et al., "Cell Balancing Paradigms" (arXiv:2411.05478)](https://arxiv.org/abs/2411.05478) · academic · published 2024-11 · scope: global
  - Quote: "This is ensured by measuring parameters like temperature, cell voltage, and pack current."
  - Flags: none (preprint, not peer-reviewed)
- **Q2-F6** No two cells are identical (cells from the same production batch can differ in internal resistance by around 15%), so the BMS must protect each cell against over- and under-voltage and keep their charge balanced.
  - Source: [Itagi et al., "Cell Balancing Paradigms" – full text (arXiv HTML)](https://arxiv.org/html/2411.05478) · academic · published 2024-11 · scope: global
  - Quote: "There can be variations in internal resistance of around 15% amongst cells produced in the same batch."
  - Flags: SINGLE SOURCE (for 15%)
- **Q2-F7** The car's thermal (cooling) system keeps the motor, power electronics and other parts, including the battery, within their proper operating temperature range.
  - Source: [U.S. DOE Alternative Fuels Data Center – How Do All-Electric Cars Work?](https://afdc.energy.gov/vehicles/how-do-all-electric-cars-work) · official · published undated · scope: US
  - Quote: "This system maintains a proper operating temperature range of the engine, electric motor, power electronics, and other components."
  - Flags: none
- **Q2-F8** Lithium-ion batteries work properly only in a narrow band of about 15–35 °C (59–95 °F); cars keep them there with air cooling, liquid cooling or phase-change materials.
  - Source: [Nasiri & Hadim, "Advances in battery thermal management", Renewable and Sustainable Energy Reviews (Stevens Institute of Technology)](https://researchwith.stevens.edu/en/publications/advances-in-battery-thermal-management-current-landscape-and-futu/) · academic · published 2024-08 · scope: global
  - Quote: "its operating temperature range which is limited within 15°C–35°C"
  - Flags: SINGLE SOURCE

## Q3. Which battery chemistries are used in passenger electric cars sold in the latest full year, what share of new cars uses each, and how do they compare on energy stored per kilogram, cost and fire safety?

**Short answer:** Two "recipes" dominate: lithium iron phosphate (LFP) and nickel-based NMC. In 2025, LFP passed half of all EV battery capacity deployed worldwide (over 55%), driven by China, while outside China nearly 80% was still nickel-based. NMC stores more energy per kilogram (up to about 265 vs 205 Wh/kg), but LFP packs are much cheaper and the LFP cathode is far more heat-stable. Shares are measured by battery capacity, not by number of cars.

- **Q3-F1** In 2025, LFP batteries made up over 55% of all EV battery capacity deployed worldwide, up from nearly 50% in 2024.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote: "In 2025, LFP batteries accounted for over 55% of EV batteries deployed globally, up from nearly 50% in 2024."
  - Flags: SINGLE SOURCE (share of battery capacity across all EVs, not share of passenger cars)
- **Q3-F2** Outside China, almost 80% of EV batteries deployed in 2025 used nickel-based chemistries such as NMC.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: outside China
  - Quote: "almost 80% of batteries used nickel‑containing chemistries, such as NMC"
  - Flags: SINGLE SOURCE
- **Q3-F3** In the European Union, LFP was just over 10% of EV battery demand in 2025 (similar to 2024); in the United States, LFP's share almost halved in 2025 from an already low level.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: Europe (EU), US
  - Quote: "In the European Union, LFP batteries accounted for more than 10% of EV battery demand in 2025, a similar level to 2024."
  - Flags: SINGLE SOURCE
- **Q3-F4** NMC stores more energy per kilogram than LFP: up to about 265 Wh/kg for NMC cells versus up to about 205 Wh/kg for the latest LFP cells (as of 2026).
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote: "up to 205 Wh/kg for the latest generation of LFP batteries … 265 Wh/kg for lithium nickel cobalt manganese oxide (NMC) batteries"
  - Flags: SINGLE SOURCE
- **Q3-F5** In 2025, LFP battery packs averaged about $81 per kWh and NMC packs about $128 per kWh, across all uses (cars and storage).
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour despite rising metal prices](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: global
  - Quote: "Average LFP battery pack prices across all segments came in at $81/kWh"
  - Flags: SINGLE SOURCE; CONFLICT with Q3-F6 (these prices imply LFP about 37% cheaper, IEA says more than 40%)
- **Q3-F6** On average, LFP packs were more than 40% cheaper per kWh than NMC packs in 2025, partly because stationary storage (which uses cheaper, less energy-dense LFP) is included.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote: "LFP battery packs were more than 40% cheaper on average than"
  - Flags: CONFLICT with Q3-F5
- **Q3-F7** On fire safety, Sandia National Laboratories found the LFP cathode stays stable above 500 °C even when charged, while nickel-based NCA and cobalt-based LCO cathodes are less stable and NCA cells showed the fastest thermal runaway.
  - Source: [Sandia National Laboratories – Multi-scale thermal stability study of commercial lithium-ion batteries (Journal of Power Sources)](https://www.sandia.gov/research/publications/details/multi-scale-thermal-stability-study-of-commercial-lithium-ion-batteries-as-2019-09-30/) · official · published 2019-09 · scope: lab tests of commercial cells
  - Quote: "By contrast, the LFP cathode is stable to >500 °C, even when charged."
  - Flags: SINGLE SOURCE (study compared LFP with LCO and NCA, not NMC)
- **Q3-F8** LFP was the fastest-growing battery chemistry in 2025, with demand up 48% from 2024 (all lithium-ion uses; EVs were 75% of battery demand), while nickel-based chemistries lost share.
  - Source: [Benchmark Mineral Intelligence – Global lithium ion battery demand rose 29% in 2025](https://source.benchmarkminerals.com/article/global-lithium-ion-battery-demand-rose-29-in-2025) · industry · published 2026-01 · scope: global
  - Quote: "LFP remained the fastest-growing battery chemistry in 2025, with demand increasing by 48% year-on-year."
  - Flags: SINGLE SOURCE

## Q4. For the best-selling electric cars of the latest model year, what are the battery size (kWh), rated range and fastest charging time (for example, 10–80%), and how do cold and hot weather affect range and charging speed?

**Short answer:** In the US in 2025, the Tesla Model Y and Model 3 sold far more than any other EV, followed by the Chevrolet Equinox EV, Ford Mustang Mach-E and Hyundai Ioniq 5. Popular models carry roughly 80–85 kWh batteries and are rated at about 320–360 miles (2026 EPA figures). Official 10–80% charging times could not be confirmed (see Gaps). Weather matters: in AAA's 2026 lab test, 20 °F cold cut range by 39% on average and 95 °F heat by 8.5%; real-world data shows EVs keep about 78% of range at freezing, and cold batteries charge more slowly.

- **Q4-F1** The five best-selling electric cars in the US in 2025 were the Tesla Model Y (357,528 sold), Tesla Model 3 (192,440), Chevrolet Equinox EV (57,945), Ford Mustang Mach-E (51,620) and Hyundai Ioniq 5 (47,039).
  - Source: [Cox Automotive / Kelley Blue Book – Electric Vehicle Sales Report Q4 2025](https://www.coxautoinc.com/wp-content/uploads/2026/01/Q4-2025-Kelley-Blue-Book-EV-Sales-Report.pdf) · industry · published 2026-01 · scope: US
  - Quote: "Tesla Model Y 92,460 85,506 8.1% 357,528 372,613 -4.0% 39.5% 28.0%"
  - Flags: SINGLE SOURCE (Cox estimates)
- **Q4-F2** The 2026 Tesla Model Y Long Range rear-wheel drive has an EPA-rated range of 357 miles; Kelley Blue Book lists the Model Y Long Range battery at 81 kWh (Tesla does not publish battery size).
  - Source: [U.S. EPA/DOE fueleconomy.gov – vehicle record 49743 (2026 Tesla Model Y Long Range RWD)](https://www.fueleconomy.gov/ws/rest/vehicle/49743) · official · published 2026-02 (last modified) · scope: US
  - Quote: "Model Y Long Range RWD" … range "357"
  - Source 2: [Kelley Blue Book – 2026 Tesla Model Y specs](https://www.kbb.com/tesla/model-y/2026/specs/) · industry · published undated · scope: US
  - Quote 2: "81.00 kWh"
  - Flags: SINGLE SOURCE for each number; CONFLICT with Q4-F5 (KBB lists 327 miles for "Long Range")
- **Q4-F3** The 2026 Chevrolet Equinox EV (front-wheel drive) has an EPA-rated range of 319 miles; Kelley Blue Book lists its battery at 85 kWh.
  - Source: [U.S. EPA/DOE fueleconomy.gov – vehicle record 49953 (2026 Chevrolet Equinox EV FWD)](https://www.fueleconomy.gov/ws/rest/vehicle/49953) · official · published 2025-10 · scope: US
  - Quote: "Equinox EV FWD" … range "319"
  - Source 2: [Kelley Blue Book – 2026 Chevrolet Equinox EV specs](https://www.kbb.com/chevrolet/equinox-ev/2026/specs/) · industry · published undated · scope: US
  - Quote 2: "85.00 kWh"
  - Flags: SINGLE SOURCE for each number; CONFLICT with Q4-F5 (KBB lists 307 miles)
- **Q4-F4** The Hyundai Ioniq 5 comes with an 84 kWh battery (a 63 kWh version is the entry model); the 2026 rear-wheel-drive Ioniq 5 has an EPA-rated range of 318 miles.
  - Source: [Kelley Blue Book – 2026 Hyundai Ioniq 5 specs](https://www.kbb.com/hyundai/ioniq-5/2026/specs/) · industry · published undated · scope: US
  - Quote: "84.00 kWh"
  - Source 2: [Hyundai Italia – IONIQ 5 Model Year 27 press release](https://www.hyundai.news/it/articles/press-releases/hyundai-ioniq-5-con-il-model-year-27-la-gamma-si-rinnova.html) · company · published 2026-07 · scope: Europe (Italy)
  - Quote 2: "La batteria da 84 kWh amplia ulteriormente le possibilità di scelta"
  - Source 3: [U.S. EPA/DOE fueleconomy.gov – vehicle record 49960 (2026 Hyundai Ioniq 5 RWD)](https://www.fueleconomy.gov/ws/rest/vehicle/49960) · official · published 2025-12 (last modified) · scope: US
  - Quote 3: "Ioniq 5 RWD" … range "318"
  - Flags: none for 84 kWh (two sources); SINGLE SOURCE for 318 miles; CONFLICT with Q4-F5
- **Q4-F5** Kelley Blue Book's spec pages list lower ranges than the EPA records above: 327 miles for the Model Y Long Range, 307 miles for the Equinox EV and 290 miles for the Ioniq 5 SE/SEL, without saying which drive type (probably the all-wheel-drive versions).
  - Source: [Kelley Blue Book – 2026 Hyundai Ioniq 5 specs](https://www.kbb.com/hyundai/ioniq-5/2026/specs/) · industry · published undated · scope: US
  - Quote: "290 miles"
  - Flags: CONFLICT with Q4-F2, Q4-F3, Q4-F4
- **Q4-F6** DC fast chargers (up to 500 kW) add roughly 100 to 200+ miles of range in 30 minutes, but the actual charging power depends on the car and on how full the battery already is.
  - Source: [U.S. DOE Alternative Fuels Data Center – Electric Vehicle Charging Stations](https://afdc.energy.gov/fuels/electricity-stations) · official · published undated · scope: US
  - Quote: "Approximately 100 to 200+ miles of range per 30 minutes of charging" … "Charging power varies by vehicle and battery state of charge."
  - Flags: SINGLE SOURCE
- **Q4-F7** In AAA's 2026 lab tests, cold weather (20 °F, about −7 °C) cut electric cars' range by 39% on average, while hot weather (95 °F, 35 °C) cut it by 8.5%.
  - Source: [NPR (via KPBS) – How well can EVs handle the heat and the cold? AAA put them to the test](https://www.kpbs.org/news/economy/2026/05/01/how-well-can-evs-handle-the-heat-and-the-cold-aaa-put-them-to-the-test) · news · published 2026-05 · scope: US
  - Quote: "Cold weather cut vehicles' range by a whopping 39%." … "hot temperatures reduced range by an average of 8.5%."
  - Flags: SINGLE SOURCE (see Q4-F8 for a milder real-world figure at a warmer temperature)
- **Q4-F8** Real-world data from more than 30,000 US electric cars shows they keep on average 78% of their range at freezing (32 °F / 0 °C), from 88% for the best model to 69% for the worst; many cars also limit charging when the battery is cold, which slows charging.
  - Source: [Recurrent – Winter EV range loss study](https://www.recurrentauto.com/research/winter-ev-range-loss) · industry · published 2025-11 · scope: US
  - Quote: "average 78% of their range in freezing temperatures" … "many cars limit the charging voltage when the battery is cold"
  - Flags: SINGLE SOURCE

## Q5. What causes an electric car battery's capacity to change over time, how much capacity do batteries keep after 5 and 10 years according to large real-world fleet datasets, and what capacity warranties do major automakers offer?

**Short answer:** Slow side reactions inside the cell (a growing surface film, lithium plating, worn-out electrode material) gradually use up lithium, and heat, very high or low charge levels and frequent high-power fast charging speed this up. Fleet data shows modest loss: about 2.3% a year on average across 22,700 vehicles, and about 95% of original range kept after five years; battery replacements are rare in recent models. Warranties typically promise at least 70% capacity for 8 years or 100,000 miles (10 years for Hyundai and Kia). No solid 10-year figure was found (see Gaps).

- **Q5-F1** Batteries lose capacity because of slow side reactions inside the cell: a surface layer (called the SEI) keeps growing, lithium can plate out as metal, and electrode material wears out; how fast this happens depends on temperature, charging speed, the charge level the car sits at, and how deeply it is drained.
  - Source: [Madabattula, "Linking Calendar and Cycle Ageing in Lithium-Ion Batteries" (arXiv:2604.09217)](https://arxiv.org/abs/2604.09217) · academic · published 2026-04 · scope: global
  - Quote: "solid-electrolyte interphase (SEI) growth, lithium plating, and active material loss in both electrodes"
  - Flags: none (preprint, not peer-reviewed)
- **Q5-F2** Heat and frequent use of the fastest chargers speed up ageing: in Geotab's fleet data, cars relying on DC fast charging above 100 kW lost up to 3.0% a year, and cars in hot climates about 0.4 percentage points a year more than in mild ones (2025 data).
  - Source: [Geotab – New Geotab data shows EV battery health remains strong as fast charging use increases](https://www.geotab.com/press-release/ev-battery-health-degradation-fast-charging-study) · industry · published 2026-01 · scope: Canada, US, Europe fleets
  - Quote: "high-power DC fast charging above 100 kW experience degradation rates of up to 3.0% per year" … "hot climates degrade around 0.4% faster per year"
  - Flags: SINGLE SOURCE
- **Q5-F3** Across more than 22,700 electric vehicles of 21 makes and models, batteries lost on average 2.3% of their capacity per year, up from 1.8% in Geotab's 2024 study.
  - Source: [Geotab – New Geotab data shows EV battery health remains strong as fast charging use increases](https://www.geotab.com/press-release/ev-battery-health-degradation-fast-charging-study) · industry · published 2026-01 · scope: Canada, US, Europe fleets
  - Quote: "shows an average annual battery degradation rate of 2.3%" … "compared to 1.8% in Geotab’s 2024 findings"
  - Flags: SINGLE SOURCE (Gizmodo, 2026-07, reports the same study; not independent)
- **Q5-F4** According to EV data company Recurrent, today's average electric car keeps 97% of its original range after three years and 95% after five years.
  - Source: [Gizmodo – New data shows EV batteries are lasting longer than initially expected](https://gizmodo.com/new-data-shows-ev-batteries-are-lasting-longer-than-initially-expected-2000790585) · news · published 2026-07 · scope: US
  - Quote: "Today's average EV retains 97% of its original range after three years and 95% after five years"
  - Flags: SINGLE SOURCE (range, not measured capacity; Recurrent's own page was not found)
- **Q5-F5** Range shown on the dashboard can hide early ageing: some automakers keep 100% of the original range over five years through software, even though the battery has still aged.
  - Source: [Recurrent – How long do EV batteries last?](https://www.recurrentauto.com/research/how-long-do-ev-batteries-last) · industry · published 2025-11 · scope: US
  - Quote: "several automakers maintain 100% of their original range over five years"
  - Flags: none
- **Q5-F6** Battery replacements are rare and falling: about 8.5% for first-generation electric cars (2011–2016), 2% for the second generation, and 0.3% for models from 2022 onward.
  - Source: [Recurrent – How long do EV batteries last?](https://www.recurrentauto.com/research/how-long-do-ev-batteries-last) · industry · published 2025-11 · scope: US
  - Quote: "For modern EVs, from 2022 and onwards, the replacement rate is 0.3%."
  - Flags: SINGLE SOURCE (Gizmodo, 2026-07, repeats the 0.3% figure from the same data)
- **Q5-F7** Hyundai and Kia guarantee their EV batteries for 10 years or 100,000 miles, promising at least 70% of original capacity (US terms, as of 2025).
  - Source: [GreenCars – EV warranties and exclusions](https://www.greencars.com/guides/ev-warranties-and-exclusions) · news · published 2025-09 (last updated) · scope: US
  - Quote: "offer extended battery warranties of 10 years or 100,000 miles, also with a 70 percent minimum capacity promise."
  - Flags: SINGLE SOURCE (automaker warranty booklets could not be opened)
- **Q5-F8** Most other major automakers (GM, Ford, Nissan) guarantee 8 years or 100,000 miles with at least 70% capacity; Tesla guarantees 8 years with a mileage limit of 100,000–150,000 miles depending on model, also at 70% (for example, the Model 3 Standard Range: 70% for 100,000 miles or 8 years).
  - Source: [GreenCars – EV warranties and exclusions](https://www.greencars.com/guides/ev-warranties-and-exclusions) · news · published 2025-09 (last updated) · scope: US
  - Quote: "provides an 8-year or 100,000-mile battery warranty with a 70 percent capacity guarantee."
  - Source 2: [Recurrent – How long do EV batteries last?](https://www.recurrentauto.com/research/how-long-do-ev-batteries-last) · industry · published 2025-11 · scope: US
  - Quote 2: "guaranteed to stay at 70% original capacity for 100,000 miles or 8 years, whichever happens first"
  - Flags: none for Tesla Model 3 terms (two sources); SINGLE SOURCE for GM, Ford, Nissan terms

## Q6. How much did an electric car battery pack cost per kWh in 2015 vs. the latest full year, and what share of a new electric car's price does the battery make up today?

**Short answer:** In 2025 the average battery pack for a battery-electric car cost about $99 per kWh (all battery uses: $108 per kWh, down 8% in a year). The US Department of Energy put the 2015 cost of an EV battery at about $268 per kWh, so costs have fallen by roughly two-thirds, though the two figures use different methods. China has the cheapest packs. No reliable 2024-or-later figure was found for the battery's share of a car's price (see Gaps).

- **Q6-F1** The average lithium-ion battery pack (all uses) cost $108 per kWh in 2025, a record low and 8% less than in 2024.
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour despite rising metal prices](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: global
  - Quote: "lithium-ion battery pack prices have dropped 8% since 2024 to a record low of $108 per kilowatt-hour"
  - Source 2: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote 2: "Average battery prices declined by 8% in 2025"
  - Flags: none for the 8% fall (two sources); SINGLE SOURCE for $108/kWh
- **Q6-F2** Battery packs for battery-electric cars were the cheapest in transport, at an average of $99 per kWh in 2025.
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: global
  - Quote: "Battery electric vehicles (BEVs) packs were the cheapest in the transport segment at $99/kWh"
  - Flags: SINGLE SOURCE
- **Q6-F3** In 2015, the US Department of Energy estimated the cost of an electric car battery at about $268 per kWh (in 2014 dollars, modelled cost at 100,000 packs a year).
  - Source: [U.S. DOE Vehicle Technologies Office – Overview of the DOE VTO Advanced Battery R&D Program (Howell et al.)](https://www.energy.gov/sites/prod/files/2016/06/f32/es000_howell_2016_o_web.pdf) · official · published 2016-06 · scope: US
  - Quote: "2015 DOE cost $268/kWh"
  - Flags: SINGLE SOURCE (modelled production cost in 2014 dollars; not the same method as BNEF's 2025 market survey)
- **Q6-F4** Battery packs are cheapest in China (about $84 per kWh on average in 2025); packs in North America cost about 44% more and in Europe about 56% more.
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: China, North America, Europe
  - Quote: "Average battery pack prices were lowest in China, at $84/kWh."
  - Source 2: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: China, North America, Europe
  - Quote 2: "In 2025, battery pack prices in China were 30% lower than in North America, and 35% lower than in Europe"
  - Flags: none for the regional gap (both sources agree); SINGLE SOURCE for $84/kWh
- **Q6-F5** The material in the positive electrode (cathode) is the biggest single cost in a cell: 40–50% of the cell production cost for NMC and 25–30% for LFP (China, 2024), one reason LFP is cheaper.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: China
  - Quote: "accounting for 40-50% for NMC batteries and 25-30% for LFP batteries"
  - Flags: SINGLE SOURCE
- **Q6-F6** BloombergNEF expects battery pack prices to fall again in 2026.
  - Source: [BloombergNEF – Lithium-ion battery pack prices fall to $108 per kilowatt-hour](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/) · industry · published 2025-12 · scope: global
  - Quote: "BNEF expects pack prices to decrease again in 2026"
  - Flags: none

## Q7. Which next-generation battery types have major automakers or battery makers announced for mass production, with what target dates, and what gains in range, charging time or cost do they claim?

**Short answer:** Three directions stand out. Solid-state batteries: Toyota (with Idemitsu) aims to launch cars with them in 2027–2028 and BYD from 2027, with mass production around 2030; makers claim faster charging and more energy, but the IEA notes these gains are not yet proven on the road. Sodium-ion: CATL's Naxtra cells (up to 175 Wh/kg) go into a Changan car in 2026, trading some energy for low cost and strong cold-weather performance. Manganese-rich (LMR): GM and LG plan US production by 2028, claiming 33% more energy than the best LFP cells at similar cost.

- **Q7-F1** Toyota and its partner Idemitsu aim to bring electric cars with all-solid-state batteries to market in 2027–2028; Idemitsu began building a large pilot plant for the solid electrolyte in January 2026, due for completion in 2027.
  - Source: [Idemitsu Kosan – Final Investment Decision and Construction Start for Large Pilot Facility for Solid Electrolytes](https://www.idemitsu.com/jp/news/2025/260129_en.pdf) · company · published 2026-01 · scope: Japan / global
  - Quote: "aims to commercialize all-solid-state battery-equipped electric vehicles (hereinafter referred to as “BEVs”) in 2027–2028"
  - Source 2: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote 2: "has announced plans to launch its first all-solid-state battery-powered vehicle by 2028."
  - Flags: none
- **Q7-F2** Makers say solid-state batteries will charge faster and deliver more power because ions move more easily through a solid electrolyte, and are expected to store more energy and last longer.
  - Source: [Idemitsu Kosan – Final Investment Decision and Construction Start for Large Pilot Facility for Solid Electrolytes](https://www.idemitsu.com/jp/news/2025/260129_en.pdf) · company · published 2026-01 · scope: global
  - Quote: "Ions move more easily, enabling shorter charging times and higher power output for BEVs."
  - Flags: none (company claim; see Q7-F4)
- **Q7-F3** BYD plans to sell its first car with all-solid-state batteries from 2027 and to start mass production from 2030; Samsung has set similar timelines.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote: "plans to sell its first EV using all-SSB from 2027 and to begin mass production from 2030"
  - Flags: SINGLE SOURCE
- **Q7-F4** The IEA cautions that the promised longer range and better safety of solid-state batteries have not yet been shown in real-world use, and that early costs will be high, keeping them in premium cars until the early 2030s.
  - Source: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote: "these advantages have not yet been demonstrated in real-world applications"
  - Flags: none
- **Q7-F5** CATL's Naxtra sodium-ion battery stores up to 175 Wh/kg and is due to enter mass production in 2026; CATL expects 10,000–20,000 electric cars to use sodium-ion batteries this year.
  - Source: [electrive – CATL targets up to 20,000 vehicles with sodium-ion batteries](https://www.electrive.com/2026/06/26/catl-targets-up-to-20000-vehicles-with-sodium-ion-batteries/) · news · published 2026-06 · scope: China
  - Quote: "expects to equip between 10,000 and 20,000 electric vehicles with sodium-ion batteries this year"
  - Source 2: [IEA – Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries) · international · published 2026-05 · scope: global
  - Quote 2: "The latest sodium‑ion cells can reach up to 175 Wh/kg"
  - Flags: none for 175 Wh/kg (two sources); SINGLE SOURCE for 10,000–20,000 cars
- **Q7-F6** The first mass-produced passenger car announced with this sodium-ion battery is the Changan Nevo A06 (45 kWh), unveiled in February 2026 with a claimed range of over 400 km on China's test cycle and over 90% of capacity kept at −40 °C.
  - Source: [CarNewsChina – Changan and CATL unveil world's first mass-produced sodium-ion passenger EV](https://carnewschina.com/2026/02/05/changan-and-catl-unveil-worlds-first-mass-produced-sodium-ion-passenger-ev/) · news · published 2026-02 · scope: China
  - Quote: "The unveiled Changan Nevo A06 is equipped with a 45 kWh sodium-ion CATL Naxtra battery"
  - Flags: SINGLE SOURCE (range and cold-weather figures are company claims)
- **Q7-F7** GM and LG Energy Solution plan to start US production of lithium manganese-rich (LMR) cells by 2028, for pickups and large SUVs, claiming 33% more energy than LFP cells at a similar cost and over 400 miles of range in an electric pickup.
  - Source: [electrive – GM and LGES want to launch LMR battery cells on the market](https://www.electrive.com/2025/05/14/gm-and-lges-want-to-launch-lmr-battery-cells-on-the-market) · news · published 2025-05 · scope: US
  - Quote: "33 per cent higher energy density than conventional lithium iron phosphate (LFP) cells at a similar cost"
  - Flags: SINGLE SOURCE
- **Q7-F8** Mercedes-Benz aims to put solid-state batteries into series production by the end of the decade, and Toyota has partnered with Sumitomo Metal Mining to mass-produce cathode material for its solid-state cells.
  - Source: [Electrek – Toyota aims to launch world's first all-solid-state EV batteries](https://electrek.co/2025/10/08/toyota-aims-to-launch-worlds-first-all-solid-state-ev-batteries/) · news · published 2025-10 · scope: global
  - Quote: "aims to bring solid-state batteries into series production by the end of the decade"
  - Flags: SINGLE SOURCE

## Gaps

- Q1: The U.S. DOE (energy.gov) and Argonne explainer pages on how lithium-ion batteries work could not be opened (404/403), so the basics rest on two university pages and a 2012 DOE/PNNL fact sheet.
- Q2: No national-lab page on battery management or cooling could be opened (NREL's site did not resolve). The 15–35 °C working range (Q2-F8) and the 15% cell-to-cell variation (Q2-F6) have one source each. A real example of cell counts in a specific car's pack was not found.
- Q3: The brief asks for the share of new *cars* using each chemistry; the opened sources only give shares of battery *capacity* deployed, across all EV types. Only the IEA gave 2025 shares on a page I opened. No 2024-or-later lab study comparing LFP and NMC fire safety head-to-head was found (Sandia's study did not test NMC).
- UNVERIFIED: other trackers report different 2025 LFP shares (search snippets cited about 48% of EV batteries and about 61% of all battery demand, attributed to various firms); these pages were not opened.
- Q4: Official 10–80% fast-charging times for the Model Y, Equinox EV and Ioniq 5 could not be confirmed (Tesla, Chevrolet and Hyundai US pages were blocked or empty). The global best-seller ranking for 2025 could not be confirmed on an opened page (CleanTechnica returned 403); Q4-F1 is US-only. Hyundai already sells a 2027 Ioniq 5, but 2026 EPA records were used. The EPA records do not state battery size, so battery sizes come from Kelley Blue Book and Hyundai.
- UNVERIFIED: Ioniq 5 charges 10–80% in about 18–20 minutes on a 350 kW charger; Equinox EV takes about 35–44 minutes 10–80% in tester reports; GM has not published an official 10–80% time (all from search snippets, not opened pages).
- Q4: Geotab's temperature tool (EVs at 54% of rated range at −15 °C) was opened but is dated 2023, so it was left out under the brief's 2024-onward rule.
- Q5: No large real-world dataset opened gave capacity kept after 10 years. UNVERIFIED: a straight-line projection of Geotab's 2.3% a year would give roughly 77% after 10 years, but this is my arithmetic, and Recurrent says ageing follows an S-shaped curve rather than a straight line. Automaker warranty booklets could not be opened (blocked), so warranty terms come from GreenCars and Recurrent.
- Q6: No 2024-or-later source was found for the battery's share of a new electric car's price. UNVERIFIED: older estimates put it around 30–40% (a 2020 Bain forecast said about 30% of manufacturing cost for compact EVs); at $99/kWh, an 84 kWh pack would cost about $8,300, but that is my arithmetic and is the automaker's cost, not the retail price.
- Q6: The 2015 baseline ($268/kWh, DOE modelled cost in 2014 dollars) is not from the same series as the 2025 figure (BNEF market survey). A like-for-like BNEF 2015 value was not found on an opened page. UNVERIFIED: a search snippet cited BNEF's 2015 pack price as about $384/kWh in 2020 dollars.
- Q7: UNVERIFIED: Toyota's first solid-state cars would have about 1,000 km range and charge 10–80% in about 10 minutes (from Toyota's 2023 roadmap, seen only in search snippets; no 2024-or-later page opened confirms it). No claimed cost figures for solid-state batteries were found.

## Sources opened

1. [Lithium-Ion Battery](https://www.cei.washington.edu/research/energy-storage/lithium-ion-battery/), Clean Energy Institute, University of Washington, undated
2. [Discharge and charge process of a conventional lithium-ion battery cell](https://www.epe.ed.tum.de/en/ees/information-material/discharge-and-charge-process-of-a-conventional-lithium-ion-battery-cell), Technical University of Munich, undated
3. [Lithium-Ion Batteries for Stationary Energy Storage (fact sheet)](https://www.energy.gov/sites/default/files/Li-ion.pdf), U.S. DOE Office of Electricity / Pacific Northwest National Laboratory, 2012-10
4. [Global EV Outlook 2026: Electric vehicle batteries](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-batteries), International Energy Agency, 2026-05
5. [Global EV Outlook 2026 (report page, used for publication date)](https://www.iea.org/reports/global-ev-outlook-2026), International Energy Agency, 2026-05
6. [Battery Glossary: Cell to Pack](https://inside.lgensol.com/en/2025/12/battery-glossary-cell-to-pack/), LG Energy Solution, 2025-12
7. [Batteries 101: Battery packs](https://docs.ionworks.com/guide/batteries-101/battery-packs), Ionworks, undated
8. [Cell Balancing Paradigms (abstract)](https://arxiv.org/abs/2411.05478), Itagi et al., arXiv, 2024-11
9. [Cell Balancing Paradigms (full text)](https://arxiv.org/html/2411.05478), Itagi et al., arXiv, 2024-11
10. [How Do All-Electric Cars Work?](https://afdc.energy.gov/vehicles/how-do-all-electric-cars-work), U.S. DOE Alternative Fuels Data Center, undated
11. [Batteries for Electric Vehicles](https://afdc.energy.gov/vehicles/electric-batteries), U.S. DOE Alternative Fuels Data Center, undated (opened, not cited)
12. [Advances in battery thermal management: Current landscape and future directions](https://researchwith.stevens.edu/en/publications/advances-in-battery-thermal-management-current-landscape-and-futu/), Nasiri & Hadim, Stevens Institute of Technology / Renewable and Sustainable Energy Reviews, 2024-08
13. [Multi-scale thermal stability study of commercial lithium-ion batteries](https://www.sandia.gov/research/publications/details/multi-scale-thermal-stability-study-of-commercial-lithium-ion-batteries-as-2019-09-30/), Sandia National Laboratories, 2019-09
14. [Global lithium ion battery demand rose 29% in 2025](https://source.benchmarkminerals.com/article/global-lithium-ion-battery-demand-rose-29-in-2025), Benchmark Mineral Intelligence, 2026-01
15. [Electric Vehicle Sales Report Q4 2025](https://www.coxautoinc.com/wp-content/uploads/2026/01/Q4-2025-Kelley-Blue-Book-EV-Sales-Report.pdf), Cox Automotive / Kelley Blue Book, 2026-01
16. [Vehicle record 49743: 2026 Tesla Model Y Long Range RWD](https://www.fueleconomy.gov/ws/rest/vehicle/49743), U.S. EPA / DOE fueleconomy.gov, 2026-02
17. [Vehicle record 49960: 2026 Hyundai Ioniq 5 RWD](https://www.fueleconomy.gov/ws/rest/vehicle/49960), U.S. EPA / DOE fueleconomy.gov, 2025-12
18. [Vehicle record 49953: 2026 Chevrolet Equinox EV FWD](https://www.fueleconomy.gov/ws/rest/vehicle/49953), U.S. EPA / DOE fueleconomy.gov, 2025-10
19. [2026 Tesla Model Y by model (MPGe listing)](https://www.fueleconomy.gov/feg/bymodel/2026_Tesla_Model_Y.shtml), U.S. EPA / DOE fueleconomy.gov, undated (opened, not cited)
20. [2026 Hyundai Ioniq 5 by model (MPGe listing)](https://www.fueleconomy.gov/feg/bymodel/2026_Hyundai_Ioniq_5.shtml), U.S. EPA / DOE fueleconomy.gov, undated (opened, not cited)
21. [2026 Tesla Model Y specs](https://www.kbb.com/tesla/model-y/2026/specs/), Kelley Blue Book, undated
22. [2026 Chevrolet Equinox EV specs](https://www.kbb.com/chevrolet/equinox-ev/2026/specs/), Kelley Blue Book, undated
23. [2026 Hyundai Ioniq 5 specs](https://www.kbb.com/hyundai/ioniq-5/2026/specs/), Kelley Blue Book, undated
24. [Hyundai IONIQ 5: con il Model Year 27 la gamma si rinnova](https://www.hyundai.news/it/articles/press-releases/hyundai-ioniq-5-con-il-model-year-27-la-gamma-si-rinnova.html), Hyundai Motor Company Italy, 2026-07
25. [Electric Vehicle Charging Stations](https://afdc.energy.gov/fuels/electricity-stations), U.S. DOE Alternative Fuels Data Center, undated
26. [Developing Infrastructure to Charge Electric Vehicles](https://afdc.energy.gov/fuels/electricity-infrastructure-development), U.S. DOE Alternative Fuels Data Center, undated (opened, not cited)
27. [How well can EVs handle the heat and the cold? AAA put them to the test](https://www.kpbs.org/news/economy/2026/05/01/how-well-can-evs-handle-the-heat-and-the-cold-aaa-put-them-to-the-test), NPR via KPBS, 2026-05
28. [Winter EV range loss](https://www.recurrentauto.com/research/winter-ev-range-loss), Recurrent, 2025-11
29. [To what degree does temperature impact EV range?](https://www.geotab.com/uk/blog/ev-range/), Geotab, 2023-08 (opened, not cited: before 2024)
30. [New Geotab data shows EV battery health remains strong as fast charging use increases](https://www.geotab.com/press-release/ev-battery-health-degradation-fast-charging-study), Geotab, 2026-01
31. [New Geotab data highlights how EV batteries can last 20 years or more](https://www.geotab.com/uk/press-release/2024-battery-degradation), Geotab, 2024-09 (opened, not cited)
32. [Linking Calendar and Cycle Ageing in Lithium-Ion Batteries](https://arxiv.org/abs/2604.09217), Madabattula, arXiv, 2026-04
33. [How long do EV batteries last?](https://www.recurrentauto.com/research/how-long-do-ev-batteries-last), Recurrent, 2025-11
34. [New data shows EV batteries are lasting longer than initially expected](https://gizmodo.com/new-data-shows-ev-batteries-are-lasting-longer-than-initially-expected-2000790585), Gizmodo, 2026-07
35. [EV warranties and exclusions](https://www.greencars.com/guides/ev-warranties-and-exclusions), GreenCars, 2025-09 (last updated)
36. [Lithium-ion battery pack prices fall to $108 per kilowatt-hour despite rising metal prices](https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/), BloombergNEF, 2025-12
37. [Battery pack prices fall to an average of $132/kWh](https://about.bnef.com/insights/clean-energy/battery-pack-prices-fall-to-an-average-of-132-kwh-but-rising-commodity-prices-start-to-bite/), BloombergNEF, 2021-11 (opened, not cited: before 2024)
38. [FOTW #1354: Electric Vehicle Battery Pack Costs for a Light-Duty Vehicle in 2023 Are 90% Lower than in 2008](https://www.energy.gov/cmei/vehicles/articles/fotw-1354-august-5-2024-electric-vehicle-battery-pack-costs-light-duty), U.S. DOE Vehicle Technologies Office, 2024-08 (opened, not cited: 2023 data, no 2015 value in text)
39. [FOTW #1272: Electric Vehicle Battery Pack Costs in 2022 Are Nearly 90% Lower than in 2008](https://www.energy.gov/eere/vehicles/articles/fotw-1272-january-9-2023-electric-vehicle-battery-pack-costs-2022-are-nearly), U.S. DOE Vehicle Technologies Office, 2023-01 (opened, not cited)
40. [Overview of the DOE VTO Advanced Battery R&D Program](https://www.energy.gov/sites/prod/files/2016/06/f32/es000_howell_2016_o_web.pdf), U.S. DOE Vehicle Technologies Office (Howell et al.), 2016-06
41. [Volume-weighted average lithium-ion battery pack and cell prices (chart)](https://datawrapper.dwcdn.net/D7K5I/1/), Datawrapper (publisher not shown), undated (opened, not cited)
42. [Bain: electric cars account for 12% of global new car sales in 2025](https://news.metal.com/es/newscontent/101322673-bain-electric-cars-account-for-12-of-global-new-car-sales-in-2025-the-battery-pack-dropped-to-100-kwh), SMM News, 2020-11 (opened, not cited: 2020 forecast)
43. [Final Investment Decision and Construction Start for Large Pilot Facility for Solid Electrolytes](https://www.idemitsu.com/jp/news/2025/260129_en.pdf), Idemitsu Kosan, 2026-01
44. [GM and LGES want to launch LMR battery cells on the market](https://www.electrive.com/2025/05/14/gm-and-lges-want-to-launch-lmr-battery-cells-on-the-market), electrive, 2025-05
45. [CATL targets up to 20,000 vehicles with sodium-ion batteries](https://www.electrive.com/2026/06/26/catl-targets-up-to-20000-vehicles-with-sodium-ion-batteries/), electrive, 2026-06
46. [Changan and CATL unveil world's first mass-produced sodium-ion passenger EV](https://carnewschina.com/2026/02/05/changan-and-catl-unveil-worlds-first-mass-produced-sodium-ion-passenger-ev/), CarNewsChina, 2026-02
47. [Toyota aims to launch world's first all-solid-state EV batteries](https://electrek.co/2025/10/08/toyota-aims-to-launch-worlds-first-all-solid-state-ev-batteries/), Electrek, 2025-10
