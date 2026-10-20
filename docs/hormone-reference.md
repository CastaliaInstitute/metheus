# Hormone and endocrine-signal reference

This is a broad working inventory for Metheus, not a claim that every listed molecule is a classical blood-borne hormone or is suitable for personal tracking. The endocrine system is open-ended: many tissues release signals that act locally, at a distance, or both. Names, categories, and evidence levels will need domain review before this becomes a product taxonomy.

The machine-readable [candidate endocrine-relations catalog](../catalog/endocrine-relations.json) represents selected pathway relationships as typed, directed, sourced edges. Version 0.2.2 contains 28 internal-only candidate relations spanning HPT, HPA, HPG, circadian–melatonin, glucose regulation, and gut-incretin signaling. It is an ontology scaffold, not an exhaustive pathway map, evidence synthesis, individual hormone model, or behavior-to-hormone response model; every edge remains under review and is ineligible for readings.

## How to read the inventory

- **Hormone** is used broadly for a chemical messenger released by cells and acting on other cells. Endocrine signals travel through blood; paracrine and autocrine signals act locally; neurohormones are released by neurons into circulation or other tissues.
- **Neurotransmitters are not automatically hormones.** Some molecules have more than one role depending on where and how they are released. Dopamine, serotonin, norepinephrine, and several neuropeptides illustrate this overlap.
- **Hormone level is not directly readable from ordinary wearable data.** Temperature, HRV, sleep, pulse, and behavior can be contextual observations or proxies, not hormone assays.
- **“Happy hormone,” “love hormone,” and similar labels are shorthand, not scientific classifications.** They flatten systems with multiple targets, feedback loops, time scales, and person-to-person variation.
- **A molecule's presence does not explain a person's experience.** Association, mechanism, and causation are different claims; interpretation should state which kind of evidence supports it.

## 1. Hypothalamic and pituitary signaling

### Hypothalamic releasing and inhibiting signals

| Signal | Common name / note |
|---|---|
| TRH | Thyrotropin-releasing hormone; also influences prolactin |
| CRH / CRF | Corticotropin-releasing hormone / factor |
| GnRH | Gonadotropin-releasing hormone; pulsatile control of LH and FSH |
| GHRH | Growth hormone-releasing hormone |
| Somatostatin / GHIH | Growth hormone-inhibiting hormone; also produced in gut and pancreas |
| Dopamine / PIH | Prolactin-inhibiting signal in the hypothalamic-pituitary portal system; also a neurotransmitter and catecholamine precursor |
| Kisspeptin | Key regulator of GnRH neurons; signaling peptide, often grouped with neuroendocrine regulators |
| Neurokinin B | Part of KNDy pulse-generating network with kisspeptin and dynorphin |
| Dynorphin | Endogenous opioid peptide in KNDy and other neural circuits |
| RFRP-3 / GnIH | RFamide-related peptide; inhibitory reproductive-axis signal, with species and context differences |
| Oxytocin | Made in hypothalamus, released by posterior pituitary and within brain; neurohormone and neuromodulator |
| Vasopressin / AVP / ADH | Made in hypothalamus, released by posterior pituitary; water balance and vascular effects |

### Anterior pituitary hormones

| Signal | Common name / note |
|---|---|
| ACTH | Adrenocorticotropic hormone / corticotropin |
| TSH | Thyroid-stimulating hormone / thyrotropin |
| FSH | Follicle-stimulating hormone |
| LH | Luteinizing hormone |
| GH | Growth hormone / somatotropin |
| PRL | Prolactin |
| POMC-derived peptides | POMC is a precursor processed into ACTH, β-lipotropin, β-endorphin, and melanocortins including α-MSH; products vary by tissue |
| MSH peptides | Melanocyte-stimulating hormones, including α-MSH; neuroendocrine peptides involved in pigmentation and energy/appetite pathways |

### Posterior pituitary releases

| Signal | Common name / note |
|---|---|
| Oxytocin | See hypothalamic signals; uterine and milk-ejection effects, plus central roles that should not be reduced to “love” |
| Vasopressin / AVP | See hypothalamic signals; distinct from cortisol and from oxytocin |

## 2. Adrenal and stress-response signals

| Signal | Common name / note |
|---|---|
| Cortisol | Principal human glucocorticoid; time-of-day and pulsatile variation |
| Cortisone | Less active glucocorticoid interconverted with cortisol in tissues |
| Aldosterone | Mineralocorticoid regulating sodium, potassium, and fluid balance |
| DHEA | Dehydroepiandrosterone; adrenal androgen precursor |
| DHEA-S | DHEA sulfate; abundant circulating reservoir/precursor |
| Androstenedione | Adrenal and gonadal androgen precursor |
| Epinephrine / adrenaline | Catecholamine; adrenal-medulla hormone and neurotransmitter |
| Norepinephrine / noradrenaline | Catecholamine; neurotransmitter and circulating adrenal signal |
| Dopamine | Catecholamine; neurotransmitter and hypothalamic pituitary regulator; circulating adrenal contribution also exists |
| Adrenal medullary peptides | Including neuropeptide Y, enkephalins, and chromogranins; co-released signals, with roles depending on tissue/context |

## 3. Thyroid and calcium/phosphate regulation

| Signal | Common name / note |
|---|---|
| T4 | Thyroxine; major thyroid secretion and prohormone reservoir |
| T3 | Triiodothyronine; active thyroid hormone, also formed in peripheral tissues |
| Reverse T3 | Inactive thyroid-hormone metabolite; not usually treated as a regulatory hormone |
| Calcitonin | Thyroid C-cell peptide; participates in calcium regulation |
| PTH | Parathyroid hormone; calcium and phosphate regulation |
| PTHrP | Parathyroid hormone-related protein; developmental and local roles, may circulate in specific states |
| Calcitriol | 1,25-dihydroxyvitamin D; active vitamin D metabolite/hormone |
| FGF23 | Fibroblast growth factor 23; bone-derived phosphate-regulating hormone |
| Klotho | Co-receptor for FGF23 and a soluble signaling protein; classification as hormone is not uniform |

## 4. Reproductive, gonadal, and life-course signals

### Steroids and precursors

| Signal | Common name / note |
|---|---|
| Estradiol (E2) | Major estrogen; produced in gonads and peripheral tissues |
| Estrone (E1) | Estrogen prominent in some life stages and peripheral conversion |
| Estriol (E3) | Estrogen that rises substantially in pregnancy; placental-fetal unit contribution |
| Estetrol (E4) | Fetal-liver-derived estrogen produced during pregnancy |
| Progesterone | Ovarian/corpus-luteum and placental steroid; adrenal precursor contributions also occur |
| Testosterone | Gonadal and adrenal steroid; present across sexes, with wide variation |
| Dihydrotestosterone (DHT) | Potent androgen formed from testosterone in tissues |
| Androstenedione | See adrenal section; gonadal precursor too |
| DHEA / DHEA-S | See adrenal section; precursors for sex steroids |
| 17-hydroxyprogesterone | Steroid precursor used in adrenal and gonadal pathways |
| Sex hormone-binding globulin (SHBG) | Binding protein that affects free/bioavailable sex-steroid fractions; not itself a hormone |

### Gonadal and reproductive peptides

| Signal | Common name / note |
|---|---|
| Inhibin A and B | Gonadal/placental peptides; selectively suppress FSH secretion |
| Activin A, B, and AB | TGF-β-family signals; local and endocrine effects, including reproductive-axis regulation |
| Follistatin | Activin-binding protein; modulates activin availability |
| AMH / MIS | Anti-Müllerian hormone / Müllerian-inhibiting substance; gonadal signal and ovarian-reserve-associated biomarker, not a direct fertility clock |
| Relaxin (especially relaxin-2) | Corpus-luteum/placental peptide; vascular and reproductive effects |
| Leptin | Energy-status signal with permissive roles in reproductive function; see adipose section |
| Kisspeptin | See hypothalamic section; central reproductive regulator |

### Pregnancy, placenta, birth, and lactation

| Signal | Common name / note |
|---|---|
| hCG | Human chorionic gonadotropin; trophoblast/placental signal, supports early pregnancy endocrine function |
| hPL / hCS | Human placental lactogen / chorionic somatomammotropin |
| Placental growth hormone (GH-V) | Placenta-derived growth-hormone variant |
| Placental CRH | Placenta-derived CRH; rises across pregnancy and participates in pregnancy timing networks |
| Placental ACTH and POMC peptides | Placenta and fetal membranes express members of this signaling family |
| Placental progesterone and estrogens | Steroids central to pregnancy physiology |
| Relaxin | Corpus luteum, placenta, and decidua sources depending on pregnancy context |
| Prolactin | Pituitary and decidual sources; lactation-related roles |
| Oxytocin | Neurohypophyseal release; uterine contraction and milk ejection, among other actions |
| Inhibin A / activin / follistatin | Placental and decidual production also occurs |
| PAPP-A | Pregnancy-associated plasma protein A; protease/regulator of IGF availability and prenatal biomarker, not a classic hormone |
| PlGF | Placental growth factor; angiogenic growth factor with clinical biomarker use |
| IGF-I and IGF-II | Insulin-like growth factors; growth factors with endocrine and local actions |

## 5. Pancreatic and glucose-regulation signals

| Signal | Common name / note |
|---|---|
| Insulin | β-cell hormone; glucose and nutrient regulation |
| Glucagon | α-cell hormone; raises circulating glucose through hepatic signaling |
| Somatostatin | δ-cell/islet and gut signal; inhibits several hormone secretions |
| Pancreatic polypeptide (PP) | Islet/F-cell peptide; digestive and energy-balance signaling |
| Amylin / IAPP | β-cell co-secreted peptide with gastric-emptying and satiety effects |
| Ghrelin | Mainly stomach-derived hunger/energy signal; also produced in other tissues |
| GIP | Glucose-dependent insulinotropic polypeptide; incretin from gut K cells |
| GLP-1 | Glucagon-like peptide-1; incretin from gut and preproglucagon neurons |
| Oxyntomodulin | Gut-derived proglucagon peptide |
| GLP-2 | Gut-derived proglucagon peptide; intestinal effects |
| Peptide YY (PYY) | Gut-derived satiety and gastrointestinal signal |
| Glucose | Nutrient and metabolic signal, not a hormone |

## 6. Gastrointestinal and appetite signals

| Signal | Common name / note |
|---|---|
| Gastrin | Stomach/duodenal G-cell hormone |
| CCK | Cholecystokinin; gut and brain peptide involved in digestion and satiety |
| Secretin | Duodenal S-cell hormone |
| Motilin | Gut peptide associated with migrating motor complex |
| Ghrelin | See pancreatic/metabolic section |
| GIP, GLP-1, GLP-2, oxyntomodulin | See pancreatic section; gut-derived incretin/proglucagon family |
| PYY | See pancreatic section |
| Somatostatin | See hypothalamic and pancreatic sections |
| Serotonin / 5-HT | Mostly produced in gut enterochromaffin cells; primarily local/neural signaling, not a simple circulating “happiness hormone” |
| Histamine | ECL-cell/paracrine and immune/neural mediator; local gut signal |
| VIP | Vasoactive intestinal peptide; neurocrine/neuropeptide with local and systemic actions |
| GRP | Gastrin-releasing peptide; neurocrine gut signal |
| Guanylin and uroguanylin | Intestinal peptides regulating epithelial salt and fluid transport |
| Enteroglucagon-related peptides | Proglucagon-derived gut signals including glicentin; classification/action depends on molecule |

## 7. Adipose, energy-balance, and metabolic signals

| Signal | Common name / note |
|---|---|
| Leptin | Adipokine signaling energy stores to brain and other tissues |
| Adiponectin | Adipokine involved in insulin sensitivity and lipid metabolism |
| Resistin | In humans, largely associated with immune cells rather than adipocytes; inflammatory/metabolic signaling |
| Visfatin / NAMPT | Enzyme and extracellular signaling factor; hormone classification is debated |
| Apelin | Peptide ligand for APJ receptor, produced in adipose and other tissues |
| Chemerin | Adipokine/chemokine with metabolic and immune roles |
| Omentin | Adipokine; produced by stromal vascular cells in visceral fat |
| RBP4 | Retinol-binding protein 4; transport protein with adipokine signaling claims |
| FGF21 | Fibroblast growth factor 21; liver/adipose/muscle metabolic hormone |
| FGF19 | Intestinal FGF signal in humans; bile-acid and metabolic regulation |
| FGF15 | Rodent counterpart of human FGF19 |
| ANGPTL3, ANGPTL4, ANGPTL8 | Angiopoietin-like proteins with lipid-metabolism regulation |
| Irisin | Proposed exercise-associated myokine; measurement and physiological claims remain debated |
| Myostatin / GDF8 | Muscle-derived TGF-β-family regulator of muscle growth |
| GDF15 | Stress-responsive cytokine/hormone with appetite and sickness-response effects |
| FGF23 | Bone-derived phosphate hormone (also listed in mineral section) |

## 8. Kidney, cardiovascular, and fluid-balance signals

| Signal | Common name / note |
|---|---|
| Renin | Kidney-derived enzyme initiating renin-angiotensin cascade; not a peptide hormone in the strict sense |
| Angiotensinogen | Liver precursor protein |
| Angiotensin I and II | Peptides in renin-angiotensin system; angiotensin II is vasoactive hormone signal |
| Aldosterone | See adrenal section |
| ANP | Atrial natriuretic peptide |
| BNP | B-type natriuretic peptide; cardiac hormone and clinical biomarker |
| CNP | C-type natriuretic peptide; vascular/endothelial and local signaling |
| Endothelin-1 | Endothelial peptide with potent vascular effects; local and circulating actions |
| Erythropoietin (EPO) | Kidney-derived hormone stimulating red-cell production |
| Thrombopoietin (TPO) | Mainly liver-derived hormone regulating platelet production |
| Vasopressin / AVP | See hypothalamic/posterior pituitary section |
| Urodilatin | Kidney-derived natriuretic peptide in local renal fluid regulation |

## 9. Bone, growth, and tissue-derived signals

| Signal | Common name / note |
|---|---|
| GH | See pituitary section |
| IGF-I and IGF-II | See placental/metabolic sections |
| Osteocalcin | Osteoblast-derived protein; endocrine actions proposed, with ongoing research and species-specific caveats |
| FGF23 | See mineral section |
| Sclerostin | Osteocyte-derived regulator of bone formation; mainly local/endocrine-adjacent signal |
| RANKL | Bone/immune-cell signal regulating osteoclast development; not a classical hormone |
| Osteoprotegerin (OPG) | Decoy receptor regulating RANKL; not a classical hormone |
| PTHrP | See mineral section; important local developmental and tissue signal |
| Calcitonin | See thyroid/mineral section |
| Myostatin / GDF8 | See metabolic section |
| Activin A | See reproductive section; also muscle and tissue signaling |

## 10. Immune, thymic, and inflammatory messengers

These are mostly cytokines or growth factors that can have endocrine effects in some settings; they should not be presented as a tidy set of “mood hormones.”

| Signal family / examples | Common name / note |
|---|---|
| Thymosin α1, thymopoietin, thymulin | Thymic peptides involved in immune development/modulation; categories and human endocrine roles differ |
| IL-1, IL-6, IL-10, IL-17, IL-22 | Interleukins; immune cytokines with local and sometimes systemic effects |
| TNF-α | Tumor necrosis factor alpha; inflammatory cytokine |
| Interferons (IFN-α, IFN-β, IFN-γ) | Antiviral and immune cytokines |
| CSFs (G-CSF, GM-CSF, M-CSF) | Colony-stimulating factors regulating blood-cell lineages |
| TGF-β | Transforming growth factor beta family; immune, growth, and tissue remodeling effects |
| VEGF | Vascular endothelial growth factor; angiogenic growth factor, sometimes released systemically |
| PTHrP, GDF15 | Also appear in tissue/metabolic sections; broad cytokine-like actions |

## 11. Neural messengers and neuropeptides that overlap with endocrine signaling

These are relevant to neurochemistry, but most are not appropriately described as continuously measurable “hormones.”

| Messenger | Classification note |
|---|---|
| Dopamine | Catecholamine neurotransmitter; hypothalamic prolactin-inhibiting hormone and peripheral endocrine roles |
| Serotonin / 5-HT | Monoamine neurotransmitter and gut-derived local signal; circulating serotonin does not report brain serotonin |
| Norepinephrine / noradrenaline | Catecholamine neurotransmitter and adrenal signal |
| Epinephrine / adrenaline | Adrenal catecholamine and neuromodulator |
| GABA | Major inhibitory neurotransmitter; not usually classed as a systemic hormone |
| Glutamate | Major excitatory neurotransmitter |
| Acetylcholine | Neurotransmitter; also autonomic and local signaling |
| Histamine | Neurotransmitter, immune mediator, and gut paracrine signal |
| Endorphins (e.g. β-endorphin) | Endogenous opioid peptides; some are POMC products and can be neurohormonal |
| Enkephalins | Endogenous opioid peptides; neural, adrenal, and gut signaling |
| Dynorphins | Endogenous opioid peptides; neural signaling and KNDy network member |
| Endocannabinoids (anandamide, 2-AG) | Lipid neuromodulators acting locally; not classical endocrine hormones |
| Orexin / hypocretin | Hypothalamic neuropeptides regulating arousal and appetite |
| NPY | Neuropeptide Y; neural and peripheral signaling in appetite, autonomic, and vascular systems |
| AgRP | Agouti-related peptide; hypothalamic appetite neuropeptide |
| α-MSH | POMC-derived melanocortin peptide; neural and endocrine roles |
| CART | Cocaine- and amphetamine-regulated transcript peptide; neuropeptide with metabolic roles |
| Substance P | Tachykinin neuropeptide involved in pain and inflammatory signaling |
| CGRP | Calcitonin gene-related peptide; sensory neuropeptide and vascular signal |
| Neuropeptide S | Neuropeptide affecting arousal and other CNS processes |
| Galanin | Neuropeptide in CNS, pituitary, gut, and peripheral systems |
| PACAP | Pituitary adenylate cyclase-activating polypeptide; neuropeptide and local hormonal signal |
| BDNF | Brain-derived neurotrophic factor; neurotrophin, not a classic hormone |
| Adenosine | Purine neuromodulator and sleep-pressure signal; not a hormone in the usual endocrine sense |

## 12. Other locally acting hormone families

| Signal family / examples | Common name / note |
|---|---|
| Prostaglandins (PGE₂, PGF₂α, PGI₂) | Eicosanoid lipid mediators; mostly local autocrine/paracrine actions |
| Thromboxanes (TXA₂) | Eicosanoid involved in platelet and vascular signaling |
| Leukotrienes | Eicosanoid inflammatory mediators |
| Lipoxins and resolvins | Lipid mediators involved in inflammation resolution |
| Nitric oxide (NO) | Gaseous local messenger; not a classical endocrine hormone |
| Hydrogen sulfide (H₂S) | Gasotransmitter/local signaling molecule |
| Carbon monoxide (CO) | Gasotransmitter at low endogenous levels |
| Retinoic acid | Vitamin A-derived morphogen and nuclear-receptor ligand; developmental and local signaling |
| Bile acids | Metabolites that signal through FXR, TGR5, and related receptors |
| Vitamin D metabolites | See mineral section; steroid-like endocrine system |

## 13. The image's informal labels, translated carefully

| Informal label | Molecule(s) often meant | Better Metheus wording |
|---|---|---|
| “Happy hormone” | Dopamine | Reward, motivation, learning, movement, and pituitary regulation; dopamine is a neurotransmitter and also a hypothalamic endocrine signal |
| “Stress hormone” | Cortisol | One glucocorticoid in the HPA axis; stress physiology also involves catecholamines, CRH, ACTH, autonomic signaling, and context |
| “Love hormone” | Oxytocin | Neurohormone and neuromodulator involved in several reproductive and social processes; effects depend on context and are not a measure of love or trust |
| “Sleep hormone” | Melatonin | Darkness-linked circadian timing signal; sleep depends on interacting circadian, homeostatic, behavioral, and environmental processes |
| “Energy hormone” | Adrenaline | Catecholamine signal in acute arousal; energy regulation involves many systems |
| “Pain-relief hormone” | Endorphins | Endogenous opioid peptides among several pain-modulating systems |
| “Feel-good hormone” | Serotonin | Multifunctional neurotransmitter and gut signal; blood serotonin is not a readout of mood or brain serotonin |
| “Hunger hormone” | Ghrelin | One appetite and energy-balance signal; hunger is regulated by interacting peripheral and brain pathways |
| “Fullness hormone” | Leptin | Longer-term energy-store signal; meal-related fullness also involves CCK, GLP-1, PYY, insulin, vagal signals, and others |
| “Metabolism hormone” | Thyroxine | T4 is a thyroid hormone precursor/reservoir; T3 is the main active thyroid hormone at many targets |
| “Growth hormone” | Somatotropin / GH | Pituitary hormone with pulsatile and sleep-related secretion; effects partly mediated by IGF-I |
| “Bone growth hormone” | Calcitonin | Calcium-regulating thyroid C-cell hormone; bone growth is not controlled by calcitonin alone |
| “Fat-burning hormone” | Glucagon | Pancreatic counter-regulatory hormone; fat metabolism is not a single-hormone process |
| “Blood sugar regulator” | Insulin | One central glucose-regulating hormone; glucagon, incretins, cortisol, catecholamines, GH, and other factors also participate |
| “Water balance hormone” | Vasopressin / ADH | Hypothalamic neurohormone controlling renal water conservation; thirst, kidneys, electrolytes, and other systems also matter |

## 14. Suggested Metheus data categories

Rather than treating the list as one trackable stream, organize it by what a person can actually know:

1. **Direct assay or clinical result:** named analyte, value, unit, sample type, date/time, lab reference interval, cycle/life context if supplied, and source. Do not interpret an isolated value without collection conditions or clinical context.
   **Home-test results are a separate measured source:** retain the named test, analyte, specimen, collection/read time, and the result as qualitative or semiquantitative when that is what the kit provides. A positive/negative urinary LH or hCG result is not a laboratory concentration and does not, by itself, establish ovulation, fertility, or pregnancy outcome.
2. **Clinical event or medication context:** therapy, contraception, pregnancy, lactation, surgery, or clinician-provided interpretation; user-entered and optional.
3. **Physiological observation:** temperature, sleep timing, HRV, resting pulse, bleeding, appetite, pain, energy, or self-described desire. Label sensor versus self-report and uncertainty.
4. **Estimated phase or pattern:** derived from dated observations; state method and confidence. Do not label a phase as hormone-measured unless the relevant analyte was assayed.
5. **Reflective interpretation:** personal meaning and questions. Keep symbolic frameworks distinct from biological measurements and clinical conclusions.

Hormone results may vary with sampling time, pulsatile secretion, menstrual or reproductive stage, age, medications, illness, sleep, food intake, assay method, and binding proteins. A wearable proxy cannot establish a hormone concentration. Metheus should never use these data to diagnose, predict fertility, infer consent or desire, or assign personality.

## 15. What regulates or stimulates hormone release?

Hormones are generally regulated by networks, not isolated “boost” triggers. The same cue can increase one signal and inhibit another; feedback from the target gland, target-organ response, time of day, pulse timing, and life stage all matter. The table gives common physiological controls, not a self-treatment guide.

| Hormone or system | Main upstream regulators / release cues | Feedback or important context |
|---|---|---|
| **TRH → TSH → T4/T3** | Hypothalamic TRH stimulates pituitary TSH; TSH stimulates thyroid synthesis/release. Cold exposure can affect the axis, especially in early life. | T4/T3 feed back to reduce TRH and TSH. Iodine availability is required for thyroid hormone synthesis; it is a substrate, not a “thyroid booster.” |
| **CRH → ACTH → cortisol** | Circadian clock and wake timing regulate CRH/ACTH; physical or psychological stressors can activate the axis. ACTH stimulates adrenal cortisol synthesis. | Cortisol feeds back at pituitary and hypothalamus. Secretion is pulsatile and time-dependent; one reading cannot represent the whole axis. |
| **Sympathetic drive → epinephrine / norepinephrine** | Acute sympathetic activation, including exertion, threat, pain, hypoglycemia, and other demands, stimulates adrenal medulla secretion and nerve release. | These catecholamines also act as neurotransmitters. A pulse or HRV change cannot identify a specific catecholamine level. |
| **Renin → angiotensin II → aldosterone** | Reduced renal perfusion/pressure, reduced sodium chloride delivery to macula densa, and sympathetic β1 input stimulate renin; angiotensin II and elevated potassium stimulate aldosterone. | Sodium, potassium, kidney function, posture, medications, and volume status alter the system. Aldosterone feeds into sodium/potassium and volume regulation. |
| **GnRH → LH/FSH → gonadal steroids** | GnRH pulse pattern regulates LH and FSH. Kisspeptin/KNDy networks and gonadal feedback shape GnRH pulses. Puberty, energy availability, stress, pregnancy, lactation, and life stage alter the axis. | Estradiol, progesterone, testosterone, inhibins, and activins feed back at hypothalamus/pituitary. This is not a simple linear cycle; timing and pulse pattern matter. |
| **Estradiol, progesterone, testosterone, DHT** | Production is stimulated by LH/FSH in gonads, with tissue-specific steroid-enzyme pathways and precursor supply; pregnancy adds placental production. | Levels change with gonadal function, age, cycle/life stage, medications, binding proteins, and conversion in tissues. Peripheral production means “source” is not one gland alone. |
| **Inhibin / activin / follistatin** | Gonadotropin signaling and gonadal/placental cell activity regulate production; activin stimulates FSH synthesis, while inhibin suppresses it; follistatin binds activin. | Effects depend on local tissue concentrations and binding; measured blood levels do not directly represent local signaling. |
| **AMH** | Secreted by ovarian granulosa cells of growing follicles and Sertoli cells in testes; production depends on gonadal cell population and developmental/life stage. | It is not a moment-to-moment cycle trigger and should not be interpreted as a direct countdown to fertility or menopause. |
| **Prolactin** | Suckling and nipple stimulation, pregnancy, sleep, and estrogen can increase release; hypothalamic dopamine tonically inhibits it. | Stress, medications, thyroid status, and sampling conditions can affect levels. A “high prolactin” impression cannot be inferred from mood or behavior. |
| **Oxytocin** | Cervical/uterine stretch and suckling stimulate peripheral release through positive-feedback reflexes; touch and social/sensory contexts can influence central/peripheral oxytocin signaling. | Central and blood oxytocin are not interchangeable measures. Effects vary with context; touch or intimacy does not prove a particular level or emotional state. |
| **Vasopressin / ADH** | Increased plasma osmolality and reduced effective circulating volume stimulate release; nausea and other physiological inputs can also be potent. | Water intake, kidney response, osmolality, medications, and illness matter. This is not the same as “stress hormone.” |
| **GH → IGF-I** | GHRH stimulates and somatostatin inhibits GH; ghrelin can stimulate. GH release is pulsatile and associated with deep sleep; exercise and fasting can affect pulses. GH stimulates hepatic and local IGF-I production. | Age, puberty, nutrition, sleep architecture, sex steroids, and illness shape the axis; a consumer sleep score cannot measure GH. |
| **Melatonin** | Darkness permits pineal melatonin production through the circadian system; light at night suppresses it. | Timing is more central than a generic “amount.” Circadian phase, light exposure, age, and some medicines matter. It signals biological night; it does not itself guarantee sleep. |
| **Insulin** | Rising blood glucose after meals stimulates β-cell secretion; amino acids, incretins (GLP-1/GIP), and vagal input also contribute. | Glucose, meal composition, activity, insulin sensitivity, medications, and counter-regulatory signals interact. |
| **Glucagon** | Low glucose, amino acids, and autonomic inputs stimulate α-cell secretion; insulin and somatostatin inhibit it. | The response differs with meals, fasting, exercise, diabetes, and medication. |
| **Amylin** | Co-secreted with insulin from pancreatic β cells, especially in response to meals/glucose. | Its level tracks β-cell secretion context; it is not a standalone fullness switch. |
| **Ghrelin** | Often rises before meals and during fasting; meal intake suppresses it. Sleep, energy balance, and stomach signals influence release. | Hunger is multi-signal and context-dependent; ghrelin alone does not explain appetite or food choice. |
| **GIP / GLP-1** | Nutrients in the gut after eating stimulate K cells (GIP) and L cells (GLP-1); neural and bile-acid signals contribute. | These incretins enhance glucose-dependent insulin secretion; effects depend on glucose and physiological state. |
| **CCK / secretin / gastrin / motilin** | CCK responds to fats and amino acids in small intestine; secretin to acid entering duodenum; gastrin to peptides, distension, and vagal/GRP input; motilin cycles during fasting between meals. | Gut hormones operate with enteric nerves, local mediators, and meal state; they do not reduce to single food cravings or moods. |
| **PYY / oxyntomodulin / GLP-2** | Nutrients entering distal gut stimulate L-cell release; neural and gut transit signals modulate responses. | Meal size, composition, transit, and individual physiology affect patterns. |
| **Leptin / adiponectin** | Leptin broadly reflects energy stores and is affected by feeding, fasting, and inflammation; adiponectin release relates to adipose tissue function and metabolic context. | These are not immediate “fullness” switches. Levels and responses vary with body composition, sex steroids, inflammation, and metabolic health. |
| **FGF21** | Fasting, ketogenic state, protein restriction, and metabolic stress can stimulate FGF21 in particular tissues; regulation differs by tissue and species. | Human physiological effects and measurement interpretation are still an active area; avoid turning dietary states into a recommendation. |
| **PTH / calcitriol / FGF23** | Low ionized calcium stimulates PTH; PTH stimulates renal calcitriol production. Phosphate and vitamin D status regulate FGF23, largely from bone. | Calcium, phosphate, kidney function, vitamin D, and feedback loops jointly regulate the system. |
| **Calcitonin** | Elevated blood calcium stimulates thyroid C-cell secretion. | Its role in routine adult calcium homeostasis is more limited than popular summaries imply. |
| **EPO** | Reduced oxygen delivery to kidney tissue stimulates erythropoietin production. | Anemia, altitude, kidney function, and oxygenation affect levels; altitude is not a safe or universal “hormone hack.” |
| **ANP / BNP** | Stretch of cardiac chambers with increased filling/volume stimulates natriuretic peptide release. | Kidney function, cardiac structure, age, and volume status affect measured concentrations. |
| **Erythropoietin, TPO, and immune cytokines** | Blood-cell demand, oxygen status, inflammatory signals, and bone marrow feedback regulate these systems. | They are regulated by tissue need and complex immune/bone-marrow networks, not ordinary wellness cues. |
| **Oxytocin, prolactin, reproductive hormones and intimacy** | Sensory and relational events may coincide with changes in neural, autonomic, and endocrine signaling, but effects are highly context-dependent and not reliably inferable from an event log. | Personal notes can support reflection about an individual's experience; they cannot establish hormone levels, causal effects, desire, consent, or another person's state. |

### Everyday cues are context, not hormone controls

- **Light and darkness** are strong timing cues for melatonin and circadian organization; they affect more than one hormone system.
- **Sleep timing and sleep stages** shape several hormonal rhythms, including GH and prolactin; sleep is not a direct assay of either.
- **Meals, fasting, and nutrient composition** influence insulin, glucagon, incretins, ghrelin, and other gut signals.
- **Movement, exertion, and recovery** can alter catecholamines and pulses of GH and other signals; response depends on intensity, timing, fitness, food, sleep, and health.
- **Stressors** can recruit HPA and sympathetic systems, but subjective stress is not a cortisol measurement.
- **Touch, suckling, and reproductive events** can engage oxytocin/prolactin reflexes; emotional meanings cannot be read from those hormones alone.
- **Hydration, salt balance, blood pressure, and kidney function** influence vasopressin and renin-angiotensin-aldosterone regulation.
- **Pregnancy, postpartum life, lactation, puberty, aging, and menopause** reorganize endocrine baselines and feedback loops; they should be represented as context the person provides, not assumed from identity.

Do not frame foods, supplements, sexual activity, exercise, or light exposure as ways to “hack” hormones in a general reading. In people with a medical condition or medication regimen, intentional hormone manipulation belongs with a qualified clinician.

## 16. Developmental stages as Epimethean context

Epimethean time should include development as well as repeating cycles. A developmental stage is context for interpreting observations, not a template that every person follows on schedule. Development reflects interacting biology, relationships, health, environment, opportunity, and individual variation; it cannot be reduced to hormones or a chart.

| Life period | Useful optional context | Metheus framing |
|---|---|---|
| **Pregnancy and prenatal development** | Gestational timing when known, fetal movement as reported, pregnancy context, major transitions, birth circumstances | Context belongs to the pregnant person and family; no claim to infer fetal state, temperament, or future from parental data |
| **Newborn and early infancy (birth–3 months)** | Feeding and settling rhythms, sleep/wake pattern, sensory responses, early gaze and social engagement, caregiver observations, birth or prematurity context | Newborn rhythms are still developing and strongly shaped by feeding, care, light/dark, and individual maturity; do not expect a fixed schedule |
| **Later infancy (about 3–12 months)** | Sleep and feeding changes, movement and exploration, communication, social reciprocity, emerging routines, caregiver/infant co-regulation | Show observations over time and celebrate variation; do not predict ability or attachment from a single behavior or sensor |
| **Toddlerhood and early childhood (about 1–5 years)** | Language, play, movement, regulation, sleep, appetite, relationships, transitions in care and learning | Organize around strengths, supports, and context; avoid personality labels or deterministic forecasts |
| **Middle childhood (about 6–11 years)** | Learning contexts, peer and family relationships, sleep/activity patterns, physical growth, interests and self-described experience | Include the child's voice in age-appropriate ways and preserve privacy as autonomy grows |
| **Adolescence** | Pubertal changes when relevant, sleep timing, identity exploration, relationships, school/social context, increasing autonomy | Puberty timing varies. Do not infer gender identity, sexuality, maturity, or consent from hormone levels, appearance, or age alone |
| **Adulthood and caregiving years** | Work/rest rhythms, relationships, reproductive or non-reproductive transitions, caregiving, health changes, chosen goals | Life stages are not a single prescribed sequence; parenthood and partnership are not assumed |
| **Later life and aging** | Changing sleep, mobility, health, roles, relationships, loss and renewal, personal meaning | Avoid reducing a person to decline or age norms; interpret in their own history and stated priorities |

### Special care with babies

For babies, a useful Metheus record would be caregiver-centered and observational: date/time, who observed, what happened, and what context might matter (feeding, sleep, illness, travel, new environment, or caregiver availability). Signals should be described in ordinary language—“settled after feeding,” “looked toward a voice,” “sleep was more interrupted”—without claiming to know the baby's inner state or hormone levels.

The World Health Organization's nurturing-care framework groups early needs around **good health, adequate nutrition, safety and security, responsive caregiving, and opportunities for early learning**. This is a better organizing frame for baby-centered Epimethean context than a list of “baby hormones.” Responsive interaction and caregiver well-being belong in the picture too: an infant's rhythms unfold in relationship with caregivers and environment. The framework supports holistic context; it is not a diagnostic scoring system.

Milestone references can help caregivers notice development, but they are not diagnostic tests and no single missed or early milestone should be interpreted by Metheus as a diagnosis or forecast. When caregivers have a concern, direct conversation with a pediatrician or developmental professional is the appropriate route. Include prematurity and corrected age when the family or clinician provides them, while avoiding assumptions about a child's future.

Because an infant cannot meaningfully consent to persistent personal tracking, baby profiles should be controlled by a caregiver, collect the minimum needed, avoid public sharing, and include clear deletion and export controls. As the child matures, the design should support growing assent, voice, and privacy rather than treating caregiver access as permanent ownership.

This developmental layer is distinct from endocrine interpretation. Hormones may be part of physiology across prenatal development, infancy, puberty, and aging, but a reading must not use behavior, sleep, temperament, crying, feeding, or attachment observations to infer a specific hormone or neurochemical level.

## Sources and further reading

- [MedlinePlus: Hormones](https://medlineplus.gov/hormones.html) — accessible overview and common clinical hormone tests.
- [MedlinePlus Medical Encyclopedia: Endocrine glands](https://medlineplus.gov/ency/article/002351.htm) — major endocrine organs.
- [NCBI Bookshelf: Glands and Hormones](https://www.ncbi.nlm.nih.gov/books/NBK22231/) — overview of endocrine organs and broader hormone sources.
- [Endotext: Physiology, Endocrine Hormones](https://www.ncbi.nlm.nih.gov/books/NBK538498/) — hypothalamic-pituitary and peripheral hormone physiology.
- [Endotext: Physiology of GnRH and Gonadotrophin Secretion](https://www.ncbi.nlm.nih.gov/books/NBK279070/) — kisspeptin, KNDy signaling, and reproductive-axis regulation.
- [Endotext: Endocrinology of Pregnancy](https://www.ncbi.nlm.nih.gov/books/NBK278962/) — placental, maternal, and reproductive hormones.
- [Endotext: Gastrointestinal Hormonal Control](https://www.ncbi.nlm.nih.gov/books/NBK537284/) — endocrine, paracrine, and neurocrine gut signals.
- [Endotext: Diffuse Hormonal Systems](https://www.ncbi.nlm.nih.gov/books/NBK279025/) — enteroendocrine and pancreatic signaling.
- [Endotext: Adipose Tissue](https://www.ncbi.nlm.nih.gov/books/NBK555602/) — adipokines and limits of hormone classification in adipose tissue.
- [Endotext: Calcium and Phosphate Homeostasis](https://www.ncbi.nlm.nih.gov/books/NBK279023/) — PTH, FGF23, calcitonin, and vitamin D signaling.
- [Endotext: Neuroendocrine Control of Energy Homeostasis](https://www.ncbi.nlm.nih.gov/books/NBK570658/) — peripheral energy-status signals and hypothalamic integration.
- [Circadian Clock Control of Endocrine Factors](https://pmc.ncbi.nlm.nih.gov/articles/PMC4304769/) — daily variation across endocrine systems.
- [Endotext: The Pituitary Gland](https://www.ncbi.nlm.nih.gov/books/NBK27/) — releasing/inhibiting inputs and pituitary secretion patterns.
- [NCBI Bookshelf: Endocrine System: Hormones and Regulation](https://www.ncbi.nlm.nih.gov/books/NBK613062/) — overview of hypothalamic-pituitary and peripheral regulation.
- [WHO: Nurturing care for early childhood development](https://www.who.int/publications/i/item/9789241514064/) — health, nutrition, safety, responsive caregiving, and early learning.
- [WHO: Child health and development](https://www.who.int/teams/maternal-newborn-child-adolescent-health-and-ageing/child-health/nurturing-care) — child development and nurturing-care overview.
- [WHO: Nurturing care for young children through responsive feeding](https://www.who.int/publications/i/item/9789240070301) — responsive feeding as part of caregiving and nutrition.
- [CDC: Learn the Signs. Act Early.](https://www.cdc.gov/act-early/) — family-facing milestone resources; milestones support observation and do not replace developmental screening.

This reference is an educational starting point, not medical advice. It should be reviewed by an endocrinologist or other qualified subject-matter expert before driving product claims or individual recommendations.
