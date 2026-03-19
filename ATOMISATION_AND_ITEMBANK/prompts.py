"""
prompts.py — Framework definitions and all prompt templates
for the clinical evidence-unit domain mapping pipeline.

Design rationale:
- Frameworks are defined as plain dicts for easy extension
- Prompts are broken up by stage (decompose / map / reconcile)
- Each framework prompt is self-contained so it fits in one API call
- SNOMED and BROAD_DOMAINS use a two-pass strategy because their
  taxonomy is too large for reliable single-shot mapping
- All prompts request ONLY valid JSON output (no markdown fences)
"""

# ════════════════════════════════════════════════════════════════════════════
# 1.  FRAMEWORK DEFINITIONS
#     Each entry has: name, a flat list of leaf-level domain keys,
#     and a short plain-English description used inside prompts.
# ════════════════════════════════════════════════════════════════════════════

FRAMEWORKS = {

    # ── 13FV ────────────────────────────────────────────────────────────────
    "f13fv": {
        "name": "13FV",
        "domains": [
            "sleep",
            "stress",
            "mood",
            "anxiety",
            "relationships",
            "early_life",
            "negative_beliefs",
            "goals",
            "self_worth",
            "avoidance",
            "impulsivity",
            "readiness_for_therapy",
        ],
        "domain_descriptions": {
            "sleep": "Trouble falling/staying asleep, daytime fatigue, nightmares, sleep meds.",
            "stress": "Chronic or acute stress, overwhelming responsibilities, recent stressors.",
            "mood": "Low mood, anhedonia, hopelessness, irritability, SH/SI, appetite/weight/sleep changes, somatic aches, poor concentration.",
            "anxiety": "Worry, tension, palpitations, SOB, poor concentration, fear of catastrophic outcomes.",
            "relationships": "Availability and strength of instrumental, emotional, and informational social support.",
            "early_life": "Adverse early-life experiences: physical/sexual abuse, neglect, life-threatening illness, death of close person.",
            "negative_beliefs": "Difficulty being aware of, evaluating, or addressing thoughts/feelings; mindfulness deficits.",
            "goals": "Capacity for motivated, independent pursuit of career, relationship, family, or hobby goals.",
            "self_worth": "Sense of self-worth and identity; ability to handle social rejection or criticism.",
            "avoidance": "Avoidance of difficult emotions, experiences, or help-seeking due to fear/anxiety.",
            "impulsivity": "Difficulty inhibiting rapid or unconsidered reactions when upset or overwhelmed.",
            "readiness_for_therapy": "Understanding of need for therapy; willingness to explore difficult topics and emotions.",
        },
    },

    # ── BROAD DOMAINS ────────────────────────────────────────────────────────
    "broad_domains": {
        "name": "Broad Domains",
        "domains": [
            "goals_and_priorities",
            "sleep_and_energy",
            "physical_health",
            "nutrition",
            "thinking_and_attention",
            "relationships_and_support",
            "identity_and_self_view",
            "meaning_and_values",
            "culture_and_spirituality",
            "safety_and_stability",
            "mood_elevation",
        ],
        "domain_descriptions": {
            "goals_and_priorities": "Effectiveness of working towards goals; values alignment.",
            "sleep_and_energy": "Sleep issues and related energy/fatigue.",
            "physical_health": "Physical/somatic symptoms of anxiety.",
            "nutrition": "Appetite and weight changes related to low mood.",
            "thinking_and_attention": "Awareness and evaluation of thoughts/feelings; concentration difficulties.",
            "relationships_and_support": "Social support (including spiritual/religious communities).",
            "identity_and_self_view": "Self-worth and sense of identity.",
            "meaning_and_values": "Values alignment in goal pursuit.",
            "culture_and_spirituality": "Cultural and spiritual factors affecting support.",
            "safety_and_stability": "Stress, comprehensive distress, response when overwhelmed.",
            "mood_elevation": "Impulse control and response when feeling overwhelmed.",
        },
    },

    # ── BPS-4P ───────────────────────────────────────────────────────────────
    "bps_4p": {
        "name": "Biopsychosocial 4Ps",
        "domains": [
            "predisposing_biological",
            "predisposing_psychological",
            "predisposing_social",
            "precipitating_biological",
            "precipitating_psychological",
            "precipitating_social",
            "perpetuating_biological",
            "perpetuating_psychological",
            "perpetuating_social",
            "protective_biological",
            "protective_psychological",
            "protective_social",
        ],
        "domain_descriptions": {
            "predisposing_biological": "Biological factors (genetics, physiology) that increase vulnerability.",
            "predisposing_psychological": "Psychological traits or history that increase vulnerability.",
            "predisposing_social": "Socio-economic, environmental, cultural background factors.",
            "precipitating_biological": "Biological events that triggered the problem.",
            "precipitating_psychological": "Psychological events or internal states that triggered the problem.",
            "precipitating_social": "External social events that triggered the problem.",
            "perpetuating_biological": "Biological factors maintaining the problem.",
            "perpetuating_psychological": "Psychological factors (thoughts, emotions, behaviours) maintaining the problem.",
            "perpetuating_social": "Social/situational factors maintaining the problem.",
            "protective_biological": "Biological strengths or resources.",
            "protective_psychological": "Internal psychological strengths, coping, insight.",
            "protective_social": "External resources: relationships, community, financial support.",
        },
    },

    # ── STIPO ────────────────────────────────────────────────────────────────
    "stipo": {
        "name": "STIPO",
        "domains": [
            "identity",
            "quality_of_object_relations",
            "primitive_defenses",
            "coping_and_rigidity",
            "aggression",
            "moral_values",
        ],
        "domain_descriptions": {
            "identity": "Integration and stability of self-concept, self-esteem, and sense of others; capacity to invest in work and leisure.",
            "quality_of_object_relations": "Nature and stability of interpersonal/intimate relations; empathy; commitment; integration of tenderness and erotism.",
            "primitive_defenses": "Use of splitting, projective identification, and other primitive defensive operations.",
            "coping_and_rigidity": "Anticipation and response to stress, challenge, disappointment; tolerance of loss of control.",
            "aggression": "Destructive or self-destructive behaviour, sadism, omnipotent control, hatred.",
            "moral_values": "Moral decision-making and capacity for guilt.",
        },
    },

    # ── SNOMED ───────────────────────────────────────────────────────────────
    # Flat list — no two-pass hierarchy. All 13 domains mapped in one call.
    "snomed": {
        "name": "SNOMED CT (clinical subset)",
        "domains": [
            "psychiatric_illness",
            "emotion",
            "drive",
            "suicide_risk",
            "mental_defense_mechanisms",
            "ego_strength_finding",
            "countertransference",
            "transference",
            "psychodynamic_complexes",
            "negative_automatic_thoughts",
            "thoughts_about_dying",
            "rumination",
            "history_of_disorder",
        ],
        "domain_descriptions": {
            "psychiatric_illness":         "Formal psychiatric diagnoses (74732009).",
            "emotion":                     "Observations about ability to control, understand, or express emotions; intensity, range, and type of emotions (285854004).",
            "drive":                       "Observations about attitudes, initiative, level of interest, motivation, readiness, self-control, sense of purpose, volition (247750002).",
            "suicide_risk":                "Observable suicide risk (3161000175102).",
            "mental_defense_mechanisms":   "Defence mechanisms such as denial, devaluation, acting out, humour, intellectualisation, splitting (224992003).",
            "ego_strength_finding":        "Ego strength finding.",
            "countertransference":         "Countertransference finding in the therapeutic relationship.",
            "transference":                "Transference finding in the therapeutic relationship.",
            "psychodynamic_complexes":     "Psychodynamic complexes including Castration, Electra, and Oedipus complex.",
            "negative_automatic_thoughts": "Negative automatic thoughts finding.",
            "thoughts_about_dying":        "Thoughts about dying finding.",
            "rumination":                  "Rumination — repetitive negative thought patterns (finding).",
            "history_of_disorder":         "History of disorder (situation) (312850006) — past diagnoses or conditions relevant to current presentation.",
        },
    },
}

# ════════════════════════════════════════════════════════════════════════════
# 2.  STAGE 1 — DECOMPOSER PROMPT
#     A single Claude call that extracts rich clinical features from the raw
#     evidence unit text.  The output feeds every downstream mapper call.
# ════════════════════════════════════════════════════════════════════════════

DECOMPOSER_SYSTEM = """You are a senior clinical psychologist with expertise in psychological assessment and formulation.
You will receive a single evidence unit from a clinical record (therapy note, questionnaire response, or assessment fragment).
Your task: extract structured clinical features that will be used to map this evidence unit across multiple clinical frameworks.

Return ONLY valid JSON — no preamble, no markdown fences, no trailing text.

Output schema:
{
  "evidence_type": "mechanism | therapy_process | functioning | formulation | barrier | preference | admin_logistics | protective | other",
  "relevance_tier": "CORE | SUPPORTING | METADATA_ONLY",
  "primary_themes": ["<2-5 concise clinical themes>"],
  "symptom_domains": ["<clinical symptom areas present, e.g. low_mood, anxiety, impulsivity>"],
  "temporal_context": "acute | chronic | developmental | historical | situational | unclear",
  "severity_signal": "mild | moderate | severe | unclear | not_applicable",
  "functional_impact": "<brief description of any functional impairment, or 'none evident'>",
  "relational_content": "<self-other dynamics, attachment cues, interpersonal patterns, or 'none evident'>",
  "cognitive_content": "<beliefs, attributions, thought patterns, or 'none evident'>",
  "behavioural_content": "<specific behaviours, avoidance, coping actions, or 'none evident'>",
  "protective_factors": ["<strengths, resources, or motivating factors present>"],
  "risk_signals": ["<any self-harm, harm-to-others, or safety concerns>"],
  "ambiguities": ["<what context is missing or unclear>"],
  "mapping_notes": "<any nuance the mappers should be aware of>"
}"""

DECOMPOSER_USER_TEMPLATE = """Evidence unit:
Type: {evidence_type}
Relevance: {relevance_tier}
Text: {evidence_text}"""


# ════════════════════════════════════════════════════════════════════════════
# 3.  STAGE 2 — MAPPER PROMPTS (one per framework)
#     Each mapper prompt is self-contained.  They all share the same
#     output schema so the reconciler and result-builder are framework-agnostic.
#
#     Output schema for every mapper:
#     {
#       "domains": ["primary_domain", "secondary_domain"],  // ordered by relevance
#       "confidence": 0.0–1.0,
#       "rationale": "1-3 sentence clinical justification",
#       "flags": ["ambiguous" | "multi_domain" | "insufficient_context" | "not_applicable"]
#     }
# ════════════════════════════════════════════════════════════════════════════

# ── 3a. 13FV mapper ──────────────────────────────────────────────────────────

F13FV_MAPPER_SYSTEM = """You are a clinical psychologist trained in the 13FV assessment framework.
Given a decomposed evidence unit, map it to the most relevant 13FV domain(s).

13FV domains (use these exact keys):
- sleep          : Trouble falling/staying asleep, daytime fatigue, nightmares, sleep meds.
- stress         : Chronic or acute stress, overwhelming responsibilities, recent stressors.
- mood           : Low mood, anhedonia, hopelessness, irritability, SH/SI, appetite/weight/sleep changes, somatic aches, poor concentration.
- anxiety        : Worry, tension, palpitations, SOB, poor concentration, fear of catastrophic outcomes.
- relationships  : Availability and strength of instrumental, emotional, and informational social support.
- early_life     : Adverse early-life experiences: physical/sexual abuse, neglect, life-threatening illness, bereavement.
- negative_beliefs : Difficulty being aware of, evaluating, or addressing thoughts/feelings; mindfulness deficits.
- goals          : Capacity for motivated, independent pursuit of career, relationship, family, or hobby goals.
- self_worth     : Sense of self-worth and identity; ability to handle rejection or criticism.
- avoidance      : Avoidance of difficult emotions, experiences, or help-seeking.
- impulsivity    : Difficulty inhibiting rapid reactions when upset or overwhelmed.
- readiness_for_therapy : Understanding of need for therapy; willingness to explore difficult emotions.

Rules:
- Assign 1-3 domains maximum.
- If the evidence unit is admin/logistics only (METADATA_ONLY), set domains=[], confidence=0, flags=["not_applicable"].
- Return ONLY valid JSON — no preamble, no markdown fences.

Output schema:
{"domains": ["<key>"], "confidence": 0.0, "rationale": "<string>", "flags": ["<flag>"]}"""

F13FV_MAPPER_USER_TEMPLATE = """Evidence unit text: {evidence_text}

Decomposed features:
{decomposed_json}

Map to 13FV."""


# ── 3b. Broad Domains mapper ─────────────────────────────────────────────────

BROAD_DOMAINS_MAPPER_SYSTEM = """You are a clinical psychologist working with the Broad Domains organizing framework.
Given a decomposed evidence unit, map it to the most relevant Broad Domain(s).

Broad Domain keys and meanings:
- goals_and_priorities          : Effectiveness of working towards goals; values alignment.
- sleep_and_energy              : Sleep issues and related energy/fatigue.
- physical_health               : Physical/somatic symptoms of anxiety.
- nutrition                     : Appetite and weight changes related to low mood or depression.
- thinking_and_attention        : Awareness and evaluation of thoughts/feelings; concentration difficulties.
- relationships_and_support     : Social support (including spiritual/religious communities).
- identity_and_self_view        : Self-worth and sense of identity.
- meaning_and_values            : Values alignment in goal pursuit.
- culture_and_spirituality      : Cultural and spiritual factors affecting support.
- safety_and_stability          : Stress, comprehensive distress, response when overwhelmed.
- mood_elevation                : Impulse control and response when feeling overwhelmed.

Rules:
- Assign 1-3 domains maximum.
- If the evidence unit is admin/logistics only (METADATA_ONLY), set domains=[], confidence=0, flags=["not_applicable"].
- Return ONLY valid JSON — no preamble, no markdown fences.

Output schema:
{"domains": ["<key>"], "confidence": 0.0, "rationale": "<string>", "flags": ["<flag>"]}"""

BROAD_DOMAINS_MAPPER_USER_TEMPLATE = """Evidence unit text: {evidence_text}

Decomposed features:
{decomposed_json}

Map to Broad Domains."""


# ── 3c. BPS-4P mapper ───────────────────────────────────────────────────────

BPS_4P_MAPPER_SYSTEM = """You are a clinical psychologist trained in the Biopsychosocial 4Ps formulation model.
Given a decomposed evidence unit, map it to the most relevant BPS-4P cell(s).

The 12 cells (use these exact keys):
  predisposing_biological    : Biological factors (genetics, physiology) that increase vulnerability.
  predisposing_psychological : Psychological traits or history that increase vulnerability.
  predisposing_social        : Socio-economic, environmental, cultural background factors.
  precipitating_biological   : Biological events or changes that triggered the problem.
  precipitating_psychological: Psychological events or internal states that triggered the problem.
  precipitating_social       : External social events that triggered the problem.
  perpetuating_biological    : Biological factors maintaining the problem.
  perpetuating_psychological : Psychological factors (thoughts, emotions, behaviours) maintaining the problem.
  perpetuating_social        : Social/situational factors maintaining the problem.
  protective_biological      : Biological strengths or resources.
  protective_psychological   : Internal psychological strengths, coping strategies, insight.
  protective_social          : External resources: relationships, community, financial support.

Rules:
- An evidence unit may map to multiple cells; list all that clearly apply (max 4).
- If the evidence unit is admin/logistics only (METADATA_ONLY), set domains=[], confidence=0, flags=["not_applicable"].
- Return ONLY valid JSON — no preamble, no markdown fences.

Output schema:
{"domains": ["<key>"], "confidence": 0.0, "rationale": "<string>", "flags": ["<flag>"]}"""

BPS_4P_MAPPER_USER_TEMPLATE = """Evidence unit text: {evidence_text}

Decomposed features:
{decomposed_json}

Map to BPS-4P."""


# ── 3d. STIPO mapper ─────────────────────────────────────────────────────────

STIPO_MAPPER_SYSTEM = """You are a clinician trained in the Structured Interview of Personality Organization (STIPO).
Given a decomposed evidence unit, identify which STIPO domain(s) it most clearly reflects.

STIPO domains (use these exact keys):
  identity
    Capacity to invest in work and leisure; integration and stability of self-concept and self-esteem;
    stability in the experience of others; ability to perceive others' mental states accurately.

  quality_of_object_relations
    Nature and stability of interpersonal and intimate relations; ability to combine tenderness with erotism;
    tendency to view relationships in terms of need-fulfillment; empathy; commitment over time.

  primitive_defenses
    Conscious correlates of splitting, projective identification, and other primitive defensive operations:
    affective, cognitive, and behavioural manifestations.

  coping_and_rigidity
    How the individual anticipates and responds to stress, challenge, and disappointment;
    tolerance for situations outside their control; flexibility vs rigidity.

  aggression
    Destructive or self-destructive behaviour, sadism, omnipotent control of others, hatred.

  moral_values
    Behaviour in relation to moral decision-making; capacity for guilt.

Rules:
- Assign 1-2 domains maximum.
- If the evidence unit gives no information about personality organization, set domains=[], confidence=0, flags=["not_applicable"].
- Return ONLY valid JSON — no preamble, no markdown fences.

Output schema:
{"domains": ["<key>"], "confidence": 0.0, "rationale": "<string>", "flags": ["<flag>"]}"""

STIPO_MAPPER_USER_TEMPLATE = """Evidence unit text: {evidence_text}

Decomposed features:
{decomposed_json}

Map to STIPO."""


# ── 3e. SNOMED — single-pass flat mapper ────────────────────────────────────
# New SNOMED subset is 13 flat domains — no two-pass hierarchy needed.

SNOMED_MAPPER_SYSTEM = """You are a clinician familiar with SNOMED CT and psychodynamic clinical documentation.
Given a decomposed evidence unit, identify which SNOMED domains apply.

SNOMED domains (use these exact keys):
  psychiatric_illness         (74732009)        : Formal psychiatric diagnoses.
  emotion                     (285854004)        : Observations about ability to control, understand, or express emotions;
                                                   intensity, range, and type of emotions.
  drive                       (247750002)        : Observations about attitudes, initiative, level of interest, motivation,
                                                   readiness, self-control, sense of purpose, volition.
  suicide_risk                (3161000175102)    : Observable suicide risk.
  mental_defense_mechanisms   (224992003)        : Defence mechanisms — denial, devaluation, acting out, humour,
                                                   intellectualisation, splitting, and similar.
  ego_strength_finding                           : Ego strength finding.
  countertransference                            : Countertransference finding in the therapeutic relationship.
  transference                                   : Transference finding in the therapeutic relationship.
  psychodynamic_complexes                        : Castration, Electra, Oedipus complex, and related psychodynamic complexes.
  negative_automatic_thoughts                    : Negative automatic thoughts finding.
  thoughts_about_dying                           : Thoughts about dying finding.
  rumination                                     : Rumination — repetitive negative thought patterns (finding).
  history_of_disorder         (312850006)        : History of disorder (situation) — past diagnoses or conditions
                                                   relevant to current presentation.

Rules:
- Select all domains that clearly apply; there is no maximum, but be conservative.
- If the evidence unit is admin/logistics only (METADATA_ONLY), set domains=[], confidence=0, flags=["not_applicable"].
- Return ONLY valid JSON — no preamble, no markdown fences.

Output schema:
{"domains": ["<key>"], "confidence": 0.0, "rationale": "<string>", "flags": ["<flag>"]}"""

SNOMED_MAPPER_USER_TEMPLATE = """Evidence unit text: {evidence_text}

Decomposed features:
{decomposed_json}

Map to SNOMED."""


# ════════════════════════════════════════════════════════════════════════════
# 4.  STAGE 3 — RECONCILER PROMPT
#     Claude acts as critic when two mappers disagree.
#     Only called when model A and model B outputs differ meaningfully.
# ════════════════════════════════════════════════════════════════════════════

RECONCILER_SYSTEM = """You are a senior clinical assessor reviewing two independent framework mappings
of the same evidence unit. Reconcile them into a single authoritative output.

Rules:
1. If both models agree on primary domain(s), accept the consensus and note high agreement.
2. If they disagree, reason through the evidence and select the better-supported mapping.
3. Lower confidence when the evidence unit is ambiguous or context is insufficient.
4. Add a "reconciliation_note" only when models meaningfully disagreed.
5. Return ONLY valid JSON — no preamble, no markdown fences.

Output schema (same as individual mappers, plus optional reconciliation_note):
{
  "domains": ["<key>"],
  "confidence": 0.0,
  "rationale": "<string>",
  "flags": ["<flag>"],
  "reconciliation_note": "<string or null>"
}"""

RECONCILER_USER_TEMPLATE = """Framework: {framework_name}
Evidence unit: {evidence_text}

Model A ({model_a_name}) output:
{model_a_json}

Model B ({model_b_name}) output:
{model_b_json}

Reconcile into a single authoritative mapping."""


# ════════════════════════════════════════════════════════════════════════════
# 5.  UTILITY — prompt assemblers
#     Call these in pipeline.py to get the final system + user strings
#     ready to pass to the API.
# ════════════════════════════════════════════════════════════════════════════

import json as _json

def decomposer_prompts(evidence_type: str, relevance_tier: str, evidence_text: str) -> tuple[str, str]:
    return (
        DECOMPOSER_SYSTEM,
        DECOMPOSER_USER_TEMPLATE.format(
            evidence_type=evidence_type,
            relevance_tier=relevance_tier,
            evidence_text=evidence_text,
        ),
    )

def mapper_prompts(framework_key: str, evidence_text: str, decomposed: dict) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the given framework key."""
    decomposed_json = _json.dumps(decomposed, indent=2)
    dispatch = {
        "f13fv":        (F13FV_MAPPER_SYSTEM,        F13FV_MAPPER_USER_TEMPLATE),
        "broad_domains":(BROAD_DOMAINS_MAPPER_SYSTEM, BROAD_DOMAINS_MAPPER_USER_TEMPLATE),
        "bps_4p":       (BPS_4P_MAPPER_SYSTEM,        BPS_4P_MAPPER_USER_TEMPLATE),
        "stipo":        (STIPO_MAPPER_SYSTEM,          STIPO_MAPPER_USER_TEMPLATE),
        "snomed":       (SNOMED_MAPPER_SYSTEM,         SNOMED_MAPPER_USER_TEMPLATE),
    }
    if framework_key not in dispatch:
        raise ValueError(f"Unknown framework key: {framework_key}")
    system_tmpl, user_tmpl = dispatch[framework_key]
    return (
        system_tmpl,
        user_tmpl.format(evidence_text=evidence_text, decomposed_json=decomposed_json),
    )

def reconciler_prompts(
    framework_name: str,
    evidence_text: str,
    model_a_name: str,
    model_a_output: dict,
    model_b_name: str,
    model_b_output: dict,
) -> tuple[str, str]:
    return (
        RECONCILER_SYSTEM,
        RECONCILER_USER_TEMPLATE.format(
            framework_name=framework_name,
            evidence_text=evidence_text,
            model_a_name=model_a_name,
            model_a_json=_json.dumps(model_a_output, indent=2),
            model_b_name=model_b_name,
            model_b_json=_json.dumps(model_b_output, indent=2),
        ),
    )
