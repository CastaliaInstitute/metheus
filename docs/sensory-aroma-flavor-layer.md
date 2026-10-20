# Epimethean sensory, aroma, and flavor layer

**Status:** working design, version 0.1. This layer records sensory exposures and any independently recorded response. It does not prescribe aromatherapy, infer hormone levels from scent or mood, or promise that a flavor or aroma will “balance,” “boost,” or suppress a hormone.

## Why include it

Smell, taste, oral sensation, food ingestion, memory, expectation, and setting can all be part of a person's lived context. Metheus can help someone notice what they experienced and what was measured afterward, while keeping the exposure separate from the outcome and the interpretation.

The important distinction is between:

- **Olfactory exposure:** smelling an ambient aroma or inhaling a volatile substance.
- **Gustatory exposure:** tasting something, including a mouth rinse that is spat out.
- **Flavor during eating:** taste plus retronasal smell, texture, temperature, oral sensation, and often nutrient ingestion.
- **Ingested product:** food, drink, supplement, or other swallowed product. Its effects cannot be attributed to aroma alone.

An aroma or flavor name is not a chemical analysis. Composition, concentration, route, duration, familiarity, pleasantness, expectation, and the environment can differ substantially across people and products.

## What human evidence can support so far

| Exposure or claim | Human evidence in this draft | How Metheus may state it |
|---|---|---|
| Lavender aroma and cortisol/stress | Small clinical trials have examined lavender inhalation and cortisol or stress markers in specific stressful settings. One trial studied surgical candidates; another studied odors during urodynamic examination. Results are context-bound and do not establish a general hormone-raising or hormone-lowering effect. [Lavender in surgical candidates](https://pubmed.ncbi.nlm.nih.gov/27563324/), [lavender/clary sage during urodynamic testing](https://pubmed.ncbi.nlm.nih.gov/23360656/) | “This study found a change in this setting.” Do not generalize it to all people, settings, oils, or cortisol patterns. |
| Taste and short-term insulin response | Small human experiments report mixed results. One randomized taste-only study found insulin increases after sucrose and saccharin, while another found no significant increase after sweet solutions; a later small study found a very small, short-lived sucrose response. [2008 taste-only study](https://pubmed.ncbi.nlm.nih.gov/18556090/), [1995 study](https://pubmed.ncbi.nlm.nih.gov/7652029/), [2013 study](https://pubmed.ncbi.nlm.nih.gov/24485339/) | “Taste may produce a small, short-lived cephalic insulin response in some experimental conditions; findings are inconsistent.” Do not use taste response to infer a person's insulin or glucose status. |
| Flavored nutrient food and pancreatic polypeptide | Human studies suggest mixed nutrient foods can evoke pancreatic-polypeptide responses, with palatability/flavor affecting response; sweet or salty liquids and gum did not provide the same response in the studied conditions. [Human cephalic-phase PP studies](https://pubmed.ncbi.nlm.nih.gov/19944113/) | Attribute the response to the experimental food and sensory context together, not to a flavor molecule alone. |
| A named scent “stimulates” a named hormone | No universal mapping is established by the evidence above. | Keep as an unverified claim or research hypothesis unless a specific human study supports the exact scent, route, outcome, population, and conditions. |

These papers are examples, not a complete systematic review. Study size, replication, methods, population, and context limit generalization. “Hormone response” is not interchangeable with a meaningful or beneficial health outcome.

## Recording model

A sensory event uses the shared observation record plus optional `sensoryExposure` metadata in [the observation schema](../schema/observation.schema.json). Record, when known and wanted:

- stimulus as the person identifies it, including product/source and named ingredients or chemical composition only if available;
- modality and route: ambient smell, inhalation, taste-only, mouth-rinse/spit, food/drink flavor, or swallowed product;
- exposure interval, concentration or amount and units, and perceived intensity;
- pleasantness/familiarity/expectation if the person wants to report these;
- setting and relevant co-exposures such as food, time of day, sleep, stress, or medication when volunteered;
- responses as separate records: subjective experience, symptom, wearable measure, or laboratory assay with its specimen, assay/device, units, collection time, and protocol.

A response record should not be encoded as part of the exposure. For example, a person may log “lavender diffuser, bedroom, 20 minutes” and separately log a self-rated calmness response or a lab cortisol result. A wearable change in HR or HRV is not a hormone measurement. No response, a missing record, or a change in mood does not prove that a hormone changed.

For analysis, align exposure and response windows only when actual timestamps support that comparison. Preserve baseline, repeated exposures, concurrent food/supplement/medication changes, and missing observations. Label a within-person pattern as a co-occurrence or hypothesis; causal evidence needs a suitable study design and control of alternatives.

## How this layer relates to the system

- **Promethean map:** may offer a reflective prompt about sensory preference, environment, or routine. It cannot select an aroma or flavor as a hormone treatment.
- **Epimethean record:** describes sensory exposure, body/life context, and separately observed responses over time.
- **Behavior layer:** a voluntarily chosen scent routine or food choice may also carry behavior metadata; its presence does not make it safe, effective, or fully controllable.
- **Evidence layer:** each proposed exposure–hormone relationship needs a source, population, route, dose, timing, outcome, evidence status, and limitations. The relation must not be written as a mechanism if it is only a correlation or tradition.

## Safety and privacy boundaries

Metheus records what a person chose to share; it does not recommend ingesting essential oils or applying them to skin. Inhaled products can also irritate or trigger symptoms for some people. Exposure records involving babies and young children should be caregiver-controlled and should not be used to run hormone-manipulation experiments. Pregnancy, asthma, allergy, migraine, and other relevant sensitivities may matter to an individual's decisions; the system should not issue a safety clearance. For product-specific safety or symptoms, defer to qualified clinical guidance and the product's authoritative safety information.

Aroma, food, and intimacy can be personally sensitive. Keep these records optional, minimized, private by default, and under the subject's control. Never infer consent, desire, fertility, pregnancy, or relationship quality from scent choice, eating, or a presumed hormone response.

## Open research work

Before Metheus displays a named aroma/flavor–hormone association, compile and review human evidence for the exact exposure and route; distinguish inhaled odor from oral contact and ingestion; assess study design, sample, replication, effect size, timing, and clinically meaningful outcomes; and retain contrary or null results. Until then, the system can show a user's exposure history and separately measured responses without presenting a hormone-stimulation lookup table.
