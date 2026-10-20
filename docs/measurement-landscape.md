# Metheus measurement landscape

**Status:** working design, version 0.1. This document describes candidate inputs for a future Metheus system. It is not a recommendation to collect every data type, a medical protocol, or a claim that every listed device can measure every listed value.

## Measurement ladder

Metheus should keep six layers distinct:

1. **Sensor signal:** a device's raw or near-raw signal (for example, optical pulse waveform or accelerometer movement).
2. **Direct assay or instrument result:** a value produced by a specified instrument or laboratory method (for example, serum TSH in mIU/L).
3. **Reported experience/event:** what a person or caregiver says happened (for example, felt rested, a feed, bleeding, pain, or intimacy).
4. **Device estimate:** a vendor algorithm's estimate from sensor signals (for example, sleep interval, wrist temperature trend, or HRV summary).
5. **Metheus-derived summary:** a reproducible calculation over named records (for example, median logged sleep midpoint over 14 days).
6. **Interpretation:** a contextual question or hypothesis. It must not be presented as a measurement or diagnosis.

Labels should say which layer a value belongs to. Preserve the original value, unit, source, method, time, and uncertainty; never overwrite an assay result with an interpretation.

## Candidate modalities

| Modality | What can be recorded | What it may support | Important limits |
|---|---|---|---|
| Wearable accelerometer / phone motion | Movement counts or device activity records | Activity timing and broad sleep/wake estimates | Sleep stages and sleep quality are algorithmic estimates, not direct observations of sleep physiology; device wear and vendor methods affect coverage. |
| Optical heart sensor | Heart rate; device-derived HRV | Within-person trends under comparable conditions | HRV depends on device, algorithm, posture, breathing, activity, illness, and timing. It does not identify a hormone, emotion, or diagnosis. |
| Skin-temperature sensor | Local skin temperature and/or deviation from a personal baseline | Overnight trends and possible cycle-related context | Skin temperature is not core body temperature. Room temperature, fit, illness, and device algorithms matter. A trend does not establish ovulation or a hormone level. |
| Validated thermometer | Oral, axillary, tympanic, or basal body temperature, with method | Temperature observations; basal-temperature shifts can support retrospective cycle context | Sites and protocols are not interchangeable. BBT rise is retrospective and affected by sleep, illness, alcohol, timing, and other factors. |
| Pulse oximeter | Estimated oxygen saturation (SpO₂) and pulse | Context for a user or clinician reviewing a reading | It is an estimate with known limitations; circulation, temperature, skin pigmentation and other factors can affect accuracy. Keep symptoms and clinical context alongside it. |
| Cuff blood-pressure monitor | Systolic/diastolic pressure and pulse | Repeated readings collected using the device instructions | Cuff fit, position, rest, timing, and device validation matter; a single reading is not a stable trait. |
| ECG-capable consumer device | A short electrical tracing and any device classification | A captured tracing that may be reviewed in its intended context | Not equivalent to continuous clinical ECG or a general diagnostic conclusion. Store the device's classification separately from a clinician interpretation. |
| Light/environment sensors | Ambient light, temperature, noise when available | Context around sleep, work, or routine changes | Phone and wearable readings are local/device-specific; location, microphone, and continuous environment collection should be opt-in. |
| Food, drink, and feeding logs | User-entered time, type, amount if known; caregiver-observed feed | Timing and reported routine patterns | Logging is incomplete by default. A recorded meal is not a dietary assessment; infant feeds must not be treated as adult meal or fasting windows. |
| Urine home tests | Test-specific qualitative or semiquantitative result, such as LH or hCG; analytes on a urinalysis strip | A narrow, test-specific result under the product's instructions; a qualitative positive/negative result need not have a numeric unit | Collection time, hydration, handling, reading window, and assay instructions matter. Results do not establish a broad endocrine state. Urine tests for hCG check for hCG; urinalysis tests for specified substances. Keep a home test distinct from a laboratory result. |
| Timed urine collection / laboratory urine assay | Named analyte and result, such as 24-hour urinary cortisol | A laboratory result interpreted with collection protocol and clinical question | Collection completeness and timing matter. Cortisol testing may use timed blood, saliva, or a 24-hour urine collection; a result is not a free-standing stress score. |
| Saliva assay | A specified analyte under a lab or kit protocol | Timed sampling where that analyte and method are appropriate | Time, food, oral conditions, medications, kit and laboratory method affect interpretation. Do not infer an assay result from mood or wearable data. |
| Blood / clinical laboratory | Named analyte, value, unit, reference interval, specimen, and lab method when available | Clinical measurements such as CBC, metabolic markers, thyroid or reproductive hormone assays | These are method- and time-specific results. Preserve lab reference intervals and collection context; interpretation belongs in the appropriate clinical context. |
| Growth measurement / clinical record | Weight, length/height, head circumference, with date, method, and reporter | Change over time in a developmental context | Use measured source and method, not visual estimation. A single value or milestone is not a developmental score or prediction. |
| Self-report | Sleep quality, mood, energy, pain, appetite, libido, stress, symptoms, or sense of connection | The person's own experienced context and questions | Subjective reports are valid reports of experience, but they are not direct hormone or neurotransmitter measurements. |

Home urine pregnancy tests detect hCG in urine or blood; urinalysis checks specified substances such as blood, protein, glucose, ketones, and bilirubin. Cortisol testing can use blood, urine, or saliva, and the collection time/protocol matters. Test availability and claims vary, so Metheus should store the actual test and its intended analyte rather than a generic “hormone reading.” [MedlinePlus: pregnancy test](https://medlineplus.gov/lab-tests/pregnancy-test/), [MedlinePlus: urinalysis](https://medlineplus.gov/urinalysis.html), [MedlinePlus: cortisol test](https://medlineplus.gov/lab-tests/cortisol-test/).

## What not to claim

- No wearable HRV, sleep, temperature, or mood series directly measures dopamine, oxytocin, cortisol, estrogen, progesterone, or another hormone.
- Do not present smartwatches or rings as directly measuring glucose without a skin-piercing authorized device; the FDA has warned against noninvasive glucose claims from these devices. [FDA safety communication](https://www.fda.gov/medical-devices/safety-communications/do-not-use-smartwatches-or-smart-rings-measure-blood-glucose-levels-fda-safety-communication).
- SpO₂ is an estimate. FDA notes limitations and accuracy may be affected by factors including circulation, skin pigmentation, skin temperature, and other conditions. [FDA: pulse oximeters](https://www.fda.gov/medical-devices/products-and-medical-procedures/pulse-oximeters).
- A home or direct-to-consumer result should retain the test, claimed use, and instructions; a result is not automatically clinically validated for every inference. [FDA: direct-to-consumer tests](https://www.fda.gov/medical-devices/in-vitro-diagnostics/direct-consumer-tests).
- A time overlap between cycle, intimacy, sleep, mood, feeding, or development is a co-occurrence to explore, not evidence of cause. Do not infer a partner's consent, experience, or physiology from a user's record.

## Practical collection tiers

### Tier 1: low-friction lived rhythms

Optional sleep/wake intervals, activity, light exposure, meal/feeding times, symptoms, and brief self-reports. Include source, coverage, time zone, and whether the entry was measured, estimated, or remembered. This tier can describe a routine without pretending to explain it biologically.

### Tier 2: consumer-device trends

Import heart rate, device HRV, skin-temperature trends, and device sleep/activity estimates where the user wants them. Keep vendor, device, algorithm/version if known, raw-versus-summary status, wear coverage, and original timestamps. Personal baselines require enough coverage and should adapt to life stage and circumstance.

### Tier 3: targeted home tests and clinical records

Allow user-entered or imported named urine, saliva, blood, and clinical results as distinct optional records. Preserve specimen, analyte, exact result and unit, collection time, lab/device, reference range, and test instructions/source where available. Do not recommend testing frequency or make a treatment decision.

### Tier 4: developmental records

Use caregiver reports and measured clinical growth records with explicit reporter and age basis. Keep developmental notes descriptive and sparse. Minimize collection about children, protect access, allow correction/deletion, and plan for the child's increasing assent and control.

## Conditions to capture

When relevant and known, an observation should preserve:

- measured/estimated/reported status and the original provider or reporter;
- analyte or signal name, specimen or sensor location, device/assay, method and version;
- numeric or categorical result with units; assay-specific reference interval where supplied;
- collection/observation time, time zone, interval, and relevant sampling instructions;
- quality flags or context such as wear coverage, fasting status, hydration when reported, posture, illness, or medication context when the user chooses to record it;
- uncertainty, missingness, and links to source records for any derived result.

Do not require sensitive contextual details to save a reading. Avoid collecting exact location, intimate detail, or a child's record unless it materially serves the person's stated purpose and the person has meaningful control.

## Initial product boundary

The current prototype can summarize logged sleep, meal/feeding timing, meal timing relative to waking, calendar gaps between reported bleeding-onset dates, and repeated numeric measurement series. Numeric series are separated by signal, unit, domain, epistemic class, and source/method signature; they report descriptive distribution and coverage only. The contract examples include a qualitative urinary LH home test and a synthetic serum TSH assay. Compatible numeric assay results can be passed to the same descriptive summary operation, but this is not hormone dynamics or clinical interpretation. Device integrations, sample capture, lab imports, clinical interpretations, and child-specific tools are not implemented. The observation schema has optional `measurementDetails` for analyte/signal, specimen or sensor, method/device, collection conditions, quality flags, and assay reference interval. Hormone assay records require an identified analyte, specimen, and assay/test; laboratory numeric results require units while home-test categories may be qualitative. Ordinary events do not need to become medical records. See the [rhythm analysis contract](rhythm-analysis.md#repeated-numeric-measurement-series).
