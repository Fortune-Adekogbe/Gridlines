**Generation anomaly investigation — 14 November 2026**

The tables below describe the original source values. The dashboard now excludes the 106 audited extreme plant readings and their 105 affected grid hours before charts, summaries, and daily backfill. Each listed reading exceeds twice its capacity reference and twice the largest other positive reading within that reference on the same day. Exclusions match the original date, hour, plant, and value; corrected source values are accepted. Additional capacity and statistical candidates remain unfiltered pending review. [Active exclusion list](generation_exclusions.json)

Eight plants are implicated in the 13 recorded grid hours above the supplied 5,801.84 MW benchmark. Shiroro appears in five of those hours. There are 14 suspect plant readings because Shiroro and Odukpani spike in the same hour on 5 March 2019.

The scan covers 3,252 available dates from 2017-11-03 through 2026-11-14, 78,048 national hourly totals, and 1,554,120 normalized station readings. Times below use the source’s Nigerian local-time labels, including its 24:00 label.

Every one of the 13 national spikes, and every associated suspect plant value, was checked against the selected historical date on the public source website. All matched MongoDB. The source page also confirmed eight examples below the national benchmark. The exact intended replacement readings remain unverified. [NIGGRID Generation Profile](https://niggrid.org/GenerationProfile2)

**Every recorded grid hour above 5,801.84 MW**

| Date | Time | Grid MW | Suspect plant reading MW | Other positive readings that day MW |
| --- | --- | --- | --- | --- |
| 2018-01-22 | 04:00 | 8,885.9 | IHOVBOR NIPP 7,305 | IHOVBOR NIPP 73.5–179.4 |
| 2018-02-16 | 18:00 | 17,089.6 | EGBIN 15,647 | EGBIN 623–711 |
| 2018-05-31 | 17:00 | 96,492.9 | IHOVBOR NIPP 94,777 | IHOVBOR NIPP 75.5–173.6 |
| 2018-09-21 | 08:00 | 16,733.2 | SHIRORO 15,089 | SHIRORO 391–446 |
| 2019-01-01 | 02:00 | 16,422.7 | SHIRORO 14,580 | SHIRORO 105–297 |
| 2019-01-12 | 14:00 | 101,708.5 | GEREGU 100,322 | GEREGU 280–413 |
| 2019-01-28 | 14:00 | 11,465.9 | JEBBA 9,688 | JEBBA 245–372 |
| 2019-03-02 | 12:00 | 12,220.6 | KAINJI 9,522 | KAINJI 375–422 |
| 2019-03-05 | 21:00 | 6,142 | ODUKPANI NIPP 1,257<br>SHIRORO 1,703 | ODUKPANI NIPP 190–320.7<br>SHIRORO 262–432 |
| 2019-05-19 | 16:00 | 130,215.7 | SHIRORO 127,259 | SHIRORO 115–264 |
| 2019-05-22 | 06:00 | 14,938.7 | GEREGU NIPP 12,645 | GEREGU NIPP 160–275 |
| 2019-09-10 | 06:00 | 17,465.2 | SHIRORO 15,059 | SHIRORO 353–468 |
| 2020-04-19 | 15:00 | 11,800.4 | GEREGU 8,193 | GEREGU 240–316 |

The comparison ranges exclude zeros, the listed hour, and other readings above the plant’s capacity reference. They provide context rather than replacement values. On 5 March 2019 at 21:00, Odukpani reads 1,257 MW between 318.3 and 320.7 MW, while Shiroro reads 1,703 MW between 432 and 428 MW.

**Where the total comes from**

The scraper copies the website’s national total row into `Hour Total`. It also copies the individual station rows. The row with an empty company name becomes `Hour Total`, and the hourly values are stored as source text. [Scraper extraction](selenium_scraper.py#L45)

After station aliases and MongoDB dotted-name duplicates are normalized, all 77,014 nonzero comparable archive hours reconcile to the station sum within 0.01 MW. In particular, each of the 13 excessive totals equals its plant-level sum. The total therefore carries the same bad inputs as the station data. Arithmetic agreement does not establish measurement accuracy.

None of the reported daily peak, off-peak, or 06:00 values in `gridlines` exceeded the benchmark. Before the quality filter, the older `gridmoments` records exposed these large spikes when their hourly maxima filled missing daily peaks. Daily backfill now uses accepted hours and marks incomplete profiles. The database retains the original source values. [Daily backfill](grid_data.py)

**Wider station checks**

A conservative screen found 106 station readings above twice their installed-capacity reference, across 20 plants and 105 distinct grid hours. Fourteen of these readings occur in the 13 national-record breaches. The remaining 92 occur in hours whose national totals remain below 5,801.84 MW. Shiroro accounts for 16 of the 106 readings, including 11 below the national benchmark.

Capacity references come from NERC’s December 2024 installed-capacity table. For example, the references are 600 MW for Shiroro, 435 MW for each Geregu station, and 1,320 MW for Egbin. These are investigation thresholds, not date-specific certifications of historical capacity. [NERC 2024 Annual Report, Table 4.3, printed page 80](https://nerc.gov.ng/wp-content/uploads/2025/07/2024-Annual-Report.pdf#page=92)

| Plant | Above 2× capacity reference | In grid hours above benchmark | In grid hours below benchmark |
| --- | --- | --- | --- |
| SHIRORO | 16 | 5 | 11 |
| TRANS-AMADI | 13 | 0 | 13 |
| GEREGU | 10 | 2 | 8 |
| JEBBA | 10 | 1 | 9 |
| GEREGU NIPP | 8 | 1 | 7 |
| ODUKPANI NIPP | 7 | 1 | 6 |
| OMOTOSHO NIPP | 7 | 0 | 7 |
| DADINKOWA | 6 | 0 | 6 |
| AFAM VI | 5 | 0 | 5 |
| IBOM POWER | 4 | 0 | 4 |
| IHOVBOR NIPP | 4 | 2 | 2 |
| RIVERS IPP | 4 | 0 | 4 |
| ALAOJI NIPP | 3 | 0 | 3 |
| KAINJI | 2 | 1 | 1 |
| PARAS ENERGY | 2 | 0 | 2 |
| DELTA | 1 | 0 | 1 |
| EGBIN | 1 | 1 | 0 |
| OLORUNSOGO | 1 | 0 | 1 |
| OMOKU | 1 | 0 | 1 |
| OMOTOSHO | 1 | 0 | 1 |

**Examples below the grid benchmark checked on the source website**

| Date | Time | Plant | Plant MW | Previous hour MW | Next hour MW | Grid MW |
| --- | --- | --- | --- | --- | --- | --- |
| 2017-12-19 | 14:00 | OMOTOSHO | 3,430.3 | 150.1 | 151.1 | 4,566.8 |
| 2018-06-20 | 05:00 | KAINJI | 5,061.39 | 186 | 0 | 5,192.99 |
| 2019-05-02 | 22:00 | SHIRORO | 1,508 | 397 | 398 | 5,302.7 |
| 2019-05-30 | 06:00 | RIVERS IPP | 1,100 | 110 | 110 | 4,446.1 |
| 2019-11-18 | 23:00 | EGBIN | 2,406 | 593 | 539 | 5,599 |
| 2024-07-03 | 17:00 | DADINKOWA | 138.4 | 28.21 | 28.18 | 2,993.72 |
| 2025-01-06 | 12:00 | IBOM POWER | 303 | 30.1 | 30 | 4,649.6 |
| 2026-06-04 | 16:00 | TRANS-AMADI | 225.8 | 25.2 | 20.4 | 4,437.7 |

These include a decimal-like jump at Rivers IPP from 110 to 1,100 and back to 110 MW, and at Ibom from 30.1 to 303 and back to 30 MW. Other cases contain extra digits or much larger discontinuities. This supports multiple entry or formatting problems. It does not establish a common correction factor or prove which upstream process introduced each error. [NIGGRID historical source](https://niggrid.org/GenerationProfile2)

**Complete screening rules and limits**

The national screen selects every normalized hourly grid value strictly above the user-supplied 5,801.84 MW benchmark. It identifies contributing stations above their capacity reference and compares their other readings that day.

The station screens also select every reading above 110% of its mapped December 2024 capacity reference, and every positive reading above five times that station’s same-day positive median when at least eight positive readings exist. The first rule produces 460 candidates, including the 106 extreme readings. The second produces 252 candidates, of which 126 are outside the capacity screen. There are 586 distinct station/date/hour candidates across both rules. Statistical candidates can include real operating changes. The tables below retain them for review.

Capacity references are mapped for 27 of the 32 normalized station names. AFAM III FAST POWER, GPAL, KASHIMBILA, MEPP, and NIGER DELTA POWER HOLDING COMPANY have no assigned capacity in this audit and receive only the statistical screen. Their absence from the capacity lists is not a clean bill of health. The organization-named NDPHC row remains in the plant sum because the archive totals include it.

The 10% margin avoids treating small rating differences as large anomalies. For context, there are 4,657 Dadinkowa readings and 2,968 Paras readings strictly above their 40 and 110 MW references; most do not clear that margin. A date-specific capacity register is needed before using such small exceedances as validation failures. Later plant extensions, especially after 2024, also need checking. Zeros are preserved as source readings and excluded only from the positive comparison baselines.

The scan examines high-generation anomalies. It cannot establish all missing, understated, duplicated, or otherwise inaccurate measurements. The full public-source verification covers the 13 national breaches and the eight selected examples, rather than every screening candidate.

**Implication for handling the data**

Preserve the source readings and record quality flags at plant, date, and hour level. Flag the corresponding national total when any contributing plant is suspect. Use validated hours for derived daily metrics and label incomplete days. Require independent evidence before recording a corrected value. Recomputing totals from unchanged plant readings reproduces the same errors, and a single division factor would assign unsupported replacements.

The investigation itself made no database changes. The subsequent dashboard quality filter preserves the original historical date range and source readings, with excluded readings available in a collapsed section below the charts.

<details>
<summary>All 106 readings above twice capacity reference</summary>

| Date | Time | Plant | Plant MW | Previous MW | Next MW | Grid MW | Website check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-11-21 | 13:00 | GEREGU NIPP | 1,217 | 124 | 129 | 2,605.7 | Unchecked |
| 2017-12-11 | 23:00 | IBOM POWER | 973 | 0 | 0 | 2,700 | Unchecked |
| 2017-12-19 | 14:00 | OMOTOSHO | 3,430.3 | 150.1 | 151.1 | 4,566.8 | Matched |
| 2018-01-10 | 22:00 | IHOVBOR NIPP | 1,074 | 106.4 | 108.8 | 2,240.5 | Unchecked |
| 2018-01-22 | 04:00 | IHOVBOR NIPP | 7,305 | 73.5 | 88.1 | 8,885.9 | Matched |
| 2018-02-16 | 18:00 | EGBIN | 15,647 | 647 | 667 | 17,089.6 | Matched |
| 2018-02-19 | 20:00 | GEREGU | 1,377 | 133 | 0 | 3,394.1 | Unchecked |
| 2018-02-22 | 05:00 | AFAM VI | 1,537 | 384 | 366 | 2,624.3 | Unchecked |
| 2018-02-24 | 21:00 | JEBBA | 1,164 | 344 | 356 | 2,911.4 | Unchecked |
| 2018-02-25 | 20:00 | AFAM VI | 1,550 | 274 | 0 | 3,342.3 | Unchecked |
| 2018-02-27 | 06:00 | AFAM VI | 1,764 | 0 | 255 | 3,563.8 | Unchecked |
| 2018-02-28 | 05:00 | AFAM VI | 1,573 | 386 | 0 | 2,838.3 | Unchecked |
| 2018-03-22 | 11:00 | GEREGU | 1,101 | 0 | 211 | 2,794.6 | Unchecked |
| 2018-04-17 | 11:00 | PARAS ENERGY | 1,662.6 | 68.6 | 68.6 | 2,623.8 | Unchecked |
| 2018-05-25 | 12:00 | OMOTOSHO NIPP | 1,021 | 105.7 | 95.1 | 2,340.4 | Unchecked |
| 2018-05-31 | 17:00 | IHOVBOR NIPP | 94,777 | 87.3 | 97.7 | 96,492.9 | Matched |
| 2018-06-20 | 05:00 | KAINJI | 5,061.39 | 186 | 0 | 5,192.99 | Matched |
| 2018-07-11 | 18:00 | GEREGU | 1,417 | 236 | 262 | 2,244.8 | Unchecked |
| 2018-07-29 | 05:00 | PARAS ENERGY | 581.2 | 63.8 | 65.4 | 1,010.3 | Unchecked |
| 2018-08-24 | 13:00 | JEBBA | 1,213 | 388 | 399 | 2,004.3 | Unchecked |
| 2018-09-09 | 07:00 | JEBBA | 1,161 | 331 | 331 | 2,636.2 | Unchecked |
| 2018-09-21 | 08:00 | SHIRORO | 15,089 | 439 | 440 | 16,733.2 | Matched |
| 2018-09-27 | 17:00 | SHIRORO | 1,721 | 439 | 440 | 3,723.1 | Unchecked |
| 2018-10-01 | 22:00 | SHIRORO | 1,440 | 441 | 438 | 3,671.6 | Unchecked |
| 2018-10-05 | 19:00 | JEBBA | 1,337 | 416 | 437 | 3,461.8 | Unchecked |
| 2018-10-19 | 14:00 | SHIRORO | 1,575 | 575 | 577 | 3,549.7 | Unchecked |
| 2018-10-20 | 16:00 | JEBBA | 1,231 | 441 | 351 | 2,852.9 | Unchecked |
| 2018-11-07 | 02:00 | SHIRORO | 1,485 | 486 | 403 | 2,703 | Unchecked |
| 2018-11-20 | 21:00 | OMOTOSHO NIPP | 1,116.6 | 99.8 | 205 | 4,523.1 | Unchecked |
| 2018-11-22 | 02:00 | OMOTOSHO NIPP | 1,090.1 | 195.1 | 197 | 2,495 | Unchecked |
| 2018-12-01 | 18:00 | GEREGU NIPP | 1,177 | 120 | 109 | 4,014.9 | Unchecked |
| 2018-12-05 | 21:00 | JEBBA | 1,257 | 445 | 434 | 2,939.8 | Unchecked |
| 2018-12-14 | 20:00 | JEBBA | 1,231 | 0 | 438 | 2,555.4 | Unchecked |
| 2018-12-23 | 12:00 | JEBBA | 1,158 | 312 | 339 | 3,409.9 | Unchecked |
| 2019-01-01 | 02:00 | SHIRORO | 14,580 | 201 | 201 | 16,422.7 | Matched |
| 2019-01-01 | 18:00 | OMOTOSHO NIPP | 1,015.4 | 104 | 108.1 | 3,089.2 | Unchecked |
| 2019-01-07 | 04:00 | IHOVBOR NIPP | 1,064 | 105.2 | 109.5 | 1,919.8 | Unchecked |
| 2019-01-07 | 16:00 | GEREGU NIPP | 1,304 | 251 | 216 | 3,442.9 | Unchecked |
| 2019-01-11 | 09:00 | GEREGU NIPP | 1,366 | 134 | 124 | 3,840.2 | Unchecked |
| 2019-01-12 | 14:00 | GEREGU | 100,322 | 0 | 409 | 101,708.5 | Matched |
| 2019-01-28 | 14:00 | JEBBA | 9,688 | 255 | 245 | 11,465.9 | Matched |
| 2019-03-02 | 12:00 | KAINJI | 9,522 | 404 | 409 | 12,220.6 | Matched |
| 2019-03-05 | 21:00 | ODUKPANI NIPP | 1,257 | 318.3 | 320.7 | 6,142 | Matched |
| 2019-03-05 | 21:00 | SHIRORO | 1,703 | 432 | 428 | 6,142 | Matched |
| 2019-03-06 | 07:00 | IBOM POWER | 701 | 80.7 | 76.4 | 4,088.5 | Unchecked |
| 2019-03-19 | 03:00 | TRANS-AMADI | 243.5 | 62.7 | 0 | 2,804.8 | Unchecked |
| 2019-04-20 | 20:00 | TRANS-AMADI | 246.5 | 55 | 177.8 | 2,632.5 | Unchecked |
| 2019-04-21 | 01:00 | ODUKPANI NIPP | 1,320.1 | — | 0 | 3,525.1 | Unchecked |
| 2019-04-22 | 12:00 | TRANS-AMADI | 224.6 | 0 | 0 | 3,459.5 | Unchecked |
| 2019-05-02 | 22:00 | SHIRORO | 1,508 | 397 | 398 | 5,302.7 | Matched |
| 2019-05-07 | 20:00 | ODUKPANI NIPP | 1,431 | 329.9 | 418.9 | 4,541.6 | Unchecked |
| 2019-05-19 | 16:00 | SHIRORO | 127,259 | 260 | 0 | 130,215.7 | Matched |
| 2019-05-22 | 06:00 | GEREGU NIPP | 12,645 | 215 | 199 | 14,938.7 | Matched |
| 2019-05-26 | 14:00 | ODUKPANI NIPP | 1,279.7 | 292.7 | 293.7 | 4,554.4 | Unchecked |
| 2019-05-29 | 01:00 | GEREGU NIPP | 940 | — | 0 | 3,892.4 | Unchecked |
| 2019-05-30 | 06:00 | RIVERS IPP | 1,100 | 110 | 110 | 4,446.1 | Matched |
| 2019-06-02 | 04:00 | GEREGU | 1,281 | 0 | 0 | 3,921.56 | Unchecked |
| 2019-06-05 | 22:00 | IBOM POWER | 799.9 | 0 | 93.2 | 4,314.8 | Unchecked |
| 2019-06-07 | 06:00 | OLORUNSOGO | 2,817.8 | 142.9 | 141.6 | 5,159.3 | Unchecked |
| 2019-06-16 | 09:00 | GEREGU | 881 | 160 | 209 | 3,638.1 | Unchecked |
| 2019-06-22 | 09:00 | RIVERS IPP | 1,130 | 140 | 130 | 3,999.5 | Unchecked |
| 2019-06-23 | 16:00 | OMOTOSHO NIPP | 1,065.2 | 110.4 | 109.1 | 4,466.6 | Unchecked |
| 2019-06-25 | 11:00 | RIVERS IPP | 1,150 | 0 | 150 | 4,383.8 | Unchecked |
| 2019-07-02 | 22:00 | RIVERS IPP | 1,481 | 148 | 148 | 5,035.4 | Unchecked |
| 2019-07-15 | 15:00 | IBOM POWER | 901 | 93.3 | 91.5 | 4,140.5 | Unchecked |
| 2019-07-25 | 05:00 | OMOTOSHO NIPP | 1,010.4 | 97.8 | 104 | 3,997.5 | Unchecked |
| 2019-09-08 | 19:00 | SHIRORO | 1,603 | 315 | 325 | 4,222.3 | Unchecked |
| 2019-09-10 | 06:00 | SHIRORO | 15,059 | 393 | 383 | 17,465.2 | Matched |
| 2019-09-14 | 20:00 | ALAOJI NIPP | 1,229.9 | 112.8 | 0 | 3,950.5 | Unchecked |
| 2019-10-08 | 21:00 | ALAOJI NIPP | 1,155 | 114.8 | 115.5 | 4,855.6 | Unchecked |
| 2019-10-11 | 14:00 | ALAOJI NIPP | 1,111.3 | 110.8 | 70.4 | 3,782.5 | Unchecked |
| 2019-10-12 | 04:00 | SHIRORO | 1,386 | 370 | 0 | 3,333.6 | Unchecked |
| 2019-10-15 | 14:00 | SHIRORO | 1,422 | 0 | 430 | 3,797 | Unchecked |
| 2019-10-23 | 12:00 | DELTA | 2,093 | 289 | 287 | 4,490.2 | Unchecked |
| 2019-10-23 | 19:00 | SHIRORO | 1,762 | 0 | 433 | 5,051 | Unchecked |
| 2019-11-06 | 17:00 | SHIRORO | 1,725 | 442 | 405 | 4,583.2 | Unchecked |
| 2019-11-28 | 19:00 | OMOTOSHO NIPP | 1,061 | 99.6 | 104.3 | 4,933.2 | Unchecked |
| 2019-12-09 | 20:00 | GEREGU NIPP | 1,218 | 133 | 124 | 5,168.6 | Unchecked |
| 2019-12-13 | 11:00 | GEREGU NIPP | 1,216 | 119 | 127 | 5,108.1 | Unchecked |
| 2019-12-19 | 21:00 | ODUKPANI NIPP | 1,418.5 | 325.9 | 395.8 | 5,515.5 | Unchecked |
| 2019-12-21 | 17:00 | JEBBA | 1,194 | 419 | 422 | 4,277.1 | Unchecked |
| 2020-01-12 | 15:00 | GEREGU | 1,298 | 257 | 0 | 4,387.3 | Unchecked |
| 2020-01-16 | 08:00 | GEREGU | 881 | 160 | 160 | 3,659.2 | Unchecked |
| 2020-01-19 | 21:00 | ODUKPANI NIPP | 1,328.6 | 298.9 | 336.4 | 4,738.7 | Unchecked |
| 2020-03-01 | 09:00 | GEREGU | 1,331 | 348 | 293 | 4,497.2 | Unchecked |
| 2020-03-17 | 21:00 | SHIRORO | 1,627 | 0 | 430 | 5,652.5 | Unchecked |
| 2020-04-03 | 21:00 | AFAM VI | 1,383 | 398 | 365 | 3,305.8 | Unchecked |
| 2020-04-10 | 23:00 | TRANS-AMADI | 247.2 | 85.2 | 77.9 | 3,420.1 | Unchecked |
| 2020-04-12 | 22:00 | ODUKPANI NIPP | 1,317.1 | 392.2 | 431.9 | 4,801.5 | Unchecked |
| 2020-04-19 | 15:00 | GEREGU | 8,193 | 274 | 269 | 11,800.4 | Matched |
| 2021-12-07 | 23:00 | TRANS-AMADI | 293.4 | 94 | 93.6 | 4,468.2 | Unchecked |
| 2022-01-30 | 06:00 | OMOKU | 357.2 | 52.7 | 0 | 4,455.4 | Unchecked |
| 2022-02-05 | 21:00 | TRANS-AMADI | 292.4 | 89.2 | 91.6 | 4,612.5 | Unchecked |
| 2022-08-11 | 14:00 | TRANS-AMADI | 201 | 75.5 | 62.2 | 3,211.8 | Unchecked |
| 2022-12-05 | 01:00 | TRANS-AMADI | 270.7 | — | 81.2 | 4,630.8 | Unchecked |
| 2022-12-28 | 13:00 | DADINKOWA | 187.9 | 34 | 33.9 | 4,477.3 | Unchecked |
| 2023-02-08 | 12:00 | TRANS-AMADI | 211 | 53.8 | 17.1 | 4,590.7 | Unchecked |
| 2023-05-19 | 02:00 | TRANS-AMADI | 239.2 | 42.5 | 43.1 | 4,647.8 | Unchecked |
| 2023-08-05 | 18:00 | DADINKOWA | 177 | 31.9 | 32 | 3,758.7 | Unchecked |
| 2023-08-09 | 06:00 | DADINKOWA | 177.2 | 32.4 | 32.4 | 4,049.1 | Unchecked |
| 2023-08-26 | 05:00 | DADINKOWA | 190 | 19 | 19 | 4,015.7 | Unchecked |
| 2023-09-28 | 19:00 | DADINKOWA | 222.1 | 40.3 | 40.4 | 4,420.4 | Unchecked |
| 2023-12-30 | 07:00 | TRANS-AMADI | 242.1 | 41.8 | 41.9 | 4,783.29 | Unchecked |
| 2024-01-09 | 20:00 | TRANS-AMADI | 203.8 | 35.9 | 38.8 | 4,420.36 | Unchecked |
| 2024-07-03 | 17:00 | DADINKOWA | 138.4 | 28.21 | 28.18 | 2,993.72 | Matched |
| 2026-06-04 | 16:00 | TRANS-AMADI | 225.8 | 25.2 | 20.4 | 4,437.7 | Matched |

</details>

<details>
<summary>Additional 354 readings above 110% and at most twice capacity reference</summary>

| Date | Time | Plant | Plant MW | Previous MW | Next MW | Grid MW | Website check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-11-03 | 17:00 | EGBIN | 1,935 | 600 | 656 | 3,026.8 | Unchecked |
| 2017-11-05 | 20:00 | ALAOJI NIPP | 748 | 76.1 | 76 | 2,890.9 | Unchecked |
| 2017-11-06 | 07:00 | OLORUNSOGO NIPP | 992.9 | 102.2 | 98.3 | 2,074.1 | Unchecked |
| 2017-11-14 | 03:00 | OLORUNSOGO | 477.1 | 203.3 | 205.7 | 1,727.1 | Unchecked |
| 2017-11-21 | 08:00 | AFAM VI | 724.4 | 0 | 0 | 1,923.1 | Unchecked |
| 2017-11-23 | 04:00 | ODUKPANI NIPP | 1,022.4 | 229.5 | 233.8 | 1,995.3 | Unchecked |
| 2017-11-28 | 16:00 | IHOVBOR NIPP | 806 | 80 | 80.8 | 2,541.9 | Unchecked |
| 2017-12-02 | 19:00 | OLORUNSOGO NIPP | 1,107.1 | 105.3 | 107.1 | 2,979.4 | Unchecked |
| 2017-12-17 | 11:00 | EGBIN | 2,061 | 564 | 588 | 3,133.1 | Unchecked |
| 2017-12-19 | 17:00 | OLORUNSOGO NIPP | 1,096.9 | 102.9 | 105.5 | 2,417.3 | Unchecked |
| 2018-01-09 | 23:00 | OLORUNSOGO | 522.6 | 0 | 0 | 1,839 | Unchecked |
| 2018-01-16 | 15:00 | OMOTOSHO | 422.8 | 134.5 | 0 | 2,078.1 | Unchecked |
| 2018-01-24 | 20:00 | IHOVBOR NIPP | 882 | 91.4 | 97.3 | 3,065.8 | Unchecked |
| 2018-01-31 | 04:00 | JEBBA | 914 | 278 | 334 | 2,225.6 | Unchecked |
| 2018-02-21 | 19:00 | PARAS ENERGY | 152 | 70.2 | 71 | 1,661.7 | Unchecked |
| 2018-02-23 | 20:00 | EGBIN | 2,088 | 495 | 518 | 3,820 | Unchecked |
| 2018-02-24 | 23:00 | PARAS ENERGY | 151 | 0 | 0 | 1,667.7 | Unchecked |
| 2018-03-06 | 02:00 | PARAS ENERGY | 151 | 70.2 | 70.2 | 1,246.4 | Unchecked |
| 2018-03-08 | 14:00 | OMOTOSHO | 418.4 | 133.1 | 132 | 1,501.8 | Unchecked |
| 2018-03-08 | 23:00 | OMOTOSHO | 437.7 | 138.3 | 0 | 1,964.7 | Unchecked |
| 2018-03-20 | 02:00 | ODUKPANI NIPP | 938.1 | 0 | 296 | 2,037.3 | Unchecked |
| 2018-03-21 | 17:00 | ODUKPANI NIPP | 1,046.8 | 327.8 | 307.3 | 2,971.3 | Unchecked |
| 2018-05-01 | 05:00 | PARAS ENERGY | 147.6 | 67.8 | 67.8 | 1,323.5 | Unchecked |
| 2018-05-05 | 20:00 | OLORUNSOGO NIPP | 854 | 85.1 | 85.8 | 1,868.9 | Unchecked |
| 2018-05-25 | 23:00 | EGBIN | 1,536 | 581 | 0 | 2,571 | Unchecked |
| 2018-05-30 | 23:00 | EGBIN | 1,619 | 619 | 0 | 3,286.9 | Unchecked |
| 2018-06-05 | 23:00 | IHOVBOR NIPP | 910.6 | 0 | 0 | 2,688.2 | Unchecked |
| 2018-06-08 | 04:00 | IHOVBOR NIPP | 979 | 85.2 | 95 | 2,028.9 | Unchecked |
| 2018-06-20 | 10:00 | IHOVBOR NIPP | 908 | 88.7 | 0 | 2,186.7 | Unchecked |
| 2018-07-02 | 14:00 | JEBBA | 808 | 170 | 170 | 1,527.3 | Unchecked |
| 2018-07-19 | 18:00 | EGBIN | 1,569 | 556 | 557 | 2,416.5 | Unchecked |
| 2018-07-30 | 09:00 | OLORUNSOGO | 394.2 | 120.9 | 121.7 | 908.1 | Unchecked |
| 2018-08-01 | 23:00 | OLORUNSOGO | 458.4 | 157.4 | 0 | 1,266.5 | Unchecked |
| 2018-08-20 | 12:00 | OLORUNSOGO NIPP | 1,211.8 | 0 | 169.9 | 2,569.3 | Unchecked |
| 2018-08-21 | 15:00 | SHIRORO | 684 | 0 | 0 | 2,282.8 | Unchecked |
| 2018-08-25 | 02:00 | JEBBA | 910 | 328 | 281 | 1,464.4 | Unchecked |
| 2018-09-07 | 19:00 | AZURA-EDO IPP | 698 | 256 | 418 | 2,379.8 | Unchecked |
| 2018-09-12 | 13:00 | OLORUNSOGO NIPP | 1,047.6 | 107.1 | 104.4 | 2,863.3 | Unchecked |
| 2018-09-13 | 10:00 | PARAS ENERGY | 145.1 | 66.9 | 66.9 | 2,013.9 | Unchecked |
| 2018-09-14 | 13:00 | OMOTOSHO NIPP | 952 | 101.6 | 99.6 | 3,463.5 | Unchecked |
| 2018-09-14 | 17:00 | SHIRORO | 744 | 444 | 445 | 2,833.4 | Unchecked |
| 2018-09-23 | 09:00 | KAINJI | 1,023 | 0 | 330 | 2,977 | Unchecked |
| 2018-09-23 | 19:00 | SHIRORO | 802 | 439 | 431 | 2,623.6 | Unchecked |
| 2018-09-26 | 07:00 | OLORUNSOGO | 458 | 0 | 0 | 2,695.3 | Unchecked |
| 2018-09-27 | 02:00 | IHOVBOR NIPP | 791 | 0 | 71.3 | 2,376.7 | Unchecked |
| 2018-10-03 | 05:00 | ALAOJI NIPP | 808 | 81 | 80.6 | 3,153.4 | Unchecked |
| 2018-10-05 | 13:00 | JEBBA | 1,151 | 402 | 429 | 3,463.6 | Unchecked |
| 2018-10-13 | 04:00 | KAINJI | 881 | 297 | 307 | 1,792.5 | Unchecked |
| 2018-10-15 | 17:00 | JEBBA | 1,138 | 395 | 403 | 3,250.1 | Unchecked |
| 2018-11-19 | 01:00 | AFAM VI | 1,224 | — | 0 | 3,362 | Unchecked |
| 2018-11-22 | 18:00 | EGBIN | 1,530 | 542 | 529 | 3,107.1 | Unchecked |
| 2018-12-02 | 18:00 | GEREGU | 690 | 322 | 364 | 3,271.7 | Unchecked |
| 2018-12-07 | 04:00 | IHOVBOR NIPP | 913 | 0 | 98.3 | 1,369.1 | Unchecked |
| 2018-12-25 | 19:00 | OMOTOSHO | 393.6 | 121.5 | 130.9 | 3,759.2 | Unchecked |
| 2018-12-28 | 01:00 | KAINJI | 1,417 | — | 0 | 2,975.7 | Unchecked |
| 2018-12-31 | 22:00 | KAINJI | 1,188 | 0 | 388 | 2,898.6 | Unchecked |
| 2019-01-02 | 04:00 | GEREGU | 540 | 0 | 270 | 1,826.4 | Unchecked |
| 2019-01-20 | 11:00 | JEBBA | 1,135 | 449 | 395 | 2,699.4 | Unchecked |
| 2019-01-26 | 05:00 | JEBBA | 1,060 | 0 | 367 | 2,949.1 | Unchecked |
| 2019-01-27 | 07:00 | OMOTOSHO | 418.2 | 129.1 | 128.6 | 3,181.6 | Unchecked |
| 2019-02-14 | 11:00 | GEREGU | 684 | 0 | 385 | 3,220.6 | Unchecked |
| 2019-02-25 | 15:00 | ODUKPANI NIPP | 972.3 | 190.7 | 186.3 | 3,967.2 | Unchecked |
| 2019-03-02 | 05:00 | IHOVBOR NIPP | 893 | 92 | 93.8 | 3,049.2 | Unchecked |
| 2019-03-02 | 14:00 | KAINJI | 976 | 409 | 402 | 3,092.7 | Unchecked |
| 2019-03-03 | 04:00 | IHOVBOR NIPP | 981 | 96.1 | 98.7 | 2,691.4 | Unchecked |
| 2019-03-04 | 20:00 | ODUKPANI NIPP | 1,204.8 | 214.8 | 216.9 | 4,394.9 | Unchecked |
| 2019-03-07 | 13:00 | PARAS ENERGY | 139.4 | 59.9 | 62.3 | 3,673.4 | Unchecked |
| 2019-03-16 | 12:00 | ODUKPANI NIPP | 1,205.1 | 298.4 | 290.9 | 4,325.5 | Unchecked |
| 2019-03-19 | 05:00 | ODUKPANI NIPP | 1,199.8 | 296.8 | 301.6 | 3,900.5 | Unchecked |
| 2019-03-19 | 19:00 | ODUKPANI NIPP | 1,141.9 | 291.8 | 299.8 | 3,615.4 | Unchecked |
| 2019-03-22 | 04:00 | JEBBA | 867 | 125 | 167 | 2,957.35 | Unchecked |
| 2019-03-23 | 01:00 | SHIRORO | 950 | — | 0 | 4,308 | Unchecked |
| 2019-03-27 | 05:00 | IHOVBOR NIPP | 948 | 93.2 | 92.6 | 3,607 | Unchecked |
| 2019-04-16 | 14:00 | ODUKPANI NIPP | 1,136.6 | 279.8 | 270.9 | 2,582.5 | Unchecked |
| 2019-04-20 | 21:00 | TRANS-AMADI | 177.8 | 246.5 | 0 | 2,835 | Unchecked |
| 2019-04-22 | 07:00 | KAINJI | 1,186 | 255 | 261 | 3,721.1 | Unchecked |
| 2019-04-26 | 11:00 | ODUKPANI NIPP | 1,136.5 | 397.3 | 349.7 | 3,141.6 | Unchecked |
| 2019-04-27 | 03:00 | OLORUNSOGO | 622.3 | 299.8 | 286.7 | 1,802.2 | Unchecked |
| 2019-04-29 | 20:00 | ODUKPANI NIPP | 1,191.9 | 310.3 | 302.9 | 3,505.2 | Unchecked |
| 2019-04-30 | 19:00 | EGBIN | 1,493 | 486 | 514 | 3,688.1 | Unchecked |
| 2019-05-16 | 21:00 | ODUKPANI NIPP | 1,000.1 | 192.4 | 172.4 | 4,330.2 | Unchecked |
| 2019-05-21 | 14:00 | JEBBA | 924 | 241 | 204 | 2,962 | Unchecked |
| 2019-05-29 | 13:00 | IHOVBOR NIPP | 933 | 100.3 | 90.8 | 3,441.5 | Unchecked |
| 2019-05-30 | 02:00 | OLORUNSOGO | 454.5 | 177.6 | 0 | 3,252.6 | Unchecked |
| 2019-05-30 | 06:00 | OMOTOSHO | 501.7 | 177.4 | 152 | 4,446.1 | Unchecked |
| 2019-06-04 | 13:00 | ODUKPANI NIPP | 1,201.3 | 194.7 | 288.9 | 5,042.9 | Unchecked |
| 2019-06-06 | 09:00 | IHOVBOR NIPP | 927 | 97.1 | 108.6 | 3,237.9 | Unchecked |
| 2019-06-06 | 23:00 | KAINJI | 865.89 | 245 | 0 | 2,952.29 | Unchecked |
| 2019-06-09 | 18:00 | JEBBA | 1,049 | 257 | 268 | 4,145.4 | Unchecked |
| 2019-06-09 | 23:00 | OMOTOSHO | 513.4 | 206.1 | 0 | 3,740.3 | Unchecked |
| 2019-06-11 | 11:00 | OLORUNSOGO | 463.1 | 194.4 | 217.9 | 3,669.4 | Unchecked |
| 2019-06-12 | 14:00 | PARAS ENERGY | 131 | 64.1 | 58.5 | 3,847.8 | Unchecked |
| 2019-06-14 | 06:00 | SAPELE NIPP | 871 | 78.3 | 76.8 | 3,646.3 | Unchecked |
| 2019-06-26 | 16:00 | ODUKPANI NIPP | 1,203.5 | 188.2 | 202.7 | 4,054.6 | Unchecked |
| 2019-06-27 | 04:00 | JEBBA | 870 | 159 | 163 | 3,348.2 | Unchecked |
| 2019-07-02 | 16:00 | ODUKPANI NIPP | 1,019.1 | 212 | 198.5 | 3,630.9 | Unchecked |
| 2019-07-06 | 12:00 | OLORUNSOGO | 514.1 | 184.1 | 202.5 | 3,362.8 | Unchecked |
| 2019-07-07 | 23:00 | PARAS ENERGY | 214.5 | 65.1 | 0 | 3,376.1 | Unchecked |
| 2019-07-18 | 03:00 | ODUKPANI NIPP | 1,056.5 | 276.3 | 189.9 | 2,716.6 | Unchecked |
| 2019-07-19 | 01:00 | JEBBA | 977 | — | 177 | 4,141.6 | Unchecked |
| 2019-07-24 | 17:00 | OMOTOSHO | 452.3 | 132.5 | 133.3 | 3,795.2 | Unchecked |
| 2019-07-27 | 19:00 | SAPELE NIPP | 894 | 0 | 84.6 | 4,677.9 | Unchecked |
| 2019-07-30 | 04:00 | OLORUNSOGO | 405.7 | 0 | 0 | 2,503.5 | Unchecked |
| 2019-08-04 | 21:00 | ODUKPANI NIPP | 1,139.7 | 289.1 | 288.1 | 3,983.5 | Unchecked |
| 2019-08-06 | 21:00 | ODUKPANI NIPP | 1,202.3 | 304.2 | 286.9 | 3,866.4 | Unchecked |
| 2019-08-08 | 23:00 | AFAM VI | 1,239 | 255 | 0 | 4,440.4 | Unchecked |
| 2019-08-17 | 05:00 | OLORUNSOGO | 379.9 | 171.7 | 166.1 | 2,740.3 | Unchecked |
| 2019-08-20 | 01:00 | PARAS ENERGY | 133.7 | — | 60.9 | 3,432.1 | Unchecked |
| 2019-09-01 | 18:00 | PARAS ENERGY | 122.8 | 46.3 | 50.5 | 2,345.7 | Unchecked |
| 2019-09-02 | 08:00 | OMOTOSHO NIPP | 755.7 | 0 | 76.3 | 2,688.6 | Unchecked |
| 2019-09-02 | 10:00 | PARAS ENERGY | 123.5 | 50.1 | 57.6 | 2,210.4 | Unchecked |
| 2019-09-07 | 11:00 | OLORUNSOGO | 374.4 | 114.7 | 113.8 | 2,843.8 | Unchecked |
| 2019-09-12 | 18:00 | PARAS ENERGY | 124.5 | 51.7 | 55.3 | 3,504.2 | Unchecked |
| 2019-09-15 | 18:00 | OLORUNSOGO | 449.9 | 0 | 131 | 2,741.4 | Unchecked |
| 2019-09-18 | 10:00 | ODUKPANI NIPP | 1,017.1 | 194.7 | 187.6 | 3,601.4 | Unchecked |
| 2019-09-22 | 21:00 | OLORUNSOGO | 378.3 | 65.3 | 68.6 | 2,915.9 | Unchecked |
| 2019-09-30 | 08:00 | ALAOJI NIPP | 714.5 | 71.9 | 72.5 | 2,978.2 | Unchecked |
| 2019-10-01 | 01:00 | ODUKPANI NIPP | 979.6 | — | 172.6 | 3,339.4 | Unchecked |
| 2019-10-01 | 12:00 | IHOVBOR NIPP | 863 | 87.1 | 85.7 | 3,221.6 | Unchecked |
| 2019-10-09 | 19:00 | ODUKPANI NIPP | 1,104 | 203.6 | 253.7 | 4,556.2 | Unchecked |
| 2019-10-14 | 12:00 | ODUKPANI NIPP | 1,030.9 | 185 | 192.9 | 4,288.8 | Unchecked |
| 2019-10-15 | 04:00 | ODUKPANI NIPP | 920 | 109.6 | 189.6 | 2,633.1 | Unchecked |
| 2019-10-27 | 22:00 | KAINJI | 1,053 | 302 | 0 | 3,483.3 | Unchecked |
| 2019-11-05 | 09:00 | OLORUNSOGO | 370.5 | 97.7 | 95.8 | 3,271.2 | Unchecked |
| 2019-11-14 | 20:00 | PARAS ENERGY | 121.9 | 52.6 | 51.9 | 4,017.4 | Unchecked |
| 2019-11-16 | 24:00 | OMOKU | 265.5 | 0 | — | 1,668.5 | Unchecked |
| 2019-11-17 | 02:00 | TRANS-AMADI | 148.4 | 59.9 | 38.4 | 2,959.5 | Unchecked |
| 2019-11-18 | 23:00 | EGBIN | 2,406 | 593 | 539 | 5,599 | Matched |
| 2019-11-21 | 23:00 | ODUKPANI NIPP | 1,078.3 | 356.2 | 0 | 3,572 | Unchecked |
| 2019-11-23 | 04:00 | OLORUNSOGO | 459.2 | 187.3 | 189.6 | 3,526.2 | Unchecked |
| 2019-11-24 | 02:00 | OLORUNSOGO | 388.4 | 165.2 | 158.2 | 3,619.48 | Unchecked |
| 2019-11-26 | 13:00 | OLORUNSOGO | 429.2 | 161.1 | 157.7 | 4,614.9 | Unchecked |
| 2019-12-07 | 19:00 | OMOKU | 181.3 | 79.22 | 60.4 | 3,906.6 | Unchecked |
| 2019-12-09 | 08:00 | EGBIN | 1,794 | 571 | 561 | 4,400.9 | Unchecked |
| 2019-12-14 | 17:00 | OLORUNSOGO | 465.2 | 167.3 | 0 | 3,858.6 | Unchecked |
| 2019-12-24 | 17:00 | EGBIN | 1,556 | 558 | 561 | 3,785.7 | Unchecked |
| 2019-12-31 | 18:00 | DELTA | 1,028 | 0 | 299 | 3,655.2 | Unchecked |
| 2020-01-02 | 14:00 | OLORUNSOGO | 400.2 | 128.2 | 124.8 | 3,102.4 | Unchecked |
| 2020-01-12 | 02:00 | OMOKU | 271.3 | 99.1 | 101.8 | 3,292.8 | Unchecked |
| 2020-01-14 | 20:00 | OLORUNSOGO | 397.7 | 160.6 | 155.7 | 3,955.9 | Unchecked |
| 2020-01-17 | 18:00 | JEBBA | 1,096 | 402 | 395 | 2,796.2 | Unchecked |
| 2020-01-18 | 05:00 | ODUKPANI NIPP | 1,027.1 | 273.7 | 317.5 | 3,756.7 | Unchecked |
| 2020-01-18 | 14:00 | ODUKPANI NIPP | 1,204.3 | 273.8 | 295.5 | 3,940 | Unchecked |
| 2020-01-21 | 07:00 | DELTA | 1,199 | 276 | 256 | 4,340.5 | Unchecked |
| 2020-01-21 | 17:00 | GEREGU | 560 | 318 | 0 | 3,569.2 | Unchecked |
| 2020-01-23 | 21:00 | PARAS ENERGY | 177.1 | 83.5 | 87.5 | 3,730.8 | Unchecked |
| 2020-02-07 | 15:00 | ODUKPANI NIPP | 1,244.6 | 273.1 | 285.8 | 4,519 | Unchecked |
| 2020-02-15 | 23:00 | EGBIN | 2,498 | 690 | 687 | 4,866.8 | Unchecked |
| 2020-02-16 | 11:00 | KAINJI | 1,222 | 217 | 386 | 4,234.8 | Unchecked |
| 2020-02-22 | 04:00 | ODUKPANI NIPP | 1,100.9 | 277.9 | 252.7 | 3,674.2 | Unchecked |
| 2020-02-22 | 12:00 | ODUKPANI NIPP | 1,087.3 | 285.8 | 261.8 | 4,673.4 | Unchecked |
| 2020-02-23 | 09:00 | JEBBA | 1,137 | 328 | 324 | 4,211 | Unchecked |
| 2020-02-27 | 12:00 | OMOTOSHO | 384 | 337.1 | 133.4 | 4,441.2 | Unchecked |
| 2020-03-02 | 20:00 | ODUKPANI NIPP | 1,207.6 | 304.6 | 327 | 3,775.8 | Unchecked |
| 2020-03-13 | 03:00 | JEBBA | 1,058 | 259 | 262 | 4,127.6 | Unchecked |
| 2020-03-14 | 14:00 | ODUKPANI NIPP | 1,108.4 | 281.7 | 290.3 | 3,777.2 | Unchecked |
| 2020-04-04 | 15:00 | ODUKPANI NIPP | 1,114.4 | 211.3 | 287.2 | 4,181.7 | Unchecked |
| 2020-04-04 | 19:00 | ODUKPANI NIPP | 1,205.8 | 307.5 | 306.5 | 4,525.2 | Unchecked |
| 2020-04-07 | 11:00 | EGBIN | 1,504 | 453 | 507 | 4,512.6 | Unchecked |
| 2020-04-08 | 06:00 | ALAOJI NIPP | 818 | 82.1 | 81.8 | 3,703.9 | Unchecked |
| 2020-04-09 | 08:00 | OLORUNSOGO | 480.6 | 0 | 165.3 | 4,141.6 | Unchecked |
| 2020-04-12 | 16:00 | OMOKU | 228.2 | 96.6 | 86.3 | 4,022.9 | Unchecked |
| 2020-04-20 | 08:00 | TRANS-AMADI | 152.8 | 52.1 | 59.1 | 3,955.1 | Unchecked |
| 2020-04-21 | 15:00 | ODUKPANI NIPP | 1,075.2 | 333.1 | 323.7 | 4,695.8 | Unchecked |
| 2020-04-24 | 22:00 | OLORUNSOGO | 385 | 99.1 | 101.2 | 3,815.4 | Unchecked |
| 2020-04-28 | 04:00 | ODUKPANI NIPP | 1,105.7 | 256.1 | 274 | 3,390 | Unchecked |
| 2020-04-28 | 17:00 | OLORUNSOGO | 409.2 | 127.6 | 138.2 | 3,675.5 | Unchecked |
| 2020-05-02 | 21:00 | OLORUNSOGO | 430.3 | 157.3 | 155.1 | 4,184.1 | Unchecked |
| 2020-05-06 | 10:00 | OLORUNSOGO | 431.3 | 159 | 158.7 | 4,447.8 | Unchecked |
| 2020-05-07 | 22:00 | IHOVBOR NIPP | 761 | 73.5 | 108.5 | 5,153.4 | Unchecked |
| 2020-05-08 | 06:00 | ODUKPANI NIPP | 1,103.5 | 265.6 | 283.9 | 3,843.5 | Unchecked |
| 2020-06-08 | 15:00 | GEREGU | 544 | 270 | 0 | 3,969.8 | Unchecked |
| 2020-06-20 | 05:00 | OMOKU | 167.8 | 55.8 | 0 | 2,574.7 | Unchecked |
| 2020-07-06 | 14:00 | AZURA-EDO IPP | 822 | 424 | 396 | 3,944.2 | Unchecked |
| 2020-07-15 | 08:00 | TRANS-AMADI | 163.4 | 51.6 | 50.9 | 3,056.3 | Unchecked |
| 2020-08-26 | 08:00 | AZURA-EDO IPP | 771 | 375 | 375 | 3,575.8 | Unchecked |
| 2020-09-06 | 01:00 | AZURA-EDO IPP | 759 | — | 375 | 2,715.5 | Unchecked |
| 2020-10-04 | 19:00 | OMOKU | 187.7 | 41.4 | 45.6 | 4,194 | Unchecked |
| 2020-10-21 | 03:00 | TRANS-AMADI | 195.1 | 53.2 | 55.7 | 3,252.9 | Unchecked |
| 2020-10-31 | 07:00 | GEREGU | 514 | 275 | 256 | 3,430.1 | Unchecked |
| 2020-11-21 | 04:00 | GEREGU | 692 | 339 | 353 | 4,447 | Unchecked |
| 2020-11-24 | 14:00 | AZURA-EDO IPP | 865 | 399 | 416 | 5,043.3 | Unchecked |
| 2020-11-27 | 10:00 | AZURA-EDO IPP | 802 | 405 | 423 | 4,544.6 | Unchecked |
| 2021-02-06 | 18:00 | TRANS-AMADI | 143.2 | 42.4 | 41.5 | 3,731.7 | Unchecked |
| 2021-03-02 | 09:00 | TRANS-AMADI | 172 | 52.1 | 52.2 | 3,567.1 | Unchecked |
| 2021-04-04 | 10:00 | GEREGU | 790 | 380 | 0 | 4,001 | Unchecked |
| 2021-04-19 | 18:00 | GEREGU | 540 | 270 | 271 | 3,894.5 | Unchecked |
| 2021-04-19 | 22:00 | GEREGU | 544 | 274 | 276 | 4,056.8 | Unchecked |
| 2021-05-15 | 08:00 | TRANS-AMADI | 122.8 | 31.2 | 31.1 | 3,343 | Unchecked |
| 2021-06-03 | 10:00 | OMOKU | 219.7 | 40.7 | 38.3 | 3,598.4 | Unchecked |
| 2021-06-09 | 04:00 | GEREGU | 566 | 283 | 282 | 3,521.3 | Unchecked |
| 2021-06-25 | 01:00 | GEREGU | 836 | — | 411 | 3,614.1 | Unchecked |
| 2021-07-10 | 03:00 | TRANS-AMADI | 153.7 | 33.4 | 38.8 | 2,672.3 | Unchecked |
| 2021-08-23 | 23:00 | OMOKU | 245.1 | 61.5 | 0 | 3,574.2 | Unchecked |
| 2021-10-08 | 04:00 | TRANS-AMADI | 132.7 | 40.9 | 41.3 | 3,369.9 | Unchecked |
| 2021-11-01 | 14:00 | OMOKU | 181.5 | 48.7 | 48.5 | 3,794 | Unchecked |
| 2021-11-04 | 05:00 | TRANS-AMADI | 166.9 | 51.1 | 71.2 | 4,093.1 | Unchecked |
| 2022-01-04 | 04:00 | TRANS-AMADI | 155.8 | 92 | 88 | 3,613.3 | Unchecked |
| 2022-01-05 | 23:00 | OMOKU | 195.7 | 53.2 | 52.5 | 3,821.5 | Unchecked |
| 2022-01-14 | 10:00 | OMOKU | 219.1 | 55.2 | 0.5 | 4,053 | Unchecked |
| 2022-01-15 | 04:00 | GEREGU | 754 | 370 | 394 | 4,124.1 | Unchecked |
| 2022-01-29 | 03:00 | OMOKU | 171 | 36.5 | 52.5 | 3,458.4 | Unchecked |
| 2022-02-27 | 04:00 | OMOKU | 299.4 | 42.4 | 45.6 | 4,345.7 | Unchecked |
| 2022-02-27 | 16:00 | PARAS ENERGY | 138.8 | 72.2 | 73 | 3,866.4 | Unchecked |
| 2022-03-01 | 06:00 | OMOKU | 179.4 | 43.5 | 44.1 | 4,248.7 | Unchecked |
| 2022-03-05 | 19:00 | OMOKU | 220.6 | 36.6 | 35.3 | 4,073.1 | Unchecked |
| 2022-03-06 | 05:00 | PARAS ENERGY | 133.1 | 63.8 | 64.7 | 3,556.2 | Unchecked |
| 2022-04-03 | 09:00 | GEREGU | 802 | 390 | 390 | 4,066.7 | Unchecked |
| 2022-04-04 | 12:00 | GEREGU | 527 | 411 | 396 | 4,013.1 | Unchecked |
| 2022-04-07 | 03:00 | OMOKU | 176.9 | 46.9 | 47.7 | 4,180.1 | Unchecked |
| 2022-04-17 | 15:00 | GEREGU | 530 | 257 | 262 | 3,796.8 | Unchecked |
| 2022-04-18 | 23:00 | GEREGU | 798 | 386 | 398 | 4,071.8 | Unchecked |
| 2022-05-20 | 13:00 | AZURA-EDO IPP | 834 | 389 | 419 | 3,675.4 | Unchecked |
| 2022-07-04 | 16:00 | OMOKU | 206.1 | 51.5 | 50.7 | 3,291.57 | Unchecked |
| 2022-07-05 | 17:00 | OMOKU | 204.9 | 49.9 | 49.9 | 3,473.82 | Unchecked |
| 2022-07-07 | 17:00 | OMOKU | 194.3 | 0 | 47.3 | 3,758.9 | Unchecked |
| 2022-08-20 | 24:00 | OKPAI | 588 | 293 | — | 3,432.6 | Unchecked |
| 2022-08-21 | 21:00 | OKPAI | 576 | 287 | 290 | 4,500.4 | Unchecked |
| 2022-08-26 | 05:00 | OMOKU | 212.6 | 51.8 | 52.4 | 4,029.4 | Unchecked |
| 2022-08-29 | 15:00 | OMOKU | 193.6 | 49.3 | 47.4 | 4,064.1 | Unchecked |
| 2022-09-06 | 01:00 | OMOKU | 204.1 | — | 37.3 | 3,732.9 | Unchecked |
| 2022-10-21 | 01:00 | OKPAI | 726 | — | 363 | 4,063.2 | Unchecked |
| 2022-10-22 | 12:00 | OKPAI | 788 | 392 | 770 | 3,853.6 | Unchecked |
| 2022-10-22 | 13:00 | OKPAI | 770 | 788 | 368 | 3,819.2 | Unchecked |
| 2022-10-24 | 08:00 | TRANS-AMADI | 134.6 | 45.4 | 42.8 | 3,908.4 | Unchecked |
| 2022-11-12 | 16:00 | PARAS ENERGY | 186.8 | 58.8 | 59.6 | 4,538.9 | Unchecked |
| 2022-11-15 | 16:00 | IBOM POWER | 218.6 | 108 | 106.6 | 4,629.72 | Unchecked |
| 2022-12-12 | 16:00 | AZURA-EDO IPP | 816 | 420 | 419 | 4,705.2 | Unchecked |
| 2022-12-17 | 18:00 | AZURA-EDO IPP | 854 | 424 | 420 | 5,024.3 | Unchecked |
| 2022-12-19 | 04:00 | IBOM POWER | 215.8 | 107.7 | 108 | 4,332.4 | Unchecked |
| 2023-01-04 | 16:00 | OMOKU | 169.2 | 42.4 | 42.3 | 4,279.2 | Unchecked |
| 2023-01-07 | 23:00 | PARAS ENERGY | 141.9 | 65.6 | 67.2 | 3,293.7 | Unchecked |
| 2023-01-09 | 04:00 | PARAS ENERGY | 145 | 60.4 | 66 | 3,886.6 | Unchecked |
| 2023-01-09 | 06:00 | PARAS ENERGY | 139.1 | 66 | 68.4 | 4,050.3 | Unchecked |
| 2023-01-18 | 13:00 | PARAS ENERGY | 142.4 | 68.4 | 67.6 | 3,727.3 | Unchecked |
| 2023-01-23 | 01:00 | AZURA-EDO IPP | 858 | — | 375 | 4,311.1 | Unchecked |
| 2023-01-25 | 03:00 | PARAS ENERGY | 140.4 | 67.6 | 66.8 | 3,940.2 | Unchecked |
| 2023-03-02 | 23:00 | GEREGU | 538 | 260 | 266 | 3,046.9 | Unchecked |
| 2023-03-13 | 12:00 | OMOKU | 193.6 | 51.6 | 50.1 | 4,274.57 | Unchecked |
| 2023-03-30 | 14:00 | AZURA-EDO IPP | 820 | 377 | 379 | 4,157 | Unchecked |
| 2023-04-01 | 11:00 | PARAS ENERGY | 138.1 | 66.8 | 67.6 | 4,619.8 | Unchecked |
| 2023-04-02 | 04:00 | PARAS ENERGY | 139.9 | 66.8 | 67.6 | 4,791.9 | Unchecked |
| 2023-04-03 | 19:00 | PARAS ENERGY | 138.1 | 66 | 67.6 | 4,557 | Unchecked |
| 2023-04-07 | 01:00 | PARAS ENERGY | 133.7 | — | 64.8 | 3,845.7 | Unchecked |
| 2023-04-22 | 11:00 | PARAS ENERGY | 130.5 | 66.7 | 66.4 | 3,925.9 | Unchecked |
| 2023-05-03 | 09:00 | PARAS ENERGY | 200.4 | 64.8 | 65.7 | 4,217.4 | Unchecked |
| 2023-05-05 | 10:00 | PARAS ENERGY | 137.1 | 64.8 | 65.7 | 4,344.8 | Unchecked |
| 2023-05-26 | 06:00 | OMOKU | 222.3 | 40.4 | 40.2 | 4,974.9 | Unchecked |
| 2023-05-26 | 09:00 | AZURA-EDO IPP | 573 | 268 | 262 | 4,598.7 | Unchecked |
| 2023-05-28 | 13:00 | AZURA-EDO IPP | 547 | 279 | 280 | 4,367.3 | Unchecked |
| 2023-06-02 | 12:00 | AZURA-EDO IPP | 536 | 254 | 250 | 3,902.1 | Unchecked |
| 2023-06-30 | 03:00 | OKPAI | 536 | 277 | 261 | 4,056.7 | Unchecked |
| 2023-07-16 | 15:00 | IBOM POWER | 360.2 | 30.3 | 30.3 | 4,456.5 | Unchecked |
| 2023-07-27 | 02:00 | OMOKU | 275.1 | 75 | 86.9 | 4,059.8 | Unchecked |
| 2023-10-04 | 11:00 | OKPAI | 562 | 486 | 286 | 4,799.2 | Unchecked |
| 2023-10-05 | 12:00 | TRANS-AMADI | 120.4 | 21.5 | 21.6 | 4,388.7 | Unchecked |
| 2023-10-15 | 05:00 | JEBBA | 730 | 429 | 471 | 4,499.6 | Unchecked |
| 2023-10-23 | 19:00 | AZURA-EDO IPP | 738 | 369 | 758 | 4,831.4 | Unchecked |
| 2023-10-23 | 20:00 | AZURA-EDO IPP | 758 | 738 | 724 | 4,835.8 | Unchecked |
| 2023-10-23 | 21:00 | AZURA-EDO IPP | 724 | 758 | 373 | 4,777.2 | Unchecked |
| 2023-11-05 | 01:00 | OMOKU | 185.5 | — | 57.2 | 4,344.2 | Unchecked |
| 2023-11-05 | 23:00 | OMOKU | 255.7 | 76.1 | 0 | 4,792.04 | Unchecked |
| 2023-11-07 | 22:00 | PARAS ENERGY | 141.6 | 71.4 | 71.4 | 4,624.34 | Unchecked |
| 2023-11-09 | 03:00 | OMOKU | 193.9 | 67.3 | 66.3 | 4,689.9 | Unchecked |
| 2023-11-19 | 16:00 | AZURA-EDO IPP | 786 | 420 | 393 | 5,022.04 | Unchecked |
| 2023-12-03 | 24:00 | AFAM VI | 752 | 376 | — | 4,819.56 | Unchecked |
| 2023-12-04 | 12:00 | PARAS ENERGY | 150.5 | 78.5 | 78.5 | 4,366.2 | Unchecked |
| 2023-12-08 | 11:00 | PARAS ENERGY | 135 | 69.5 | 69.5 | 3,497.94 | Unchecked |
| 2023-12-12 | 09:00 | JEBBA | 738 | 0 | 331 | 4,105.68 | Unchecked |
| 2023-12-17 | 12:00 | PARAS ENERGY | 127.3 | 68.5 | 70.5 | 4,342.12 | Unchecked |
| 2023-12-20 | 21:00 | PARAS ENERGY | 138.1 | 71 | 70.5 | 3,861.5 | Unchecked |
| 2023-12-26 | 15:00 | OMOKU | 218.7 | 70.7 | 71.1 | 4,283.62 | Unchecked |
| 2023-12-29 | 21:00 | PARAS ENERGY | 132.5 | 70.4 | 70.4 | 4,398.38 | Unchecked |
| 2023-12-30 | 07:00 | PARAS ENERGY | 152.5 | 81.5 | 75.5 | 4,783.29 | Unchecked |
| 2024-01-04 | 07:00 | OMOKU | 239.4 | 74.7 | 73.2 | 4,358.66 | Unchecked |
| 2024-01-18 | 16:00 | PARAS ENERGY | 167.3 | 85.3 | 85.3 | 3,741.88 | Unchecked |
| 2024-01-21 | 01:00 | OMOKU | 239.4 | — | 56.5 | 3,828.97 | Unchecked |
| 2024-01-21 | 12:00 | OMOKU | 191.1 | 53.4 | 54.3 | 3,908.38 | Unchecked |
| 2024-01-24 | 24:00 | AFAM VI | 748 | 375 | — | 4,138.57 | Unchecked |
| 2024-02-01 | 03:00 | PARAS ENERGY | 149.5 | 80.3 | 149.5 | 4,142.38 | Unchecked |
| 2024-02-01 | 04:00 | PARAS ENERGY | 149.5 | 149.5 | 81.3 | 4,184.55 | Unchecked |
| 2024-02-05 | 11:00 | PARAS ENERGY | 150.4 | 80.3 | 81.1 | 3,325.8 | Unchecked |
| 2024-02-18 | 03:00 | GEREGU | 522 | 261 | 259 | 4,017.24 | Unchecked |
| 2024-02-22 | 09:00 | PARAS ENERGY | 134.2 | 71.3 | 73.3 | 2,986.2 | Unchecked |
| 2024-02-28 | 18:00 | OMOKU | 173 | 67.7 | 71.5 | 3,372.28 | Unchecked |
| 2024-03-02 | 20:00 | OMOKU | 172.6 | 71.5 | 73.5 | 4,236.05 | Unchecked |
| 2024-03-06 | 22:00 | PARAS ENERGY | 158.9 | 82.3 | 84.3 | 3,719.74 | Unchecked |
| 2024-03-27 | 11:00 | OKPAI | 564 | 302 | 336 | 4,424 | Unchecked |
| 2024-04-06 | 19:00 | OMOKU | 252.6 | 70.6 | 72.3 | 3,501.85 | Unchecked |
| 2024-04-07 | 12:00 | OKPAI | 636 | 319 | 304 | 4,071.54 | Unchecked |
| 2024-04-17 | 11:00 | TRANS-AMADI | 144.8 | 48.1 | 49.2 | 3,562.11 | Unchecked |
| 2024-05-03 | 01:00 | AZURA-EDO IPP | 544 | — | 375 | 4,109.54 | Unchecked |
| 2024-05-06 | 07:00 | PARAS ENERGY | 153.7 | 84.2 | 86.4 | 2,488.68 | Unchecked |
| 2024-05-09 | 11:00 | PARAS ENERGY | 155.5 | 86.8 | 84.2 | 3,728.2 | Unchecked |
| 2024-05-10 | 01:00 | PARAS ENERGY | 153.9 | — | 154.4 | 3,853.56 | Unchecked |
| 2024-05-10 | 02:00 | PARAS ENERGY | 154.4 | 153.9 | 84.6 | 3,865.3 | Unchecked |
| 2024-06-01 | 23:00 | TRANS-AMADI | 141.8 | 42.1 | 42.5 | 3,600.78 | Unchecked |
| 2024-06-06 | 05:00 | PARAS ENERGY | 169.5 | 94.1 | 91.9 | 3,319.58 | Unchecked |
| 2024-06-06 | 22:00 | OMOKU | 235.4 | 34.8 | 0 | 3,780.24 | Unchecked |
| 2024-06-13 | 22:00 | AZURA-EDO IPP | 581 | 425 | 387 | 3,724.06 | Unchecked |
| 2024-06-23 | 01:00 | OMOKU | 224 | — | 58.1 | 4,209.61 | Unchecked |
| 2024-07-16 | 05:00 | PARAS ENERGY | 143.7 | 62.9 | 64.5 | 2,957.93 | Unchecked |
| 2024-08-02 | 21:00 | PARAS ENERGY | 130.1 | 64.9 | 64.1 | 4,236.88 | Unchecked |
| 2024-08-13 | 21:00 | PARAS ENERGY | 189.9 | 108.3 | 108.3 | 4,183.71 | Unchecked |
| 2024-08-15 | 05:00 | OMOKU | 238.1 | 75.5 | 77.3 | 3,785.95 | Unchecked |
| 2024-08-21 | 17:00 | DADINKOWA | 49.86 | 39.84 | 39.99 | 2,954.69 | Unchecked |
| 2024-08-25 | 11:00 | OMOKU | 197.1 | 78 | 60.1 | 3,553.78 | Unchecked |
| 2024-08-25 | 19:00 | PARAS ENERGY | 178 | 104.7 | 107.4 | 4,044.57 | Unchecked |
| 2024-08-26 | 19:00 | PARAS ENERGY | 187.1 | 103.5 | 109.9 | 4,176.8 | Unchecked |
| 2024-08-31 | 21:00 | PARAS ENERGY | 178.4 | 106.5 | 106.6 | 4,303.64 | Unchecked |
| 2024-09-03 | 17:00 | PARAS ENERGY | 177.1 | 108.9 | 108.2 | 4,414.27 | Unchecked |
| 2024-09-03 | 23:00 | PARAS ENERGY | 181.9 | 107.9 | 109.5 | 4,251.08 | Unchecked |
| 2024-09-09 | 13:00 | OMOKU | 226 | 56.2 | 56.3 | 4,148.75 | Unchecked |
| 2024-09-19 | 08:00 | OKPAI | 686 | 345 | 363 | 4,165.17 | Unchecked |
| 2024-09-19 | 12:00 | OKPAI | 714 | 344 | 380 | 4,453.38 | Unchecked |
| 2024-09-25 | 13:00 | PARAS ENERGY | 191.8 | 109.3 | 110.4 | 3,437.41 | Unchecked |
| 2024-11-29 | 19:00 | PARAS ENERGY | 192.4 | 109.1 | 109.9 | 4,598.2 | Unchecked |
| 2024-12-02 | 18:00 | PARAS ENERGY | 191.5 | 107.5 | 107 | 4,492.44 | Unchecked |
| 2024-12-24 | 15:00 | PARAS ENERGY | 181.9 | 106 | 103.7 | 3,745.11 | Unchecked |
| 2025-01-06 | 12:00 | IBOM POWER | 303 | 30.1 | 30 | 4,649.6 | Matched |
| 2025-01-10 | 18:00 | PARAS ENERGY | 148.7 | 107.8 | 107.7 | 4,202.59 | Unchecked |
| 2025-01-11 | 22:00 | PARAS ENERGY | 190.6 | 108.6 | 110.1 | 3,365.58 | Unchecked |
| 2025-01-18 | 01:00 | PARAS ENERGY | 175.1 | — | 99.5 | 4,613.59 | Unchecked |
| 2025-01-22 | 10:00 | OMOKU | 180 | 50.1 | 49.7 | 4,156.34 | Unchecked |
| 2025-01-28 | 03:00 | OMOKU | 199.1 | 50.4 | 0 | 4,626.18 | Unchecked |
| 2025-03-01 | 13:00 | OMOKU | 200 | 35.8 | 18.6 | 4,759.58 | Unchecked |
| 2025-03-02 | 20:00 | PARAS ENERGY | 196.5 | 110.1 | 111.3 | 5,241.19 | Unchecked |
| 2025-03-15 | 01:00 | OMOKU | 186.3 | — | 36.4 | 5,079.48 | Unchecked |
| 2025-04-01 | 10:00 | AZURA-EDO IPP | 762 | 408 | 396 | 4,837.48 | Unchecked |
| 2025-04-27 | 19:00 | IBOM POWER | 357 | 14.3 | 35.7 | 4,222.31 | Unchecked |
| 2025-05-11 | 06:00 | OMOKU | 202.2 | 36.6 | 36.7 | 4,975.9 | Unchecked |
| 2025-06-13 | 10:00 | PARAS ENERGY | 190.5 | 110.2 | 108.9 | 4,253.89 | Unchecked |
| 2025-06-30 | 07:00 | PARAS ENERGY | 192.7 | 110.2 | 109.5 | 3,951.4 | Unchecked |
| 2025-07-05 | 05:00 | OMOKU | 195 | 53.5 | 54.2 | 3,394.4 | Unchecked |
| 2025-07-24 | 12:00 | PARAS ENERGY | 180.5 | 101.5 | 101 | 3,962.19 | Unchecked |
| 2025-07-25 | 07:00 | OMOKU | 187 | 19.1 | 18.8 | 4,088.41 | Unchecked |
| 2025-08-01 | 24:00 | OKPAI | 538 | 274 | — | 3,833.18 | Unchecked |
| 2025-08-15 | 24:00 | PARAS ENERGY | 192.4 | 110.1 | — | 4,016.11 | Unchecked |
| 2025-11-09 | 05:00 | OMOKU | 203.3 | 37 | 37.5 | 4,514.87 | Unchecked |
| 2025-11-16 | 05:00 | GEREGU | 502 | 232 | 239 | 4,827.3 | Unchecked |
| 2026-01-02 | 13:00 | PARAS ENERGY | 185.1 | 108.6 | 104.2 | 4,840.97 | Unchecked |
| 2026-01-11 | 18:00 | PARAS ENERGY | 190.8 | 110.2 | 109.9 | 4,328.1 | Unchecked |
| 2026-01-18 | 05:00 | PARAS ENERGY | 195.2 | 110 | 110.7 | 4,561.49 | Unchecked |
| 2026-02-16 | 02:00 | OMOKU | 197.8 | 36.4 | 36.9 | 3,912.14 | Unchecked |
| 2026-03-26 | 21:00 | PARAS ENERGY | 179.2 | 109.6 | 110.2 | 4,174.09 | Unchecked |
| 2026-04-17 | 02:00 | PARAS ENERGY | 190.9 | 105.3 | 105.4 | 3,900.98 | Unchecked |
| 2026-04-25 | 24:00 | OMOKU | 197.8 | 52.2 | — | 3,375.28 | Unchecked |
| 2026-05-15 | 02:00 | PARAS ENERGY | 166.7 | 81.9 | 81.3 | 4,317.31 | Unchecked |
| 2026-05-15 | 24:00 | AZURA-EDO IPP | 868 | 408 | — | 4,674.76 | Unchecked |
| 2026-06-01 | 05:00 | PARAS ENERGY | 166.4 | 80.5 | 77.7 | 4,046.4 | Unchecked |
| 2026-06-13 | 13:00 | TRANS-AMADI | 125.3 | 26.6 | 20.5 | 3,718.15 | Unchecked |
| 2026-08-23 | 04:00 | TRANS-AMADI | 144 | 25.4 | 25 | 3,531.45 | Unchecked |
| 2026-09-25 | 08:00 | DADINKOWA | 49.88 | 40.86 | 40.82 | 3,982.95 | Unchecked |
| 2026-10-15 | 01:00 | PARAS ENERGY | 170.7 | — | 84.7 | 4,038.2 | Unchecked |

</details>

<details>
<summary>Additional 126 statistical candidates outside the capacity screen</summary>

| Date | Time | Plant | Plant MW | Previous MW | Next MW | Grid MW | Positive day median MW | Website check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-11-15 | 01:00 | EGBIN | 560 | — | 0 | 1,618.3 | 48 | Unchecked |
| 2017-11-15 | 04:00 | EGBIN | 550 | 0 | 570 | 1,267.1 | 48 | Unchecked |
| 2017-11-15 | 05:00 | EGBIN | 570 | 550 | 387 | 1,513 | 48 | Unchecked |
| 2017-11-15 | 06:00 | EGBIN | 387 | 570 | 383 | 1,751.6 | 48 | Unchecked |
| 2017-11-15 | 07:00 | EGBIN | 383 | 387 | 345 | 1,701.1 | 48 | Unchecked |
| 2017-11-15 | 08:00 | EGBIN | 345 | 383 | 239 | 1,808.9 | 48 | Unchecked |
| 2018-05-01 | 06:00 | GEREGU | 357 | 0 | 0 | 1,592.1 | 69.5 | Unchecked |
| 2018-10-01 | 20:00 | AZURA-EDO IPP | 377 | 278 | 375 | 3,043.5 | 75 | Unchecked |
| 2019-03-22 | 22:00 | AZURA-EDO IPP | 437 | 355 | 440 | 4,311.3 | 75 | Unchecked |
| 2019-03-22 | 23:00 | AZURA-EDO IPP | 440 | 437 | 0 | 3,588.3 | 75 | Unchecked |
| 2019-07-14 | 20:00 | AFAM VI | 284.2 | 206.5 | 281.4 | 3,731.8 | 45.4 | Unchecked |
| 2019-07-14 | 21:00 | AFAM VI | 281.4 | 284.2 | 264.4 | 3,103.2 | 45.4 | Unchecked |
| 2019-07-14 | 22:00 | AFAM VI | 264.4 | 281.4 | 0 | 3,457.4 | 45.4 | Unchecked |
| 2019-08-30 | 21:00 | AZURA-EDO IPP | 417 | 212 | 375 | 1,636.9 | 75 | Unchecked |
| 2019-08-30 | 23:00 | AZURA-EDO IPP | 385 | 375 | 0 | 2,285.9 | 75 | Unchecked |
| 2019-09-22 | 10:00 | OLORUNSOGO | 322 | 32.1 | 31.8 | 2,240.9 | 35 | Unchecked |
| 2020-02-04 | 16:00 | TRANS AFAM POWER | 551 | 100 | 100 | 4,215.1 | 100 | Unchecked |
| 2020-04-29 | 01:00 | TRANS-AMADI | 51.9 | — | 0.6 | 2,187.5 | 10.1 | Unchecked |
| 2020-06-11 | 18:00 | SAPELE | 51.6 | 9.2 | 63.7 | 2,308.7 | 9.5 | Unchecked |
| 2020-06-11 | 19:00 | SAPELE | 63.7 | 51.6 | 65.8 | 2,579.5 | 9.5 | Unchecked |
| 2020-06-11 | 20:00 | SAPELE | 65.8 | 63.7 | 0 | 3,222.1 | 9.5 | Unchecked |
| 2020-07-05 | 20:00 | TRANS-AMADI | 72.3 | 0 | 0 | 3,080.5 | 9.8 | Unchecked |
| 2020-07-05 | 23:00 | TRANS-AMADI | 94.2 | 0 | 49.5 | 2,082 | 9.8 | Unchecked |
| 2020-07-05 | 24:00 | TRANS-AMADI | 49.5 | 94.2 | — | 504.7 | 9.8 | Unchecked |
| 2020-10-21 | 19:00 | SAPELE | 58.9 | 3.9 | 58.3 | 4,215.5 | 4.5 | Unchecked |
| 2020-10-21 | 20:00 | SAPELE | 58.3 | 58.9 | 56.3 | 4,453 | 4.5 | Unchecked |
| 2020-10-21 | 21:00 | SAPELE | 56.3 | 58.3 | 56.4 | 4,428.9 | 4.5 | Unchecked |
| 2020-10-21 | 22:00 | SAPELE | 56.4 | 56.3 | 56.3 | 3,651.2 | 4.5 | Unchecked |
| 2020-10-21 | 23:00 | SAPELE | 56.3 | 56.4 | 0 | 2,228 | 4.5 | Unchecked |
| 2020-10-24 | 01:00 | SAPELE | 41.5 | — | 75 | 3,154.5 | 4.7 | Unchecked |
| 2020-10-24 | 02:00 | SAPELE | 75 | 41.5 | 40.6 | 3,430.8 | 4.7 | Unchecked |
| 2020-10-24 | 03:00 | SAPELE | 40.6 | 75 | 41.5 | 3,075.5 | 4.7 | Unchecked |
| 2020-10-24 | 04:00 | SAPELE | 41.5 | 40.6 | 41.2 | 2,998.8 | 4.7 | Unchecked |
| 2020-10-24 | 05:00 | SAPELE | 41.2 | 41.5 | 41.1 | 2,959.9 | 4.7 | Unchecked |
| 2020-10-24 | 06:00 | SAPELE | 41.1 | 41.2 | 41.4 | 3,245.4 | 4.7 | Unchecked |
| 2020-10-24 | 07:00 | SAPELE | 41.4 | 41.1 | 40.6 | 2,597.7 | 4.7 | Unchecked |
| 2020-10-24 | 08:00 | SAPELE | 40.6 | 41.4 | 41.5 | 3,466.8 | 4.7 | Unchecked |
| 2020-10-24 | 09:00 | SAPELE | 41.5 | 40.6 | 41.6 | 3,492.7 | 4.7 | Unchecked |
| 2020-10-24 | 10:00 | SAPELE | 41.6 | 41.5 | 41.6 | 3,788.1 | 4.7 | Unchecked |
| 2020-10-24 | 11:00 | SAPELE | 41.6 | 41.6 | 4.6 | 3,895.4 | 4.7 | Unchecked |
| 2022-09-04 | 15:00 | SAPELE | 355 | 35 | 35 | 3,745.2 | 35 | Unchecked |
| 2023-06-17 | 01:00 | DELTA | 341 | — | 68 | 4,119.4 | 68 | Unchecked |
| 2023-09-14 | 14:00 | AFAM VI | 190 | 1.8 | 120 | 1,498.4 | 1.8 | Unchecked |
| 2023-09-14 | 15:00 | AFAM VI | 120 | 190 | 0 | 1,894.1 | 1.8 | Unchecked |
| 2023-09-14 | 20:00 | AFAM VI | 130 | 0 | 160 | 3,366.2 | 1.8 | Unchecked |
| 2023-09-14 | 21:00 | AFAM VI | 160 | 130 | 0 | 3,605.3 | 1.8 | Unchecked |
| 2023-09-14 | 23:00 | AFAM VI | 160 | 0 | 160 | 3,523.7 | 1.8 | Unchecked |
| 2023-09-14 | 24:00 | AFAM VI | 160 | 160 | — | 3,149.4 | 1.8 | Unchecked |
| 2024-06-03 | 01:00 | SHIRORO | 112.5 | — | 0 | 2,805.59 | 3.09 | Unchecked |
| 2024-06-04 | 21:00 | SHIRORO | 160.69 | 0 | 163.9 | 1,484.59 | 3.03 | Unchecked |
| 2024-06-04 | 22:00 | SHIRORO | 163.9 | 160.69 | 0 | 1,777.2 | 3.03 | Unchecked |
| 2024-11-10 | 15:00 | AFAM III FAST POWER | 85.1 | 15 | 15 | 3,014.92 | 15 | Unchecked |
| 2024-11-11 | 11:00 | AFAM III FAST POWER | 85 | 15 | 15 | 3,543.15 | 15 | Unchecked |
| 2024-11-27 | 09:00 | TRANS-AMADI | 16 | 1.3 | 2.1 | 3,868.15 | 2.95 | Unchecked |
| 2025-05-26 | 20:00 | TRANS-AMADI | 4.3 | 0.2 | 4.1 | 4,831.65 | 0.2 | Unchecked |
| 2025-05-26 | 21:00 | TRANS-AMADI | 4.1 | 4.3 | 4.7 | 4,919.99 | 0.2 | Unchecked |
| 2025-05-26 | 22:00 | TRANS-AMADI | 4.7 | 4.1 | 0 | 4,551.8 | 0.2 | Unchecked |
| 2025-05-26 | 24:00 | TRANS-AMADI | 6.1 | 0 | — | 4,157.67 | 0.2 | Unchecked |
| 2025-07-22 | 01:00 | OLORUNSOGO | 187.9 | — | 191.7 | 3,959.57 | 33.75 | Unchecked |
| 2025-07-22 | 02:00 | OLORUNSOGO | 191.7 | 187.9 | 192.1 | 3,346.28 | 33.75 | Unchecked |
| 2025-07-22 | 03:00 | OLORUNSOGO | 192.1 | 191.7 | 196.2 | 3,660.46 | 33.75 | Unchecked |
| 2025-07-22 | 04:00 | OLORUNSOGO | 196.2 | 192.1 | 196.2 | 3,657.25 | 33.75 | Unchecked |
| 2025-07-22 | 05:00 | OLORUNSOGO | 196.2 | 196.2 | 195.6 | 3,814.21 | 33.75 | Unchecked |
| 2025-07-22 | 06:00 | OLORUNSOGO | 195.6 | 196.2 | 187.1 | 3,940.27 | 33.75 | Unchecked |
| 2025-07-22 | 07:00 | OLORUNSOGO | 187.1 | 195.6 | 195.5 | 3,823.85 | 33.75 | Unchecked |
| 2025-07-22 | 08:00 | OLORUNSOGO | 195.5 | 187.1 | 195.3 | 3,831.76 | 33.75 | Unchecked |
| 2025-07-22 | 09:00 | OLORUNSOGO | 195.3 | 195.5 | 194.5 | 3,824.5 | 33.75 | Unchecked |
| 2025-07-22 | 10:00 | OLORUNSOGO | 194.5 | 195.3 | 100.3 | 3,928.43 | 33.75 | Unchecked |
| 2025-08-06 | 15:00 | TRANS-AMADI | 76 | 6.7 | 7.4 | 4,141.49 | 8.85 | Unchecked |
| 2025-09-28 | 12:00 | OMOTOSHO | 199 | 19.8 | 28.7 | 3,956.71 | 20.3 | Unchecked |
| 2026-02-11 | 23:00 | TRANS-AMADI | 21.3 | 20.1 | 22.7 | 4,249.24 | 4.2 | Unchecked |
| 2026-02-11 | 24:00 | TRANS-AMADI | 22.7 | 21.3 | — | 3,942.7 | 4.2 | Unchecked |
| 2026-02-19 | 01:00 | OMOTOSHO | 184.8 | — | 238.9 | 4,339.86 | 33.55 | Unchecked |
| 2026-02-19 | 02:00 | OLORUNSOGO | 221 | 138 | 255.1 | 4,417.53 | 33.5 | Unchecked |
| 2026-02-19 | 02:00 | OMOTOSHO | 238.9 | 184.8 | 273.8 | 4,417.53 | 33.55 | Unchecked |
| 2026-02-19 | 03:00 | OLORUNSOGO | 255.1 | 221 | 253.6 | 4,385.47 | 33.5 | Unchecked |
| 2026-02-19 | 03:00 | OMOTOSHO | 273.8 | 238.9 | 270.7 | 4,385.47 | 33.55 | Unchecked |
| 2026-02-19 | 04:00 | OLORUNSOGO | 253.6 | 255.1 | 248.7 | 4,668.43 | 33.5 | Unchecked |
| 2026-02-19 | 04:00 | OMOTOSHO | 270.7 | 273.8 | 273.1 | 4,668.43 | 33.55 | Unchecked |
| 2026-02-19 | 05:00 | OLORUNSOGO | 248.7 | 253.6 | 251.7 | 4,759.05 | 33.5 | Unchecked |
| 2026-02-19 | 05:00 | OMOTOSHO | 273.1 | 270.7 | 273.2 | 4,759.05 | 33.55 | Unchecked |
| 2026-02-19 | 06:00 | OLORUNSOGO | 251.7 | 248.7 | 258.4 | 4,782.04 | 33.5 | Unchecked |
| 2026-02-19 | 06:00 | OMOTOSHO | 273.2 | 273.1 | 275.7 | 4,782.04 | 33.55 | Unchecked |
| 2026-02-19 | 07:00 | OLORUNSOGO | 258.4 | 251.7 | 0 | 4,350.75 | 33.5 | Unchecked |
| 2026-02-19 | 07:00 | OMOTOSHO | 275.7 | 273.2 | 158 | 4,350.75 | 33.55 | Unchecked |
| 2026-02-19 | 09:00 | OLORUNSOGO | 259.5 | 0 | 135.5 | 4,152.52 | 33.5 | Unchecked |
| 2026-02-27 | 07:00 | TRANS-AMADI | 17.4 | 4.3 | 6.6 | 3,965.18 | 2.7 | Unchecked |
| 2026-04-07 | 16:00 | OMOKU | 4.7 | 0 | 17.8 | 4,099.62 | 0.9 | Unchecked |
| 2026-04-07 | 17:00 | OMOKU | 17.8 | 4.7 | 7.5 | 4,320.01 | 0.9 | Unchecked |
| 2026-04-07 | 18:00 | OMOKU | 7.5 | 17.8 | 0.7 | 4,341.44 | 0.9 | Unchecked |
| 2026-04-07 | 21:00 | OMOKU | 14.6 | 3 | 11.3 | 4,455.8 | 0.9 | Unchecked |
| 2026-04-07 | 22:00 | OMOKU | 11.3 | 14.6 | 0.9 | 4,311.67 | 0.9 | Unchecked |
| 2026-04-07 | 24:00 | OMOKU | 8.2 | 0.9 | — | 3,372.59 | 0.9 | Unchecked |
| 2026-06-01 | 20:00 | TRANS-AMADI | 14.9 | 3.7 | 17.5 | 4,728.6 | 2.3 | Unchecked |
| 2026-06-01 | 21:00 | TRANS-AMADI | 17.5 | 14.9 | 16.6 | 4,658.36 | 2.3 | Unchecked |
| 2026-06-01 | 22:00 | TRANS-AMADI | 16.6 | 17.5 | 17.7 | 4,320.49 | 2.3 | Unchecked |
| 2026-06-01 | 23:00 | TRANS-AMADI | 17.7 | 16.6 | 18.5 | 4,677.24 | 2.3 | Unchecked |
| 2026-06-01 | 24:00 | TRANS-AMADI | 18.5 | 17.7 | — | 4,351.25 | 2.3 | Unchecked |
| 2026-07-04 | 01:00 | OLORUNSOGO | 160.4 | — | 151.1 | 4,510.39 | 30.25 | Unchecked |
| 2026-07-04 | 04:00 | OLORUNSOGO | 156.3 | 148.7 | 160.3 | 4,165.89 | 30.25 | Unchecked |
| 2026-07-04 | 04:00 | TRANS-AMADI | 25.3 | 25.1 | 25.1 | 4,165.89 | 5.05 | Unchecked |
| 2026-07-04 | 05:00 | OLORUNSOGO | 160.3 | 156.3 | 160 | 4,213.31 | 30.25 | Unchecked |
| 2026-07-04 | 06:00 | OLORUNSOGO | 160 | 160.3 | 105.2 | 4,158.6 | 30.25 | Unchecked |
| 2026-09-05 | 01:00 | TRANS-AMADI | 18.8 | — | 19.8 | 4,298.65 | 2 | Unchecked |
| 2026-09-05 | 02:00 | TRANS-AMADI | 19.8 | 18.8 | 1.7 | 3,895.71 | 2 | Unchecked |
| 2026-09-05 | 14:00 | TRANS-AMADI | 10.7 | 2 | 4.2 | 3,226.46 | 2 | Unchecked |
| 2026-09-06 | 16:00 | TRANS-AMADI | 9.48 | 2.3 | 2 | 3,581.11 | 1.8 | Unchecked |
| 2026-10-01 | 21:00 | ZUNGERU | 634 | 601 | 635 | 4,480.57 | 126 | Unchecked |
| 2026-10-01 | 22:00 | ZUNGERU | 635 | 634 | 569 | 4,066.43 | 126 | Unchecked |
| 2026-10-07 | 02:00 | TRANS-AMADI | 16 | 15 | 16.4 | 3,417.49 | 3.1 | Unchecked |
| 2026-10-07 | 03:00 | TRANS-AMADI | 16.4 | 16 | 17 | 3,296.52 | 3.1 | Unchecked |
| 2026-10-07 | 04:00 | TRANS-AMADI | 17 | 16.4 | 16.7 | 3,320.26 | 3.1 | Unchecked |
| 2026-10-07 | 05:00 | TRANS-AMADI | 16.7 | 17 | 16 | 3,574.33 | 3.1 | Unchecked |
| 2026-10-07 | 06:00 | TRANS-AMADI | 16 | 16.7 | 17.5 | 3,726.12 | 3.1 | Unchecked |
| 2026-10-07 | 07:00 | TRANS-AMADI | 17.5 | 16 | 3.86 | 3,437.63 | 3.1 | Unchecked |
| 2026-10-20 | 15:00 | TRANS-AMADI | 15.3 | 11.1 | 2.6 | 4,158.33 | 2.95 | Unchecked |
| 2026-10-24 | 02:00 | TRANS-AMADI | 93.9 | 3.4 | 4.6 | 4,032.93 | 3.5 | Unchecked |
| 2026-10-26 | 19:00 | TRANS-AMADI | 15.5 | 4.1 | 15.9 | 4,329.5 | 2.5 | Unchecked |
| 2026-10-26 | 20:00 | TRANS-AMADI | 15.9 | 15.5 | 16.1 | 4,016.17 | 2.5 | Unchecked |
| 2026-10-26 | 21:00 | TRANS-AMADI | 16.1 | 15.9 | 16.2 | 4,009.84 | 2.5 | Unchecked |
| 2026-10-26 | 22:00 | TRANS-AMADI | 16.2 | 16.1 | 0 | 3,622.16 | 2.5 | Unchecked |
| 2026-10-27 | 08:00 | SAPELE | 211 | 21.4 | 21.5 | 3,659.88 | 21.95 | Unchecked |
| 2026-11-03 | 12:00 | TRANS-AMADI | 18.5 | 2.2 | 5.1 | 3,643.94 | 2 | Unchecked |
| 2026-11-10 | 09:00 | TRANS-AMADI | 15.5 | 2.2 | 14.1 | 3,912.58 | 2.8 | Unchecked |
| 2026-11-10 | 10:00 | TRANS-AMADI | 14.1 | 15.5 | 14.7 | 3,826.89 | 2.8 | Unchecked |
| 2026-11-10 | 11:00 | TRANS-AMADI | 14.7 | 14.1 | 13.8 | 3,935.36 | 2.8 | Unchecked |

</details>

In the candidate tables, “Matched” means the website publishes the same plant and grid readings for that date and hour. It does not validate their accuracy. “Unchecked” means no individual public-page comparison was performed. “—” means the adjacent hour is outside the available day or the value is unavailable. No interpolation or inferred corrections were applied.
