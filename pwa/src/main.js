import './style.css';
import { formatChartAsk, formatChartSet, parseChartAsk } from '../../shared/chart-command.mjs';
import { generateBodygraphInputPrompt } from '../../shared/bodygraph-prompt.mjs';
import { BODYGRAPH_REFERENCE_URL } from './reference-assets.js';
import cycleDayExample from '../../examples/reported-cycle-day-view.example.json';
import measurementSeriesExample from '../../examples/measurement-series-summary.example.json';
import urinaryLhExample from '../../examples/urinary-lh-home-test.example.json';
import affordanceTrialExample from '../../examples/affordance-trial-summary.example.json';

const $ = (selector) => document.querySelector(selector);
const connectForm = $('#connect-form');
const connectPanel = $('#connection-panel');
const roomPicker = $('#room-picker');
const roomPickerSelect = $('#room-picker-select');
const conversation = $('#conversation');
const bodygraphPanel = $('#bodygraph-panel');
const timeline = $('#timeline');
const statusLine = $('#connect-status');
const syncIndicator = $('#sync-indicator');
const messageForm = $('#message-form');
const messageInput = $('#message-input');
const cycleDayFileInput = $('#cycle-day-file');
const measurementSeriesFileInput = $('#measurement-series-file');
const affordanceTrialFileInput = $('#affordance-trial-file');
const GATE_AI_AFFORDANCES_URL = '/chat/gate-ai-affordances.json';
const CASTALIA_HOMESERVER = 'https://matrix.castalia.institute';
const CASTALIA_SSO_IDP = 'oidc-supabase';
const CASTALIA_SSO_TRANSACTION_KEY = 'metheus.matrix.castalia-sso-transaction.v1';
const pendingSsoCallback = window.__metheusSsoCallback || null;
delete window.__metheusSsoCallback;
const METHEUS_GATE_PROFILE_KEY = 'metheus.pwa.symbolic-gate-profile.v1';
const INTERACTION_MODES = new Set(['create', 'organize', 'compare', 'communicate', 'reflect', 'adapt', 'practice', 'coordinate', 'learn']);
const BODYGRAPH_CENTERS = new Set(['head', 'ajna', 'throat', 'g_identity', 'heart', 'solar_plexus', 'sacral', 'spleen', 'root']);
const CENTER_LABELS = {
  head: 'Head', ajna: 'Ajna', throat: 'Throat', g_identity: 'G / Identity', heart: 'Heart / Ego',
  solar_plexus: 'Solar Plexus', sacral: 'Sacral', spleen: 'Spleen', root: 'Root',
};
const session = { client: null, sdk: null, userId: null, roomId: null, encrypted: false, seen: new Set() };
let deferredInstall = null;
let bodygraph = null;
let bodygraphLoadPromise = null;
let bodygraphLifecycle = 0;
let gateAiAffordances = [];
let gateAiAffordanceCatalogVersion = '';
let gateAiAffordanceCatalog = null;
let gateAiTopology = null;
let pendingGateTrial = null;
const selectedChartGates = new Set();
const selectedMetheusGates = new Set(readMetheusGateProfile());
const recentBodygraphMentions = [];
let comparingGateMaps = false;
let pendingChartPromptMode = 'ask';

function readMetheusGateProfile() {
  try {
    const stored = JSON.parse(localStorage.getItem(METHEUS_GATE_PROFILE_KEY) || '[]');
    return Array.isArray(stored)
      ? [...new Set(stored.filter((gate) => Number.isInteger(gate) && gate >= 1 && gate <= 64))]
      : [];
  } catch {
    return [];
  }
}

function saveMetheusGateProfile() {
  try { localStorage.setItem(METHEUS_GATE_PROFILE_KEY, JSON.stringify([...selectedMetheusGates].sort((a, b) => a - b))); }
  catch { $('#ai-guide-status').textContent = 'The Metheus profile is active for this page session but could not be saved in this browser.'; }
}

function isIsoCalendarDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

function validateReportedCycleDayView(view) {
  if (
    !view || view.contextType !== 'reported_cycle_day_view'
    || view.contextScope !== 'explicitly_selected_same_subject_records'
    || typeof view.subjectId !== 'string' || !view.subjectId
    || view.methodVersion !== 'metheus-reported-cycle-day-view/0.1.0'
    || !Array.isArray(view.cycleDayOneMarkers) || !view.cycleDayOneMarkers.length
    || !Array.isArray(view.observations) || !view.observations.length
    || !Array.isArray(view.sourceRecordIds) || !Array.isArray(view.limitations)
    || !view.consentPreflight || view.consentPreflight.policyVersion !== 'metheus-consent-policy/0.5.0'
    || view.consentPreflight.purpose !== 'rhythm_summary' || view.consentPreflight.action !== 'analyze'
    || !['authorized', 'synthetic_example'].includes(view.consentPreflight.status)
    || typeof view.consentPreflight.checkedAt !== 'string' || Number.isNaN(Date.parse(view.consentPreflight.checkedAt))
    || !Array.isArray(view.consentPreflight.recordGrantIds) || !Array.isArray(view.consentPreflight.limitations)
  ) return false;
  const sourceIds = new Set(view.sourceRecordIds);
  if (sourceIds.size !== view.sourceRecordIds.length || [...sourceIds].some((id) => typeof id !== 'string' || !id)) return false;
  const markerIds = new Set();
  let priorMarkerDate = '';
  for (const marker of view.cycleDayOneMarkers) {
    if (
      !marker || !isIsoCalendarDate(marker.date) || marker.date <= priorMarkerDate
      || !Array.isArray(marker.recordIds) || marker.recordIds.length === 0
      || new Set(marker.recordIds).size !== marker.recordIds.length
      || marker.recordIds.some((id) => typeof id !== 'string' || !id || !sourceIds.has(id) || markerIds.has(id))
      || !['date_only', 'timestamp_local_calendar_date'].includes(marker.timePrecision)
    ) return false;
    marker.recordIds.forEach((id) => markerIds.add(id));
    priorMarkerDate = marker.date;
  }
  if (!markerIds.size) return false;
  const observationIds = new Set();
  const observationUnion = new Set();
  for (const record of view.observations) {
    if (
      !record || typeof record.recordId !== 'string' || !record.recordId
      || observationIds.has(record.recordId) || markerIds.has(record.recordId) || !sourceIds.has(record.recordId)
      || (record.date !== null && !isIsoCalendarDate(record.date))
      || !['date_only', 'timestamp_local_calendar_date', 'unknown'].includes(record.timePrecision)
      || !['observation', 'event'].includes(record.recordType)
      || typeof record.domain !== 'string' || !record.domain
      || typeof record.epistemicClass !== 'string' || !record.epistemicClass
      || typeof record.label !== 'string' || !record.label
      || (record.eventType !== undefined && (typeof record.eventType !== 'string' || !record.eventType))
      || (record.value !== undefined && (!record.value || typeof record.value !== 'object' || Array.isArray(record.value)))
      || (record.source !== undefined && (
        !record.source || typeof record.source !== 'object' || Array.isArray(record.source)
        || typeof record.source.kind !== 'string'
        || Object.values(record.source).some((value) => typeof value !== 'string')
      ))
      || (record.measurementDetails !== undefined && (
        !record.measurementDetails || typeof record.measurementDetails !== 'object' || Array.isArray(record.measurementDetails)
        || Object.values(record.measurementDetails).some((value) => typeof value !== 'string')
      ))
      || !(record.reportedCycleDay === null || (Number.isInteger(record.reportedCycleDay) && record.reportedCycleDay >= 1))
      || !Array.isArray(record.cycleStartRecordIds)
      || new Set(record.cycleStartRecordIds).size !== record.cycleStartRecordIds.length
      || record.cycleStartRecordIds.some((id) => !markerIds.has(id))
      || !['between_selected_day_one_markers', 'since_latest_selected_day_one_marker', 'before_first_selected_marker', 'unknown_time'].includes(record.windowRelation)
    ) return false;
    observationIds.add(record.recordId);
    observationUnion.add(record.recordId);

    if (record.date === null) {
      if (record.timePrecision !== 'unknown' || record.reportedCycleDay !== null || record.cycleStartRecordIds.length || record.windowRelation !== 'unknown_time') return false;
      continue;
    }
    if (record.timePrecision === 'unknown') return false;
    const precedingMarkers = view.cycleDayOneMarkers.filter((marker) => marker.date <= record.date);
    if (precedingMarkers.length === 0) {
      if (record.reportedCycleDay !== null || record.cycleStartRecordIds.length || record.windowRelation !== 'before_first_selected_marker') return false;
      continue;
    }
    const startMarker = precedingMarkers.at(-1);
    const nextMarker = view.cycleDayOneMarkers.find((marker) => marker.date > record.date);
    const expectedRelation = nextMarker ? 'between_selected_day_one_markers' : 'since_latest_selected_day_one_marker';
    const expectedIds = [...startMarker.recordIds].sort();
    if (
      record.reportedCycleDay !== (new Date(`${record.date}T00:00:00Z`) - new Date(`${startMarker.date}T00:00:00Z`)) / 86_400_000 + 1
      || [...record.cycleStartRecordIds].sort().join('|') !== expectedIds.join('|')
      || record.windowRelation !== expectedRelation
    ) return false;
  }
  const expectedSourceIds = new Set([...markerIds, ...observationUnion]);
  const coveredIds = new Set();
  const grantCoverageValid = view.consentPreflight.recordGrantIds.every((item) => {
    if (!item || typeof item.recordId !== 'string' || !sourceIds.has(item.recordId) || coveredIds.has(item.recordId) || typeof item.grantId !== 'string' || !item.grantId) return false;
    coveredIds.add(item.recordId);
    return true;
  });
  return expectedSourceIds.size === sourceIds.size
    && [...expectedSourceIds].every((id) => sourceIds.has(id))
    && grantCoverageValid
    && coveredIds.size === sourceIds.size
    && view.limitations.length > 0
    && view.limitations.every((item) => typeof item === 'string')
    && view.consentPreflight.limitations.length > 0
    && view.consentPreflight.limitations.every((item) => typeof item === 'string');
}

function displayReportedCycleDayView(view) {
  const results = $('#cycle-day-results');
  const markerDates = view.cycleDayOneMarkers.map((marker) => marker.date).sort();
  $('#cycle-day-markers').textContent = `Selected day-one markers: ${markerDates.join(' · ')}. Day labels are calendar-date offsets, not hormone phases.`;
  $('#cycle-day-consent').textContent = view.consentPreflight.status === 'synthetic_example'
    ? 'Synthetic authorization example only; no real consent check was performed.'
    : `Local consent preflight reported authorization for ${view.consentPreflight.recordGrantIds.length} selected records at ${view.consentPreflight.checkedAt}. This unsigned receipt is based on supplied grants; it does not verify identity or authority.`;
  const body = $('#cycle-day-rows');
  body.replaceChildren();
  const rows = [...view.observations].sort((a, b) => (a.date || '').localeCompare(b.date || '') || a.recordId.localeCompare(b.recordId));
  for (const record of rows) {
    const row = document.createElement('tr');
    const dateCell = document.createElement('td');
    dateCell.textContent = record.date || 'Date unavailable';
    const dayCell = document.createElement('td');
    dayCell.textContent = record.reportedCycleDay === null ? record.windowRelation.replaceAll('_', ' ') : `Day ${record.reportedCycleDay}`;
    const recordCell = document.createElement('td');
    const title = document.createElement('strong');
    title.textContent = record.label;
    const context = document.createElement('div');
    context.textContent = `${record.domain} · ${record.epistemicClass}`;
    recordCell.append(title, context);
    const valueCell = document.createElement('td');
    if (record.value && typeof record.value === 'object') {
      const visible = Object.entries(record.value).map(([key, value]) => `${key}: ${typeof value === 'object' ? JSON.stringify(value) : String(value)}`).join(' · ');
      valueCell.textContent = visible.length > 240 ? `${visible.slice(0, 237)}…` : visible;
    } else valueCell.textContent = '—';
    const sourceCell = document.createElement('td');
    const sourceParts = [record.source?.kind, record.source?.name, record.source?.method, record.source?.version, record.source?.reportedByRelation]
      .filter((value) => typeof value === 'string' && value);
    const measurementParts = record.measurementDetails
      ? Object.entries(record.measurementDetails).map(([key, value]) => `${key}: ${value}`).filter(Boolean)
      : [];
    sourceCell.textContent = [...sourceParts, ...measurementParts].join(' · ') || 'Source not specified';
    const basisCell = document.createElement('td');
    const startDates = view.cycleDayOneMarkers
      .filter((marker) => record.cycleStartRecordIds.includes(marker.recordIds[0]) || marker.recordIds.some((id) => record.cycleStartRecordIds.includes(id)))
      .map((marker) => marker.date);
    basisCell.textContent = record.cycleStartRecordIds.length ? `From ${startDates.join(', ') || 'selected marker'} · ${record.timePrecision}` : record.timePrecision;
    row.append(dateCell, dayCell, recordCell, valueCell, sourceCell, basisCell);
    body.append(row);
  }
  $('#cycle-day-limit').textContent = view.limitations.join(' ');
  results.hidden = false;
  $('#cycle-day-clear').disabled = false;
}

if (cycleDayFileInput) {
  $('#cycle-day-preview').addEventListener('click', () => {
    if (!validateReportedCycleDayView(cycleDayExample)) {
      $('#cycle-day-status').textContent = 'The bundled synthetic cycle-day example is invalid.';
      return;
    }
    displayReportedCycleDayView(cycleDayExample);
    $('#cycle-day-status').textContent = 'Synthetic example loaded in this tab. It contains no personal data.';
  });
  cycleDayFileInput.addEventListener('change', async () => {
    const file = cycleDayFileInput.files?.[0];
    const status = $('#cycle-day-status');
    if (!file) return;
    if (file.size > 1_000_000) {
      status.textContent = 'This view file is larger than 1 MB. Choose a smaller, explicitly selected view.';
      $('#cycle-day-rows').replaceChildren();
      $('#cycle-day-results').hidden = true;
      $('#cycle-day-clear').disabled = true;
      cycleDayFileInput.value = '';
      return;
    }
    try {
      const parsed = JSON.parse(await file.text());
      const view = parsed?.view || parsed;
      if (!validateReportedCycleDayView(view)) throw new Error('invalid view');
      displayReportedCycleDayView(view);
      status.textContent = `Loaded ${view.observations.length} selected records for this tab only. The file has not been shared with your circle or Mētheus AI.`;
    } catch {
      $('#cycle-day-rows').replaceChildren();
      $('#cycle-day-results').hidden = true;
      $('#cycle-day-clear').disabled = true;
      status.textContent = 'Could not read this file as a valid Metheus reported-cycle-day view. No data was sent.';
    } finally {
      cycleDayFileInput.value = '';
    }
  });
  $('#cycle-day-clear').addEventListener('click', () => {
    $('#cycle-day-rows').replaceChildren();
    $('#cycle-day-results').hidden = true;
    $('#cycle-day-status').textContent = 'Local cycle-day view cleared from this tab.';
    $('#cycle-day-clear').disabled = true;
  });
}

function validNullableNumber(value) {
  return value === null || (typeof value === 'number' && Number.isFinite(value));
}

function validateUncertaintyMetadata(metadata, measurementCount) {
  const levels = ['low', 'moderate', 'high', 'unknown', 'not_reported'];
  return Boolean(metadata && Number.isInteger(metadata.recordsWithUncertaintyObject)
    && metadata.recordsWithUncertaintyObject >= 0
    && metadata.recordsWithUncertaintyObject <= measurementCount
    && metadata.levelCounts && levels.every((level) => Number.isInteger(metadata.levelCounts[level]) && metadata.levelCounts[level] >= 0)
    && Object.keys(metadata.levelCounts).length === levels.length
    && levels.reduce((sum, level) => sum + metadata.levelCounts[level], 0) === measurementCount);
}

function describeUncertaintyMetadata(metadata) {
  const counts = metadata.levelCounts;
  return `Recorded uncertainty labels: low ${counts.low}, moderate ${counts.moderate}, high ${counts.high}, unknown ${counts.unknown}, not reported ${counts.not_reported}; an uncertainty object was present on ${metadata.recordsWithUncertaintyObject} of ${Object.values(counts).reduce((sum, count) => sum + count, 0)} measurements.`;
}

function validateMeasurementSeriesSummary(summary) {
  const series = summary?.measurementSeries;
  const coverage = summary?.coverage;
  const overallStats = ['medianNumericValue', 'medianAbsoluteDeviationValue', 'minimumValue', 'maximumValue'];
  if (
    !summary || summary.recordType !== 'rhythm_summary'
    || summary.summaryType !== 'derived_rhythm_summary'
    || summary.summaryMeasure !== 'measurement_series'
    || summary.methodVersion !== 'metheus-numeric-measurement-series/0.3.0'
    || typeof summary.id !== 'string' || !summary.id
    || typeof summary.subjectId !== 'string' || !summary.subjectId
    || typeof summary.domain !== 'string' || !summary.domain
    || typeof summary.label !== 'string' || !summary.label
    || !summary.window || !isIsoCalendarDate(summary.window.startDate)
    || !isIsoCalendarDate(summary.window.endDate)
    || !Array.isArray(summary.inputRecordIds) || summary.inputRecordIds.length === 0
    || new Set(summary.inputRecordIds).size !== summary.inputRecordIds.length
    || summary.inputRecordIds.some((id) => typeof id !== 'string' || !id)
    || !Array.isArray(summary.limitations) || !summary.limitations.length
    || summary.limitations.some((item) => typeof item !== 'string' || !item)
    || !series || typeof series !== 'object'
    || ['analyteOrSignal', 'unit', 'epistemicClass', 'sourceKind', 'sourceName', 'sourceMethod', 'sourceVersion', 'methodDetails', 'specimen', 'sensorLocation', 'deviceOrAssay', 'deviceModel', 'algorithmVersion', 'collectionConditions']
      .some((key) => typeof series[key] !== 'string' || !series[key])
    || !Number.isInteger(summary.nMeasurements) || summary.nMeasurements < 0
    || !Number.isInteger(summary.nDistinctMeasurementDates) || summary.nDistinctMeasurementDates < 0
    || !Number.isInteger(summary.recordsWithQualityFlags) || summary.recordsWithQualityFlags < 0
    || !Array.isArray(summary.qualityFlags) || summary.qualityFlags.some((flag) => typeof flag !== 'string')
    || !validateUncertaintyMetadata(summary.uncertaintyMetadata, summary.nMeasurements)
    || !validNullableNumber(summary.medianNumericValue)
    || !validNullableNumber(summary.medianAbsoluteDeviationValue)
    || !validNullableNumber(summary.minimumValue)
    || !validNullableNumber(summary.maximumValue)
    || !coverage || !Number.isInteger(coverage.daysWithAtLeastOneRecord)
    || !Number.isInteger(coverage.calendarDaysInWindow) || coverage.calendarDaysInWindow < 1
    || typeof coverage.fractionOfDaysWithARecord !== 'number'
    || !Number.isFinite(coverage.fractionOfDaysWithARecord)
    || coverage.fractionOfDaysWithARecord < 0 || coverage.fractionOfDaysWithARecord > 1
    || !Array.isArray(summary.timeBuckets) || !summary.timeBuckets.length
  ) return false;
  if (summary.nMeasurements === 0 && overallStats.some((key) => summary[key] !== null)) return false;
  if (summary.nMeasurements > 0 && overallStats.some((key) => typeof summary[key] !== 'number')) return false;
  return summary.timeBuckets.every((bucket) =>
    bucket && isIsoCalendarDate(bucket.startDate) && isIsoCalendarDate(bucket.endDate)
    && Number.isInteger(bucket.inclusiveDays) && bucket.inclusiveDays > 0
    && Number.isInteger(bucket.nMeasurements) && bucket.nMeasurements >= 0
    && Number.isInteger(bucket.nDistinctMeasurementDates) && bucket.nDistinctMeasurementDates >= 0
    && ['medianValue', 'medianAbsoluteDeviationValue', 'minimumValue', 'maximumValue'].every((key) => validNullableNumber(bucket[key]))
    && Number.isInteger(bucket.daysWithAtLeastOneRecord) && bucket.daysWithAtLeastOneRecord >= 0
    && typeof bucket.fractionOfDaysWithARecord === 'number'
    && Number.isFinite(bucket.fractionOfDaysWithARecord)
    && bucket.fractionOfDaysWithARecord >= 0 && bucket.fractionOfDaysWithARecord <= 1
    && Array.isArray(bucket.inputRecordIds)
    && bucket.inputRecordIds.every((id) => summary.inputRecordIds.includes(id))
    && Array.isArray(bucket.qualityFlags)
    && bucket.qualityFlags.every((flag) => typeof flag === 'string')
    && validateUncertaintyMetadata(bucket.uncertaintyMetadata, bucket.nMeasurements)
    && (bucket.nMeasurements === 0
      ? ['medianValue', 'medianAbsoluteDeviationValue', 'minimumValue', 'maximumValue'].every((key) => bucket[key] === null)
      : ['medianValue', 'medianAbsoluteDeviationValue', 'minimumValue', 'maximumValue'].every((key) => typeof bucket[key] === 'number'))
  );
}

function isTrialSummaryTime(time) {
  if (time === null) return true;
  if (!time || typeof time !== 'object' || Array.isArray(time)) return false;
  return ['exact', 'approximate', 'date_only', 'unknown'].includes(time.precision)
    && (time.observedAt === undefined || (typeof time.observedAt === 'string' && !Number.isNaN(Date.parse(time.observedAt))))
    && (time.start === undefined || (typeof time.start === 'string' && !Number.isNaN(Date.parse(time.start))))
    && (time.end === undefined || (typeof time.end === 'string' && !Number.isNaN(Date.parse(time.end))))
    && (time.date === undefined || isIsoCalendarDate(time.date))
    && (time.timeZone === undefined || typeof time.timeZone === 'string');
}

function validateAffordanceTrialSummary(summary) {
  const lifecycleKinds = new Set(['made_available', 'offered', 'chosen', 'declined', 'unavailable', 'started', 'used', 'partial_use', 'stopped', 'revised']);
  const temporalKinds = new Set(['precedes', 'follows', 'overlaps', 'same_instant', 'same_calendar_date', 'indeterminate']);
  const inputIds = summary?.inputRecordIds;
  if (
    !summary || typeof summary !== 'object' || Array.isArray(summary)
    || typeof summary.summaryId !== 'string' || !/^affordance-trial:[a-f0-9]{16}$/.test(summary.summaryId)
    || typeof summary.subjectId !== 'string' || !summary.subjectId
    || typeof summary.affordanceId !== 'string' || !summary.affordanceId
    || summary.methodVersion !== 'metheus-affordance-trial-summary/0.2.0'
    || typeof summary.deliveryMode !== 'string' || !summary.deliveryMode
    || typeof summary.intendedFunction !== 'string' || !summary.intendedFunction
    || typeof summary.roleFrame !== 'string' || !summary.roleFrame
    || !Array.isArray(inputIds) || inputIds.length === 0
    || new Set(inputIds).size !== inputIds.length
    || inputIds.some((id) => typeof id !== 'string' || !id)
    || !Array.isArray(summary.lifecycleEvents) || summary.lifecycleEvents.length === 0
    || !Array.isArray(summary.lifecycleTemporalRelations)
    || !Array.isArray(summary.experienceReports)
    || !Array.isArray(summary.eventReportTemporalRelations)
    || !Array.isArray(summary.limitations) || summary.limitations.length === 0
    || summary.limitations.some((item) => typeof item !== 'string' || !item)
  ) return false;
  const eventIds = summary.lifecycleEvents.map((event) => event?.recordId);
  const reportIds = summary.experienceReports.map((report) => report?.recordId);
  if (
    new Set(eventIds).size !== eventIds.length
    || new Set(reportIds).size !== reportIds.length
    || eventIds.some((id) => typeof id !== 'string' || !inputIds.includes(id))
    || reportIds.some((id) => typeof id !== 'string' || !inputIds.includes(id))
    || new Set([...eventIds, ...reportIds]).size !== inputIds.length
    || inputIds.some((id) => ![...eventIds, ...reportIds].includes(id))
    || summary.lifecycleEvents.some((event) =>
      !lifecycleKinds.has(event?.lifecycleEvent)
      || !isTrialSummaryTime(event?.time)
      || !(event.epistemicClass === null || typeof event.epistemicClass === 'string')
      || !(event.sourceKind === null || typeof event.sourceKind === 'string')
    )
    || summary.experienceReports.some((report) =>
      !['observation', 'event'].includes(report?.recordType)
      || !(report.eventType === null || typeof report.eventType === 'string')
      || !(report.domain === null || typeof report.domain === 'string')
      || !(report.label === null || typeof report.label === 'string')
      || !isTrialSummaryTime(report.time)
      || !(report.epistemicClass === null || typeof report.epistemicClass === 'string')
      || !(report.sourceKind === null || typeof report.sourceKind === 'string')
      || (report.value !== undefined && (!report.value || typeof report.value !== 'object' || Array.isArray(report.value)))
    )
  ) return false;
  const validRelation = (relation) =>
    relation && typeof relation === 'object'
    && relation.subjectId === summary.subjectId
    && typeof relation.leftRecordId === 'string' && inputIds.includes(relation.leftRecordId)
    && typeof relation.rightRecordId === 'string' && inputIds.includes(relation.rightRecordId)
    && temporalKinds.has(relation.temporalRelation)
    && (relation.elapsedGap === null || (typeof relation.elapsedGap === 'number' && Number.isFinite(relation.elapsedGap) && relation.elapsedGap >= 0))
    && Array.isArray(relation.limitations) && relation.limitations.every((item) => typeof item === 'string');
  return summary.lifecycleTemporalRelations.every((relation) =>
    validRelation(relation) && eventIds.includes(relation.leftRecordId) && eventIds.includes(relation.rightRecordId))
    && summary.eventReportTemporalRelations.every((relation) =>
      validRelation(relation) && eventIds.includes(relation.leftRecordId) && reportIds.includes(relation.rightRecordId));
}

function trialTimeLabel(time) {
  if (!time) return 'Time not recorded';
  return [time.observedAt || time.start || time.date || 'Time unavailable', time.timeZone, time.precision]
    .filter((part) => typeof part === 'string' && part).join(' · ');
}

function appendTrialList(host, entries, formatEntry) {
  host.replaceChildren();
  if (!entries.length) {
    const item = document.createElement('li');
    item.textContent = 'No records included.';
    host.append(item);
    return;
  }
  for (const entry of entries) {
    const item = document.createElement('li');
    item.textContent = formatEntry(entry);
    host.append(item);
  }
}

function displayAffordanceTrialSummary(summary) {
  $('#affordance-trial-heading').textContent = `Trial summary · ${summary.intendedFunction.replaceAll('_', ' ')}`;
  $('#affordance-trial-context').textContent = `${summary.deliveryMode.replaceAll('_', ' ')} · ${summary.roleFrame.replaceAll('_', ' ')} · ${summary.inputRecordIds.length} selected source records · ${summary.methodVersion}`;
  appendTrialList($('#affordance-trial-events'), summary.lifecycleEvents, (event) =>
    `${event.lifecycleEvent.replaceAll('_', ' ')} · ${trialTimeLabel(event.time)} · ${event.epistemicClass || 'epistemic source not stated'} · record ${event.recordId}`);
  appendTrialList($('#affordance-trial-reports'), summary.experienceReports, (report) => {
    const values = report.value ? Object.entries(report.value).map(([key, value]) => `${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`).join(' · ') : 'No value recorded';
    return `${report.label || 'Experience report'} · ${trialTimeLabel(report.time)} · ${report.epistemicClass || 'epistemic source not stated'} · ${values} · record ${report.recordId}`;
  });
  appendTrialList($('#affordance-trial-relations'), summary.eventReportTemporalRelations, (relation) =>
    `${relation.leftRecordId} ${relation.temporalRelation.replaceAll('_', ' ')} ${relation.rightRecordId}${relation.elapsedGap === null ? '' : ` · recorded gap ${relation.elapsedGap} ${relation.elapsedGapUnit}`}`);
  $('#affordance-trial-limit').textContent = summary.limitations.join(' ');
  $('#affordance-trial-results').hidden = false;
  $('#affordance-trial-clear').disabled = false;
}

function formatSeriesNumber(value, unit = '') {
  if (value === null || value === undefined) return 'Unavailable';
  return `${Number(value).toLocaleString()}${unit ? ` ${unit}` : ''}`;
}

function displayMeasurementSeriesSummary(summary) {
  $('#measurement-record-rows').replaceChildren();
  $('#measurement-record-results').hidden = true;
  const series = summary.measurementSeries;
  $('#measurement-series-heading').textContent = `${series.analyteOrSignal} · ${series.unit}`;
  $('#measurement-series-source').textContent = [
    `${series.epistemicClass} · ${series.sourceKind}`,
    series.sourceName,
    series.sourceMethod,
    `source version: ${series.sourceVersion}`,
    `method details: ${series.methodDetails}`,
    `device/assay: ${series.deviceOrAssay}`,
    `model: ${series.deviceModel}`,
    `algorithm: ${series.algorithmVersion}`,
    `specimen: ${series.specimen}`,
    `sensor: ${series.sensorLocation}`,
    `conditions: ${series.collectionConditions}`,
  ].join(' · ');
  const qualitySummary = summary.qualityFlags.length ? ` · flags: ${summary.qualityFlags.join(', ')}` : ' · no quality flags recorded';
  $('#measurement-series-summary').textContent = `${summary.window.startDate} to ${summary.window.endDate} · ${summary.nMeasurements} samples across ${summary.nDistinctMeasurementDates} dates · overall median ${formatSeriesNumber(summary.medianNumericValue, series.unit)} · MAD ${formatSeriesNumber(summary.medianAbsoluteDeviationValue, series.unit)} · range ${formatSeriesNumber(summary.minimumValue, series.unit)} to ${formatSeriesNumber(summary.maximumValue, series.unit)} · coverage ${summary.coverage.daysWithAtLeastOneRecord}/${summary.coverage.calendarDaysInWindow} days · ${summary.recordsWithQualityFlags} records with quality flags${qualitySummary} · ${describeUncertaintyMetadata(summary.uncertaintyMetadata)}`;
  const rows = $('#measurement-series-rows');
  rows.replaceChildren();
  for (const bucket of summary.timeBuckets) {
    const row = document.createElement('tr');
    const values = [
      `${bucket.startDate} – ${bucket.endDate}`,
      `${bucket.nMeasurements} samples · ${bucket.nDistinctMeasurementDates} dates`,
      `${formatSeriesNumber(bucket.medianValue, series.unit)} ± ${formatSeriesNumber(bucket.medianAbsoluteDeviationValue, series.unit)}`,
      `${formatSeriesNumber(bucket.minimumValue, series.unit)} – ${formatSeriesNumber(bucket.maximumValue, series.unit)}`,
      `${bucket.daysWithAtLeastOneRecord}/${bucket.inclusiveDays} days · ${(bucket.fractionOfDaysWithARecord * 100).toLocaleString()}%${bucket.qualityFlags.length ? ` · Flags: ${bucket.qualityFlags.join(', ')}` : ''}`,
      describeUncertaintyMetadata(bucket.uncertaintyMetadata),
    ];
    for (const value of values) {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.append(cell);
    }
    rows.append(row);
  }
  $('#measurement-series-limit').textContent = summary.limitations.join(' ');
  $('#measurement-series-results').hidden = false;
  $('#measurement-series-clear').disabled = false;
}

function validateMeasurementObservation(record) {
  const value = record?.value;
  const source = record?.source;
  const time = record?.time;
  const details = record?.measurementDetails;
  const primaryValues = ['number', 'text', 'boolean', 'category'].filter((key) => value?.[key] !== undefined);
  if (
    !record || !['observation', 'event', 'estimate'].includes(record.recordType)
    || typeof record.id !== 'string' || !record.id
    || typeof record.subjectId !== 'string' || !record.subjectId
    || typeof record.schemaVersion !== 'string' || !record.schemaVersion
    || typeof record.label !== 'string' || !record.label
    || typeof record.domain !== 'string' || !record.domain
    || !['measured', 'self_reported', 'caregiver_reported', 'clinician_reported', 'derived', 'symbolic', 'imported'].includes(record.epistemicClass)
    || !value || typeof value !== 'object' || Array.isArray(value)
    || primaryValues.length !== 1
    || (value.number !== undefined && (typeof value.number !== 'number' || !Number.isFinite(value.number)))
    || (value.text !== undefined && typeof value.text !== 'string')
    || (value.boolean !== undefined && typeof value.boolean !== 'boolean')
    || (value.category !== undefined && (typeof value.category !== 'string' || !value.category))
    || (value.unit !== undefined && typeof value.unit !== 'string')
    || !source || typeof source !== 'object'
    || !['sensor', 'laboratory', 'home_test', 'subject', 'caregiver', 'clinician', 'symbolic_system', 'algorithm', 'external_import', 'unknown'].includes(source.kind)
    || !time || typeof time !== 'object'
    || !['exact', 'approximate', 'date_only', 'unknown'].includes(time.precision)
    || !((typeof time.observedAt === 'string' && !Number.isNaN(Date.parse(time.observedAt)))
      || (typeof time.date === 'string' && isIsoCalendarDate(time.date))
      || (typeof time.start === 'string' && !Number.isNaN(Date.parse(time.start))))
    || !details || typeof details !== 'object' || Array.isArray(details)
    || !['analyteOrSignal', 'specimen', 'deviceOrAssay'].some((key) => typeof details[key] === 'string' && details[key])
    || ['analyteOrSignal', 'specimen', 'sensorLocation', 'deviceOrAssay', 'deviceModel', 'algorithmVersion', 'collectionConditions']
      .some((key) => details[key] !== undefined && typeof details[key] !== 'string')
  ) return false;
  if (record.domain === 'hormone_assay') {
    if (!['laboratory', 'home_test'].includes(source.kind) || record.epistemicClass !== 'measured') return false;
    if (source.kind === 'laboratory' && (typeof value.unit !== 'string' || !value.unit)) return false;
  }
  return true;
}

function measurementRecordsFromPayload(payload) {
  const records = Array.isArray(payload) ? payload
    : Array.isArray(payload?.records) ? payload.records
      : payload?.record ? [payload.record]
        : payload?.recordType ? [payload]
          : null;
  if (!records || records.length === 0 || records.length > 1_000) return null;
  const ids = records.map((record) => record?.id);
  const subjects = new Set(records.map((record) => record?.subjectId));
  if (new Set(ids).size !== ids.length || subjects.size !== 1 || !records.every(validateMeasurementObservation)) return null;
  return records;
}

function displayMeasurementObservations(records) {
  $('#measurement-series-rows').replaceChildren();
  $('#measurement-series-results').hidden = true;
  $('#measurement-record-rows').replaceChildren();
  for (const record of records) {
    const row = document.createElement('tr');
    const timestamp = record.time.observedAt || record.time.date || record.time.start || 'Time unavailable';
    const result = record.value.category !== undefined
      ? `Category: ${record.value.category}`
      : record.value.text !== undefined
        ? `Text: ${record.value.text}`
        : record.value.boolean !== undefined
          ? `Boolean: ${record.value.boolean}`
          : `${record.value.number}${record.value.unit ? ` ${record.value.unit}` : ''}`;
    const details = record.measurementDetails;
    const sourceText = [record.source.kind, record.source.name, record.source.method, record.source.version]
      .filter((value) => typeof value === 'string' && value).join(' · ');
    const analyteText = [details.analyteOrSignal, `specimen: ${details.specimen || 'unspecified'}`, `test/device: ${details.deviceOrAssay || 'unspecified'}`]
      .filter(Boolean).join(' · ');
    const uncertaintyText = [details.collectionConditions, record.uncertainty?.notes, record.notes]
      .filter((value) => typeof value === 'string' && value).join(' · ') || 'No additional context recorded';
    for (const text of [timestamp, result, analyteText, sourceText || 'Source not specified', uncertaintyText]) {
      const cell = document.createElement('td');
      cell.textContent = text;
      row.append(cell);
    }
    $('#measurement-record-rows').append(row);
  }
  $('#measurement-record-results').hidden = false;
}

if (measurementSeriesFileInput) {
  const status = $('#measurement-series-status');
  const rows = $('#measurement-series-rows');
  const clearView = () => {
    rows.replaceChildren();
    $('#measurement-record-rows').replaceChildren();
    $('#measurement-series-results').hidden = true;
    $('#measurement-record-results').hidden = true;
    $('#measurement-series-clear').disabled = true;
  };
  $('#measurement-series-preview').addEventListener('click', () => {
    if (!validateMeasurementSeriesSummary(measurementSeriesExample)) {
      clearView();
      status.textContent = 'The bundled synthetic measurement-series example is invalid.';
      return;
    }
    displayMeasurementSeriesSummary(measurementSeriesExample);
    status.textContent = 'Synthetic example loaded in this tab. It contains no personal data.';
  });
  $('#measurement-record-preview').addEventListener('click', () => {
    if (!validateMeasurementObservation(urinaryLhExample)) {
      clearView();
      status.textContent = 'The bundled synthetic qualitative home-test example is invalid.';
      return;
    }
    displayMeasurementObservations([urinaryLhExample]);
    status.textContent = 'Synthetic example loaded in this tab. It shows one qualitative category and contains no personal data.';
    $('#measurement-series-clear').disabled = false;
  });
  measurementSeriesFileInput.addEventListener('change', async () => {
    const file = measurementSeriesFileInput.files?.[0];
    if (!file) return;
    if (file.size > 1_000_000) {
      clearView();
      status.textContent = 'This summary file is larger than 1 MB. Choose a smaller, explicitly selected summary.';
      measurementSeriesFileInput.value = '';
      return;
    }
    try {
      const parsed = JSON.parse(await file.text());
      const summary = parsed?.summary || parsed;
      if (validateMeasurementSeriesSummary(summary)) {
        displayMeasurementSeriesSummary(summary);
        status.textContent = `Loaded a descriptive summary for ${summary.nMeasurements} numeric samples in this tab only. The file has not been shared with your circle or Mētheus AI.`;
      } else {
        const records = measurementRecordsFromPayload(parsed);
        if (!records) throw new Error('invalid measurement payload');
        displayMeasurementObservations(records);
        status.textContent = `Loaded ${records.length} selected measurement record${records.length === 1 ? '' : 's'} individually in this tab. Results have not been averaged or shared with your circle or Mētheus AI.`;
        $('#measurement-series-clear').disabled = false;
      }
    } catch {
      clearView();
      status.textContent = 'Could not read this file as a valid Metheus numeric measurement-series summary. No data was sent.';
    } finally {
      measurementSeriesFileInput.value = '';
    }
  });
  $('#measurement-series-clear').addEventListener('click', () => {
    clearView();
    status.textContent = 'Local measurement-series view cleared from this tab.';
  });
}

if (affordanceTrialFileInput) {
  const status = $('#affordance-trial-status');
  const clearView = () => {
    $('#affordance-trial-events').replaceChildren();
    $('#affordance-trial-reports').replaceChildren();
    $('#affordance-trial-relations').replaceChildren();
    $('#affordance-trial-results').hidden = true;
    $('#affordance-trial-clear').disabled = true;
  };
  $('#affordance-trial-preview').addEventListener('click', () => {
    if (!validateAffordanceTrialSummary(affordanceTrialExample)) {
      clearView();
      status.textContent = 'The bundled synthetic affordance-trial example is invalid.';
      return;
    }
    displayAffordanceTrialSummary(affordanceTrialExample);
    status.textContent = 'Synthetic example loaded in this tab. It contains no personal data.';
  });
  affordanceTrialFileInput.addEventListener('change', async () => {
    const file = affordanceTrialFileInput.files?.[0];
    if (!file) return;
    if (file.size > 1_000_000) {
      clearView();
      status.textContent = 'This summary file is larger than 1 MB. Choose a smaller, explicitly selected summary.';
      affordanceTrialFileInput.value = '';
      return;
    }
    try {
      const parsed = JSON.parse(await file.text());
      const summary = parsed?.summary || parsed;
      if (!validateAffordanceTrialSummary(summary)) throw new Error('invalid trial summary');
      displayAffordanceTrialSummary(summary);
      status.textContent = `Loaded a local summary for ${summary.experienceReports.length} experience report${summary.experienceReports.length === 1 ? '' : 's'}. The file was not shared with your circle or Mētheus AI.`;
    } catch {
      clearView();
      status.textContent = 'Could not read this file as a valid Metheus affordance-trial summary. No data was sent.';
    } finally {
      affordanceTrialFileInput.value = '';
    }
  });
  $('#affordance-trial-clear').addEventListener('click', () => {
    clearView();
    status.textContent = 'Local affordance-trial view cleared from this tab.';
  });
}

if (window.matchMedia('(max-width: 740px)').matches) bodygraphPanel.open = false;

function showBodygraphFallback(error) {
  const fallback = document.createElement('img');
  fallback.src = BODYGRAPH_REFERENCE_URL;
  fallback.alt = 'Generic BodyGraph reference. Three-dimensional interaction is unavailable in this browser.';
  $('#bodygraph-viewer').replaceChildren(fallback);
  $('#bodygraph-detail').textContent = 'The reference is shown without interactive 3D highlighting in this browser.';
  recentBodygraphMentions.length = 0;
  syncIndicator.textContent = `Connected · reference map unavailable (${getPlainBody(error)})`;
}

function ensureBodygraph() {
  if (bodygraph) return Promise.resolve(bodygraph);
  if (bodygraphLoadPromise) return bodygraphLoadPromise;
  const lifecycle = bodygraphLifecycle;
  let loading;
  loading = (async () => {
    let instance = null;
    try {
      const { mountBodygraph } = await import('./bodygraph.js');
      instance = await mountBodygraph();
      if (lifecycle !== bodygraphLifecycle || !session.client) {
        instance.dispose();
        return null;
      }
      bodygraph = instance;
      if (comparingGateMaps) bodygraph.highlightGateComparison([...selectedChartGates], [...selectedMetheusGates]);
      else if (selectedChartGates.size) bodygraph.highlightGates([...selectedChartGates]);
      else recentBodygraphMentions.forEach((message) => bodygraph.highlightFromText(message));
      recentBodygraphMentions.length = 0;
      return bodygraph;
    } catch (error) {
      instance?.dispose();
      if (lifecycle === bodygraphLifecycle && session.client) showBodygraphFallback(error);
      return null;
    } finally {
      if (bodygraphLoadPromise === loading) bodygraphLoadPromise = null;
    }
  })();
  bodygraphLoadPromise = loading;
  return loading;
}

bodygraphPanel.addEventListener('toggle', () => {
  if (bodygraphPanel.open && session.client) void ensureBodygraph();
});

function extractBodygraphMentions(text) {
  return [
    ...[...text.matchAll(/\bgate\s*#?\s*(\d{1,2})\b/gi)].map((match) => `Gate ${match[1]}`),
    ...[...text.matchAll(/\bchannel\s*#?\s*(\d{1,2})\s*[-–/]\s*(\d{1,2})\b/gi)].map((match) => `Channel ${match[1]}-${match[2]}`),
  ];
}

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  deferredInstall = event;
  $('#install-button').hidden = false;
});
$('#install-button').addEventListener('click', async () => {
  if (!deferredInstall) return;
  deferredInstall.prompt();
  await deferredInstall.userChoice;
  deferredInstall = null;
  $('#install-button').hidden = true;
});

if ('serviceWorker' in navigator) navigator.serviceWorker.register('/chat/sw.js', { scope: '/chat/' }).catch(() => {});

function setStatus(message, isError = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle('error', isError);
}

function safeText(parent, tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  parent.append(element);
  return element;
}

function describeSelectedGates(gates) {
  return gates.map((gateNumber) => {
    const entry = gateAiAffordances.find((candidate) => candidate.gateNumber === gateNumber);
    return entry ? `Gate ${gateNumber} · ${entry.title}` : `Gate ${gateNumber}`;
  }).join('; ');
}

function describeSelectedChannels(gates) {
  const selected = new Set(gates);
  const channels = new Set(gateAiAffordances
    .filter((entry) => selected.has(entry.gateNumber))
    .flatMap((entry) => entry.channelIds || []));
  return [...channels]
    .filter((id) => {
      const match = /^ch-(\d{1,2})-(\d{1,2})$/.exec(id);
      return match && selected.has(Number(match[1])) && selected.has(Number(match[2]));
    })
    .sort()
    .map((id) => `Channel ${id.slice(3).replace('-', '–')}`);
}

function updateMetheusProfileSummary() {
  const gates = [...selectedMetheusGates].sort((a, b) => a - b);
  const userGates = [...selectedChartGates].sort((a, b) => a - b);
  const sharedGates = userGates.filter((gate) => selectedMetheusGates.has(gate));
  const userChannels = new Set(describeSelectedChannels(userGates));
  const metheusChannels = new Set(describeSelectedChannels(gates));
  const sharedChannels = [...userChannels].filter((channel) => metheusChannels.has(channel));
  $('#metheus-profile-summary').textContent = gates.length
    ? `Configured Metheus prompt gates: ${describeSelectedGates(gates)}. Its complete channels: ${[...metheusChannels].join(', ') || 'none'}. Your complete channels: ${[...userChannels].join(', ') || 'none'}. Shared gates: ${sharedGates.length ? sharedGates.join(', ') : 'none'}; shared complete channels: ${sharedChannels.join(', ') || 'none'}.`
    : 'No Metheus gates selected. Choose “Add to Metheus map” on any gate card to create this local prompt profile.';
}

function clearGeneratedBodygraphPrompt() {
  $('#bodygraph-prompt-output').value = '';
  $('#bodygraph-prompt-output').hidden = true;
  $('#bodygraph-prompt-actions').hidden = true;
  $('#bodygraph-prompt-status').textContent = '';
}

function createGeneratedBodygraphPrompt() {
  if (!selectedChartGates.size || !gateAiTopology || !gateAiAffordanceCatalog) {
    $('#bodygraph-prompt-status').textContent = 'Select at least one gate and wait for the version-matched BodyGraph catalog before generating a prompt.';
    return '';
  }
  const prompt = generateBodygraphInputPrompt({
    userGates: [...selectedChartGates],
    metheusGates: [...selectedMetheusGates],
    topology: gateAiTopology,
    affordanceCatalog: gateAiAffordanceCatalog,
  });
  $('#bodygraph-prompt-output').value = prompt;
  $('#bodygraph-prompt-output').hidden = false;
  $('#bodygraph-prompt-actions').hidden = false;
  $('#bodygraph-prompt-status').textContent = prompt.includes('compact form')
    ? 'Generated a compact prompt to stay within the chat size limit. It includes every selected gate, complete channel, and defined center; per-gate activity descriptions are omitted from this prompt.'
    : 'Generated from the selected gates, their complete topology-defined channels and centers, and the current activity catalog. Review or edit the text after inserting it into chat.';
  return prompt;
}

async function showGateMapComparison() {
  if (!selectedChartGates.size || !selectedMetheusGates.size) {
    $('#ai-guide-status').textContent = 'Select at least one gate for your map and one for Metheus’s map before comparing them.';
    return;
  }
  const viewer = await ensureBodygraph();
  if (!viewer) return;
  comparingGateMaps = true;
  viewer.highlightGateComparison([...selectedChartGates], [...selectedMetheusGates]);
  $('#ai-guide-status').textContent = 'BodyGraph comparison shown: amber is your selected map, teal is Metheus’s local prompt profile, and violet marks shared gates or channels. This compares symbolic map structure only.';
}

function describeGateChannels(channelIds = []) {
  return channelIds.map((id) => {
    const match = /^ch-(\d{1,2})-(\d{1,2})$/.exec(id);
    return match ? `Channel ${match[1]}–${match[2]}` : id;
  }).join(' · ');
}

function getSelectedChannelActivities(gates) {
  const selected = new Set(gates);
  const channelIds = new Set(gateAiAffordances
    .filter((entry) => selected.has(entry.gateNumber))
    .flatMap((entry) => entry.channelIds || []));
  return [...channelIds].sort().flatMap((channelId) => {
    const match = /^ch-(\d{1,2})-(\d{1,2})$/.exec(channelId);
    if (!match) return [];
    const [gateA, gateB] = match.slice(1).map(Number);
    if (!selected.has(gateA) || !selected.has(gateB)) return [];
    const entryA = gateAiAffordances.find((entry) => entry.gateNumber === gateA);
    const entryB = gateAiAffordances.find((entry) => entry.gateNumber === gateB);
    return entryA && entryB ? [{ channelId, entries: [entryA, entryB] }] : [];
  });
}

function getComplementaryActivities(gates) {
  const selected = new Set(gates);
  const candidates = new Map();
  for (const gateNumber of selected) {
    const source = gateAiAffordances.find((entry) => entry.gateNumber === gateNumber);
    for (const channelId of source?.channelIds || []) {
      const match = /^ch-(\d{1,2})-(\d{1,2})$/.exec(channelId);
      if (!match) continue;
      const [gateA, gateB] = match.slice(1).map(Number);
      const otherGate = gateA === gateNumber ? gateB : gateA;
      if (selected.has(otherGate)) continue;
      const complement = gateAiAffordances.find((entry) => entry.gateNumber === otherGate);
      if (complement) candidates.set(`${channelId}:${otherGate}`, { channelId, ...complement });
    }
  }
  return [...candidates.values()].sort((a, b) => {
    const gatesA = a.channelId.slice(3).split('-').map(Number);
    const gatesB = b.channelId.slice(3).split('-').map(Number);
    return gatesA[0] - gatesB[0] || gatesA[1] - gatesB[1];
  });
}

function renderGateAiIdeas() {
  const host = $('#gate-ai-idea-list');
  if (!host) return;
  const query = $('#gate-ai-filter').value.trim().toLocaleLowerCase();
  const matches = gateAiAffordances.filter((entry) => [
    `gate ${entry.gateNumber}`, entry.title, entry.centerId, CENTER_LABELS[entry.centerId], entry.aiAffordance, entry.examplePrompt,
    ...(entry.channelIds || []), ...(entry.interactionModes || []),
  ].join(' ').toLocaleLowerCase().includes(query));
  host.replaceChildren();
  $('#gate-ai-count').textContent = `${matches.length} of ${gateAiAffordances.length} gate ideas shown. Activities are optional and can be used without a chart.`;
  const selection = $('#gate-ai-selection');
  updateMetheusProfileSummary();
  selection.hidden = selectedChartGates.size === 0;
  if (selectedChartGates.size) {
    const numbers = [...selectedChartGates].sort((a, b) => a - b);
    const channels = describeSelectedChannels(numbers);
    const pairedActivities = getSelectedChannelActivities(numbers);
    const complements = getComplementaryActivities(numbers);
    const activeEntries = numbers
      .map((gateNumber) => gateAiAffordances.find((entry) => entry.gateNumber === gateNumber))
      .filter(Boolean);
    const channelSummary = channels.length
      ? `Together, these selected gates complete ${channels.join(', ')} in this symbolic map.`
      : 'This selection does not include both gates of a channel.';
    $('#gate-ai-selected-summary').textContent = `Selected self-reported gates: ${describeSelectedGates(numbers)}. ${channelSummary} Choose “Use this idea with selected gates” to prepare a chart-aware request.`;
    const activeDetails = $('#gate-ai-active-activities');
    const activeList = $('#gate-ai-active-list');
    activeDetails.hidden = activeEntries.length === 0;
    $('#gate-ai-active-summary').textContent = `Activities the AI may draw on · ${activeEntries.length}`;
    activeList.replaceChildren();
    for (const entry of activeEntries) {
      const item = document.createElement('li');
      safeText(item, 'strong', `Gate ${entry.gateNumber} · ${entry.title}`);
      safeText(item, 'span', entry.aiAffordance);
      activeList.append(item);
    }
    const pairedDetails = $('#gate-ai-complete-channels');
    const pairedList = $('#gate-ai-complete-channel-list');
    pairedDetails.hidden = pairedActivities.length === 0;
    $('#gate-ai-complete-channels-summary').textContent = `Paired activities in complete channels · ${pairedActivities.length}`;
    pairedList.replaceChildren();
    for (const channel of pairedActivities) {
      const item = document.createElement('li');
      safeText(item, 'strong', `Channel ${channel.channelId.slice(3).replace('-', '–')}`);
      safeText(item, 'span', channel.entries.map((entry) => `Gate ${entry.gateNumber} · ${entry.title}: ${entry.aiAffordance}`).join(' '));
      pairedList.append(item);
    }
    const complementDisclosure = $('#gate-ai-complements');
    const complementList = $('#gate-ai-complement-list');
    complementDisclosure.hidden = complements.length === 0;
    $('#gate-ai-complements-summary').textContent = `Possible channel complements · ${complements.length}`;
    complementList.replaceChildren();
    for (const complement of complements) {
      const item = document.createElement('li');
      safeText(item, 'strong', `Channel ${complement.channelId.slice(3).replace('-', '–')} · Gate ${complement.gateNumber} · ${complement.title}`);
      safeText(item, 'span', complement.aiAffordance);
      complementList.append(item);
    }
  } else {
    $('#gate-ai-complete-channels').hidden = true;
    $('#gate-ai-complements').hidden = true;
  }
  for (const entry of matches) {
    const card = document.createElement('article');
    card.className = 'gate-ai-card';
    safeText(card, 'h3', `Gate ${entry.gateNumber} · ${entry.title}`);
    safeText(card, 'p', `Symbolic map · ${CENTER_LABELS[entry.centerId] || entry.centerId} · ${describeGateChannels(entry.channelIds)}`, 'gate-ai-context');
    safeText(card, 'p', entry.aiAffordance);
    const modeLabels = (entry.interactionModes || []).map((mode) => mode.replace(/^./, (letter) => letter.toLocaleUpperCase()));
    if (modeLabels.length) safeText(card, 'p', `AI activity style: ${modeLabels.join(' · ')}`, 'gate-ai-modes');
    safeText(card, 'p', `Try asking: “${entry.examplePrompt}”`, 'gate-ai-prompt');
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'gate-ai-use';
    button.dataset.gateAiPrompt = entry.examplePrompt;
    button.textContent = 'Use as a regular AI question';
    card.append(button);
    const selectButton = document.createElement('button');
    selectButton.type = 'button';
    selectButton.className = 'gate-ai-select';
    selectButton.dataset.gateAiSelect = String(entry.gateNumber);
    selectButton.setAttribute('aria-pressed', String(selectedChartGates.has(entry.gateNumber)));
    selectButton.textContent = selectedChartGates.has(entry.gateNumber) ? 'Remove from my gates' : 'Add to my gates';
    card.append(selectButton);
    const metheusButton = document.createElement('button');
    metheusButton.type = 'button';
    metheusButton.className = 'gate-ai-select metheus-gate-select';
    metheusButton.dataset.metheusGateSelect = String(entry.gateNumber);
    metheusButton.setAttribute('aria-pressed', String(selectedMetheusGates.has(entry.gateNumber)));
    metheusButton.textContent = selectedMetheusGates.has(entry.gateNumber) ? 'Remove from Metheus map' : 'Add to Metheus map';
    card.append(metheusButton);
    const trialButton = document.createElement('button');
    trialButton.type = 'button';
    trialButton.className = 'gate-ai-trial';
    trialButton.dataset.gateAiTrial = String(entry.gateNumber);
    trialButton.textContent = 'Record trying this activity';
    card.append(trialButton);
    if (selectedChartGates.size) {
      const chartButton = document.createElement('button');
      chartButton.type = 'button';
      chartButton.className = 'gate-ai-chart-use';
      chartButton.dataset.gateAiChartPrompt = entry.examplePrompt;
      chartButton.textContent = 'Use this idea with selected gates';
      card.append(chartButton);
    }
    host.append(card);
  }
}

async function loadGateAiIdeas() {
  try {
    const [catalogResponse, bodygraphResponse] = await Promise.all([
      fetch(GATE_AI_AFFORDANCES_URL, { cache: 'force-cache' }),
      fetch(BODYGRAPH_REFERENCE_URL, { cache: 'force-cache' }),
    ]);
    if (!catalogResponse.ok || !bodygraphResponse.ok) throw new Error('reference catalog unavailable');
    const catalog = await catalogResponse.json();
    const bodygraphMarkup = await bodygraphResponse.text();
    const bodygraphDocument = new DOMParser().parseFromString(bodygraphMarkup, 'image/svg+xml');
    const bodygraphRoot = bodygraphDocument.documentElement;
    if (
      bodygraphDocument.querySelector('parsererror')
      || bodygraphRoot.localName !== 'svg'
      || bodygraphRoot.querySelector('script')
    ) throw new Error('bodygraph reference invalid');
    const svgGateNodes = [...bodygraphRoot.querySelectorAll('.gate[data-gate]')];
    const svgGates = new Map(svgGateNodes
      .map((gate) => [Number(gate.getAttribute('data-gate')), gate.getAttribute('data-center')]));
    const svgChannels = new Map();
    let svgChannelDataValid = true;
    const svgChannelNodes = [...bodygraphRoot.querySelectorAll('.channel-group')];
    for (const channel of svgChannelNodes) {
      const gateA = Number(channel.getAttribute('data-from'));
      const gateB = Number(channel.getAttribute('data-to'));
      const channelId = `ch-${gateA}-${gateB}`;
      const declaredPair = channel.getAttribute('data-channel');
      if (
        !channel.hasAttribute('data-from') || !channel.hasAttribute('data-to')
        || !channel.hasAttribute('data-channel')
        || !Number.isInteger(gateA) || gateA < 1 || gateA > 64
        || !Number.isInteger(gateB) || gateB < 1 || gateB > 64
        || gateA === gateB
        || declaredPair !== `${gateA}-${gateB}`
        || svgChannels.has(channelId)
      ) {
        svgChannelDataValid = false;
        continue;
      }
      svgChannels.set(channelId, new Set([gateA, gateB]));
    }
    const svgTopologyValid = bodygraphRoot.getAttribute('data-topology-catalog-id') === 'human-design-bodygraph-topology-v1'
      && Boolean(bodygraphRoot.getAttribute('data-topology-version')?.trim())
      && svgGateNodes.length === 64
      && svgGates.size === 64
      && [...svgGates].every(([number, center]) => Number.isInteger(number) && number >= 1 && number <= 64 && BODYGRAPH_CENTERS.has(center))
      && svgChannelNodes.length === 36
      && svgChannels.size === 36
      && svgChannelDataValid;
    const entryNumbers = Array.isArray(catalog.entries) ? catalog.entries.map((entry) => entry?.gateNumber) : [];
    const entryShapeValid = Array.isArray(catalog.entries) && catalog.entries.every((entry) => {
      if (
        !Number.isInteger(entry?.gateNumber)
        || entry.gateNumber < 1 || entry.gateNumber > 64
        || typeof entry.title !== 'string' || !entry.title.trim()
        || !BODYGRAPH_CENTERS.has(entry.centerId)
        || typeof entry.aiAffordance !== 'string' || !entry.aiAffordance.trim()
        || typeof entry.examplePrompt !== 'string' || !entry.examplePrompt.trim()
        || svgGates.get(entry.gateNumber) !== entry.centerId
        || !Array.isArray(entry.channelIds) || !entry.channelIds.length
        || new Set(entry.channelIds).size !== entry.channelIds.length
      ) return false;
      return entry.channelIds.every((id) => {
        if (typeof id !== 'string') return false;
        const match = /^ch-(\d{1,2})-(\d{1,2})$/.exec(id);
        return match
          && Number(match[1]) !== Number(match[2])
          && id === `ch-${Number(match[1])}-${Number(match[2])}`
          && [Number(match[1]), Number(match[2])].includes(entry.gateNumber);
      });
    });
    const channelToGates = new Map();
    if (entryShapeValid) {
      for (const entry of catalog.entries) {
        for (const channelId of entry.channelIds) {
          if (!channelToGates.has(channelId)) channelToGates.set(channelId, new Set());
          channelToGates.get(channelId).add(entry.gateNumber);
        }
      }
    }
    const channelPairsValid = entryShapeValid
      && channelToGates.size === 36
      && [...channelToGates].every(([id, gates]) => {
        const match = /^ch-(\d{1,2})-(\d{1,2})$/.exec(id);
        const svgGatePair = svgChannels.get(id);
        return match && gates.size === 2
          && gates.has(Number(match[1])) && gates.has(Number(match[2]))
          && svgGatePair?.has(Number(match[1])) && svgGatePair?.has(Number(match[2]));
      });
    if (
      catalog.catalogId !== 'metheus-gate-ai-affordances-v1'
      || typeof catalog.version !== 'string' || !catalog.version.trim()
      || !svgTopologyValid
      || catalog.topologyVersion !== bodygraphRoot.getAttribute('data-topology-version')
      || catalog.topologyCatalogId !== 'human-design-bodygraph-topology-v1'
      || !Array.isArray(catalog.entries)
      || catalog.entries.length !== 64
      || new Set(entryNumbers).size !== 64
      || !Array.from({ length: 64 }, (_, index) => index + 1).every((gateNumber) => entryNumbers.includes(gateNumber))
      || !entryShapeValid
      || !channelPairsValid
      || catalog.entries.some((entry) =>
        !Array.isArray(entry?.interactionModes)
        || entry.interactionModes.length === 0
        || new Set(entry.interactionModes).size !== entry.interactionModes.length
        || entry.interactionModes.some((mode) => !INTERACTION_MODES.has(mode))
      )
    ) {
      throw new Error('catalog invalid');
    }
    gateAiAffordances = catalog.entries;
    gateAiAffordanceCatalogVersion = catalog.version;
    gateAiAffordanceCatalog = catalog;
    gateAiTopology = {
      catalogId: 'human-design-bodygraph-topology-v1',
      version: bodygraphRoot.getAttribute('data-topology-version'),
      gates: catalog.entries.map((entry) => ({
        number: entry.gateNumber,
        title: entry.title,
        centerId: entry.centerId,
        channelIds: entry.channelIds,
      })),
      channels: [...svgChannels].map(([id]) => {
        const [gateA, gateB] = id.slice(3).split('-').map(Number);
        return {
          id,
          gateA,
          gateB,
          centerA: svgGates.get(gateA),
          centerB: svgGates.get(gateB),
        };
      }),
    };
    renderGateAiIdeas();
  } catch {
    $('#gate-ai-count').textContent = 'The gate activity catalog could not be loaded. You can still ask Mētheus AI without chart context.';
  }
}

$('#gate-ai-filter').addEventListener('input', renderGateAiIdeas);
$('#generate-bodygraph-prompt').addEventListener('click', () => {
  try { createGeneratedBodygraphPrompt(); }
  catch (error) { $('#bodygraph-prompt-status').textContent = `Prompt could not be generated · ${getPlainBody(error)}`; }
});

$('#copy-bodygraph-prompt').addEventListener('click', async () => {
  const prompt = $('#bodygraph-prompt-output').value;
  if (!prompt) return;
  try {
    await navigator.clipboard.writeText(prompt);
    $('#bodygraph-prompt-status').textContent = 'Prompt copied. It remains in this browser until you choose where to paste it.';
  } catch {
    $('#bodygraph-prompt-status').textContent = 'Clipboard access is unavailable. Select the generated prompt above and copy it manually.';
  }
});

$('#use-bodygraph-prompt').addEventListener('click', () => {
  if (!session.client || !session.roomId || !session.encrypted) {
    $('#bodygraph-prompt-status').textContent = 'Choose a protected circle before sending a question to Mētheus.';
    return;
  }
  let prompt = $('#bodygraph-prompt-output').value;
  if (!prompt) {
    try { prompt = createGeneratedBodygraphPrompt(); }
    catch (error) { $('#bodygraph-prompt-status').textContent = `Prompt could not be generated · ${getPlainBody(error)}`; return; }
  }
  if (!prompt) return;
  const userGates = [...selectedChartGates].sort((a, b) => a - b);
  const metheusGates = [...selectedMetheusGates].sort((a, b) => a - b);
  if (!userGates.length) {
    $('#bodygraph-prompt-status').textContent = 'Choose at least one marker on your BodyGraph first.';
    return;
  }
  pendingChartPromptMode = metheusGates.length ? 'both' : 'chart';
  $('#ask-metheus').checked = true;
  messageInput.value = `${prompt}\n\nQuestion: `;
  messageInput.focus();
  messageInput.style.height = 'auto';
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 160)}px`;
  $('#bodygraph-prompt-status').textContent = 'Prompt ready. Add your question; your selected design context will be included for this reply only.';
});

$('#gate-ai-idea-list').addEventListener('click', (event) => {
  const metheusButton = event.target.closest('[data-metheus-gate-select]');
  if (metheusButton) {
    const gateNumber = Number(metheusButton.dataset.metheusGateSelect);
    if (selectedMetheusGates.has(gateNumber)) selectedMetheusGates.delete(gateNumber);
    else selectedMetheusGates.add(gateNumber);
    clearGeneratedBodygraphPrompt();
    saveMetheusGateProfile();
    if (comparingGateMaps) bodygraph?.highlightGateComparison([...selectedChartGates], [...selectedMetheusGates]);
    renderGateAiIdeas();
    return;
  }
  const gateButton = event.target.closest('[data-gate-ai-select]');
  if (gateButton) {
    const gateNumber = Number(gateButton.dataset.gateAiSelect);
    if (selectedChartGates.has(gateNumber)) selectedChartGates.delete(gateNumber);
    else selectedChartGates.add(gateNumber);
    clearGeneratedBodygraphPrompt();
    if (comparingGateMaps) bodygraph?.highlightGateComparison([...selectedChartGates], [...selectedMetheusGates]);
    else bodygraph?.highlightGates([...selectedChartGates]);
    renderGateAiIdeas();
    return;
  }
  const trialButton = event.target.closest('[data-gate-ai-trial]');
  if (trialButton) {
    const gateNumber = Number(trialButton.dataset.gateAiTrial);
    pendingGateTrial = gateAiAffordances.find((entry) => entry.gateNumber === gateNumber) || null;
    const form = $('#gate-trial-form');
    if (!pendingGateTrial || !form) return;
    $('#gate-trial-title').textContent = `Record trying Gate ${gateNumber}'s optional activity`;
    $('#gate-trial-status').textContent = '';
    $('#gate-trial-date').value = new Date(Date.now() - new Date().getTimezoneOffset() * 60_000).toISOString().slice(0, 10);
    form.hidden = false;
    form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    $('#gate-trial-subject').focus();
    return;
  }
  const button = event.target.closest('[data-gate-ai-prompt]');
  const chartButton = event.target.closest('[data-gate-ai-chart-prompt]');
  if (!button && !chartButton) return;
  const prompt = chartButton?.dataset.gateAiChartPrompt || button.dataset.gateAiPrompt;
  const gates = [...selectedChartGates].sort((a, b) => a - b);
  pendingChartPromptMode = chartButton ? 'chart' : 'ask';
  $('#ask-metheus').checked = true;
  messageInput.value = prompt;
  messageInput.focus();
  messageInput.setSelectionRange(messageInput.value.length, messageInput.value.length);
  messageInput.style.height = 'auto';
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 160)}px`;
  $('#ai-guide-status').textContent = chartButton
    ? 'The example is ready. Your selected design markers and question will be shared with Mētheus AI for this reply only.'
    : 'The example is ready. Review your question, then choose “Ask Mētheus” when you are ready.';
});

$('#gate-trial-cancel').addEventListener('click', () => {
  pendingGateTrial = null;
  $('#gate-trial-form').hidden = true;
  $('#gate-trial-form').reset();
  $('#gate-trial-status').textContent = '';
});

$('#gate-trial-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const entry = pendingGateTrial;
  const subjectId = $('#gate-trial-subject').value.trim();
  const usedDate = $('#gate-trial-date').value;
  if (!entry || !subjectId || !isIsoCalendarDate(usedDate)) {
    $('#gate-trial-status').textContent = 'Choose an activity, enter a pseudonymous participant label, and provide a valid use date.';
    return;
  }
  const now = new Date();
  const timestamp = now.toISOString();
  const nonce = crypto.randomUUID();
  const affordanceId = `ai-affordance-${nonce}`;
  const records = [{
    id: `ai-affordance-use-${nonce}`,
    subjectId,
    recordType: 'event',
    schemaVersion: '0.2',
    eventType: 'environmental_affordance',
    epistemicClass: 'self_reported',
    time: { date: usedDate, timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone, precision: 'date_only', scale: 'daily' },
    source: { kind: 'subject', reportedByRelation: 'self', name: 'Metheus PWA local record composer', version: '1' },
    domain: 'environment',
    label: 'Self-reported use of an optional AI activity',
    environmentalAffordance: {
      affordanceId,
      deliveryMode: 'conversational_ai',
      intendedFunction: $('#gate-trial-function').value,
      lifecycleEvent: 'used',
      roleFrame: 'tool_or_scaffold',
      aiDisclosures: { identity: 'not_observed', privacyBoundaries: 'not_observed', roleBoundaries: 'not_observed' },
    },
    contextTags: ['metheus_gate_ai_affordance', `catalog_version:${gateAiAffordanceCatalogVersion}`],
    privacy: { sensitivity: 'personal', subjectControlled: true, sharing: 'private' },
    createdAt: timestamp,
    notes: 'Self-reported activity use. This record does not contain an AI transcript or assert gate activation, channel completion, or physiological effect.',
  }];
  const includeSymbolic = $('#gate-trial-include-symbolic').checked;
  if (includeSymbolic) {
    records[0].contextTags.push(`human_design_gate:${entry.gateNumber}`, ...entry.channelIds.map((id) => `human_design_${id}`));
  }
  const response = $('#gate-trial-response').value;
  const notes = $('#gate-trial-notes').value.trim();
  if (response || notes) {
    const report = {
      id: `ai-affordance-report-${nonce}`,
      subjectId,
      recordType: 'observation',
      schemaVersion: '0.2',
      eventType: 'other',
      epistemicClass: 'self_reported',
      time: { observedAt: timestamp, timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone, precision: 'exact', scale: 'instant' },
      source: { kind: 'subject', reportedByRelation: 'self', name: 'Metheus PWA local record composer', version: '1' },
      domain: 'environment',
      label: 'Self-reported experience after an optional AI activity',
      relatedAffordanceIds: [affordanceId],
      privacy: { sensitivity: 'personal', subjectControlled: true, sharing: 'private' },
      createdAt: timestamp,
      notes: 'A subjective report only; it does not establish benefit, harm, causation, a hormone change, or gate activation.',
    };
    if (response) report.value = { category: response };
    if (notes) report.value = { ...(report.value || {}), text: notes };
    if (includeSymbolic) report.contextTags = [`human_design_gate:${entry.gateNumber}`, ...entry.channelIds.map((id) => `human_design_${id}`)];
    records.push(report);
  }
  const blob = new Blob([JSON.stringify(records, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `metheus-ai-affordance-${now.toISOString().slice(0, 10)}.json`;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('#gate-trial-status').textContent = `Downloaded ${records.length} self-reported record${records.length === 1 ? '' : 's'}. The file stays on your device unless you choose to share it.`;
  pendingGateTrial = null;
  $('#gate-trial-form').hidden = true;
  $('#gate-trial-form').reset();
});

$('#gate-ai-clear').addEventListener('click', () => {
  selectedChartGates.clear();
  clearGeneratedBodygraphPrompt();
  if (comparingGateMaps) bodygraph?.highlightGateComparison([], [...selectedMetheusGates]);
  else bodygraph?.highlightGates([]);
  renderGateAiIdeas();
});

$('#metheus-profile-clear').addEventListener('click', () => {
  selectedMetheusGates.clear();
  clearGeneratedBodygraphPrompt();
  saveMetheusGateProfile();
  if (comparingGateMaps) bodygraph?.highlightGateComparison([...selectedChartGates], []);
  renderGateAiIdeas();
});

$('#metheus-profile-compare').addEventListener('click', showGateMapComparison);

function displayEvent(event) {
  if (!event || event.getType() !== 'm.room.message') return;
  const content = event.getContent();
  if (!['m.text', 'm.notice'].includes(content?.msgtype) || typeof content.body !== 'string') return;
  const id = event.getId() || `${event.getSender()}-${event.getTs()}-${content.body}`;
  if (session.seen.has(id)) return;
  session.seen.add(id);
  const mine = event.getSender() === session.userId;
  const message = presentConversationMessage(content.body, mine);
  if (!message) return;
  $('#welcome-card').hidden = true;
  const article = document.createElement('article');
  article.className = `message ${mine ? 'message-mine' : ''}`;
  safeText(article, 'p', mine ? 'You' : (event.sender?.name || 'Circle member'), 'message-sender');
  safeText(article, 'p', message.text, 'message-body');
  safeText(article, 'time', new Date(event.getTs()).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }), 'message-time');
  timeline.append(article);
  timeline.scrollTop = timeline.scrollHeight;
  const mentions = message.highlightText ? extractBodygraphMentions(message.highlightText) : [];
  if (bodygraph) mentions.forEach((mention) => bodygraph.highlightFromText(mention));
  else if (mentions.length) {
    recentBodygraphMentions.push(...mentions);
    if (recentBodygraphMentions.length > 80) recentBodygraphMentions.splice(0, recentBodygraphMentions.length - 80);
  }
}

function presentConversationMessage(body, mine = false) {
  const text = body.trim();
  if (text.startsWith('!metheus ask-chart ')) {
    const parsed = parseChartAsk(text.slice('!metheus ask-chart '.length));
    return { text: parsed.error ? 'Asked Mētheus using selected design context.' : `Asked Mētheus using selected design context: ${parsed.question}`, highlightText: parsed.error ? '' : parsed.question };
  }
  if (text.startsWith('!metheus ask ')) {
    const question = text.slice('!metheus ask '.length).trim();
    return { text: `Asked Mētheus: ${question}`, highlightText: question };
  }
  if (text.startsWith('!metheus chart-set ')) return { text: 'Updated personal design context.' };
  if (text === '!metheus chart-clear') return { text: 'Cleared personal design context.' };
  if (text === '!metheus chart-status') return null;
  if (text === '!metheus ai-info') return { text: 'Requested Mētheus AI information.' };
  if (text === '!metheus ai-status') return { text: 'Checked AI agreement for this circle.' };
  if (text === '!metheus ai-opt-in') return { text: 'Agreed to AI support in this circle.' };
  if (text === '!metheus ai-opt-out') return { text: 'Paused AI support in this circle.' };
  if (text.startsWith('!metheus ')) return { text: 'Sent a request to Mētheus.' };
  if (!mine) {
    if (/Metheus AI is optional\./i.test(text)) {
      return { text: 'Mētheus AI is optional. It replies only after everyone agrees. Regular messages are not sent to the AI service. Questions and any selected BodyGraph context are sent to the service for a reply; everyone in the circle can see them, and the service may retain content. Avoid sensitive personal details.' };
    }
    if (/If you understand and agree|choose “I agree to AI support/i.test(text)) {
      return { text: 'Read the AI agreement, then choose “I agree to AI support” in the app. Everyone chooses separately. You can include design context for one question, save it for later, clear it, or pause AI support.' };
    }
    if (/Your opt-in is recorded/i.test(text)) {
      return { text: 'Your agreement is saved. Mētheus AI will remain paused until everyone in the circle has agreed.' };
    }
    if (/chart-aware setting has been cleared from bot memory/i.test(text)) {
      return { text: 'Your saved BodyGraph context has been cleared.' };
    }
    if (/do not have a chart-aware setting stored in bot memory/i.test(text)) {
      return { text: 'You have not saved BodyGraph context for this circle.' };
    }
    if (/please keep each Metheus question under/i.test(text)) {
      return { text: 'Please shorten your question and try again.' };
    }
    if (/Metheus AI is inactive|will not process any room content/i.test(text)) {
      return { text: 'Mētheus AI is paused until everyone in the circle has read the agreement and agreed. No question was sent to the AI service.' };
    }
    if (/Every currently joined person has opted in|Every currently joined person has independently opted in/i.test(text)) {
      return { text: 'Everyone has agreed. Mētheus AI is ready for questions that people choose to send.' };
    }
    if (/AI processing is paused for this room/i.test(text)) {
      return { text: 'Mētheus AI is paused for this circle and its temporary conversation context has been cleared. A question already sent to the AI service cannot be recalled. Everyone must agree again to resume.' };
    }
    if (/Chart-aware mode is enabled|Your chart-aware setting/i.test(text)) {
      return { text: /enabled/i.test(text) ? 'Your selected BodyGraph context will accompany your questions in this circle until you clear it.' : 'Your saved BodyGraph context is not enabled in this circle.' };
    }
    if (/matrix|homeserver|m\.login\.|!metheus\s/i.test(text)) return { text: 'Mētheus updated a conversation setting.' };
  }
  return { text, highlightText: text };
}

function getPlainBody(error) {
  const message = String(error?.message || '').toLowerCase();
  if (message.includes('login') || message.includes('auth') || message.includes('token')) return 'Sign-in could not be completed. Please try again.';
  if (message.includes('encrypt') || message.includes('crypto')) return 'This circle is not ready for protected messaging. Ask its organizer for help.';
  if (message.includes('room') || message.includes('not found')) return 'That circle is not available to this account. Ask its organizer to add you.';
  if (message.includes('network') || message.includes('fetch') || message.includes('timeout')) return 'Connection was interrupted. Check your internet connection and try again.';
  return 'Something went wrong. Please try again or ask the circle organizer for help.';
}

function onceSyncReady(client, sdk) {
  return new Promise((resolve, reject) => {
    const onTimeout = () => {
      client.removeListener(sdk.ClientEvent.Sync, onSync);
      reject(new Error('The homeserver did not finish syncing in time.'));
    };
    const timeout = window.setTimeout(onTimeout, 30000);
    const onSync = (state, _previous, data) => {
      if (state === 'PREPARED' || state === 'SYNCING') {
        clearTimeout(timeout);
        client.removeListener(sdk.ClientEvent.Sync, onSync);
        resolve(data);
      }
    };
    client.on(sdk.ClientEvent.Sync, onSync);
  });
}

async function connectToMatrixRoom(login, roomInput) {
  const baseUrl = CASTALIA_HOMESERVER;
  const sdk = session.sdk || await import('matrix-js-sdk');
  session.sdk = sdk;
  const client = sdk.createClient({ baseUrl, accessToken: login.access_token, userId: login.user_id, deviceId: login.device_id, timelineSupport: true });
  try {
    await client.initRustCrypto();
    session.client = client;
    session.userId = login.user_id;
    session.roomId = roomInput?.trim() || null;
    client.on(sdk.RoomEvent.Timeline, (matrixEvent, room) => {
      if (!room || room.roomId !== session.roomId) return;
      matrixEvent.once('Event.decrypted', () => displayEvent(matrixEvent));
      displayEvent(matrixEvent);
    });
    const ready = onceSyncReady(client, sdk);
    client.startClient({ initialSyncLimit: 30 });
    await ready;
    client.on(sdk.ClientEvent.Sync, (state) => {
      if (state === 'SYNCING' || state === 'PREPARED') syncIndicator.textContent = 'Connected';
      else if (state === 'ERROR') syncIndicator.textContent = 'Reconnecting…';
    });
    if (!roomInput?.trim()) {
      showMatrixRoomPicker(login, client);
      return false;
    }
    let room = client.getRoom(roomInput);
    if (!room) room = await client.joinRoom(roomInput);
    if (!room) throw new Error('The circle is not available to this account. Ask its organizer to add you.');
    await openMatrixRoom(room, login);
    return true;
  } catch (error) {
    client.stopClient();
    session.client = null;
    session.userId = null;
    session.roomId = null;
    session.encrypted = false;
    recentBodygraphMentions.length = 0;
    throw error;
  }
}

function showMatrixRoomPicker(login, client) {
  const rooms = client.getRooms()
    .filter((room) => room.getMyMembership?.() === 'join')
    .sort((a, b) => (a.name || a.roomId).localeCompare(b.name || b.roomId));
  roomPickerSelect.replaceChildren();
  for (const room of rooms) {
    const option = document.createElement('option');
    option.value = room.roomId;
    option.textContent = room.name || 'Circle';
    roomPickerSelect.append(option);
  }
  roomPickerSelect.hidden = rooms.length === 0;
  $('#room-picker-open').disabled = rooms.length === 0;
  $('#room-picker-empty').hidden = rooms.length > 0;
  connectForm.hidden = true;
  roomPicker.hidden = false;
  syncIndicator.textContent = 'Connected';
  setStatus('You’re signed in. Choose your circle.');
}

async function openMatrixRoom(room, login) {
  const client = session.client;
  if (!room || !client) throw new Error('Sign in again before opening this circle.');
  session.roomId = room.roomId;
  const cryptoApi = client.getCrypto();
  session.encrypted = cryptoApi ? await cryptoApi.isEncryptionEnabledInRoom(room.roomId) : false;
  const liveEvents = room.getLiveTimeline()?.getEvents?.() || [];
  liveEvents.forEach(displayEvent);
  $('#room-title').textContent = room.name || 'The Hearth';
  $('#room-subtitle').textContent = `${room.getJoinedMembers().length} people · ${session.encrypted ? 'protected conversation' : 'private messaging unavailable'}`;
  messageInput.disabled = !session.encrypted;
  messageInput.placeholder = session.encrypted ? 'Write to your circle…' : 'Messaging is unavailable in this circle.';
  messageForm.querySelector('button').disabled = !session.encrypted;
  $('.composer-note').textContent = session.encrypted
    ? 'Messages are shared with everyone in this circle. Only messages marked “Ask Mētheus” are sent to the AI service.'
    : 'This circle is not set up for protected messaging. Sending is paused; ask its organizer for help.';
  connectPanel.hidden = true;
  conversation.hidden = false;
  $('#logout-button').hidden = false;
  $('#install-button').hidden = false;
  syncIndicator.textContent = 'Connected';
  await loadGateAiIdeas();
  if (bodygraphPanel.open) await ensureBodygraph();
}

async function exchangeCastaliaLoginToken(loginToken, roomInput) {
  const sdk = await import('matrix-js-sdk');
  session.sdk = sdk;
  const loginClient = sdk.createClient({ baseUrl: CASTALIA_HOMESERVER });
  const login = await loginClient.login('m.login.token', {
    token: loginToken,
    initial_device_display_name: 'Mētheus Circle PWA',
  });
  return connectToMatrixRoom(login, roomInput);
}

function createSsoState() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return [...bytes].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function startCastaliaSso(roomInput) {
  const state = createSsoState();
  sessionStorage.setItem(CASTALIA_SSO_TRANSACTION_KEY, JSON.stringify({ state, roomInput, createdAt: Date.now() }));
  const redirectUrl = new URL(window.location.pathname, window.location.origin);
  redirectUrl.searchParams.set('state', state);
  const ssoUrl = new URL(`/_matrix/client/v3/login/sso/redirect/${encodeURIComponent(CASTALIA_SSO_IDP)}`, CASTALIA_HOMESERVER);
  ssoUrl.searchParams.set('redirectUrl', redirectUrl.toString());
  setStatus('Opening Castalia.Institute sign-in…');
  window.location.assign(ssoUrl.toString());
}

async function handleCastaliaSsoCallback(callback) {
  if (callback.error) {
    sessionStorage.removeItem(CASTALIA_SSO_TRANSACTION_KEY);
    setStatus('Castalia sign-in was cancelled or could not be completed. Please try again.', true);
    return;
  }
  let transaction = null;
  try { transaction = JSON.parse(sessionStorage.getItem(CASTALIA_SSO_TRANSACTION_KEY) || 'null'); } catch { /* invalid pending login state */ }
  sessionStorage.removeItem(CASTALIA_SSO_TRANSACTION_KEY);
  if (
    !callback.loginToken || !callback.state || !transaction
    || callback.state !== transaction.state
    || !Number.isFinite(transaction.createdAt)
    || Date.now() - transaction.createdAt > 10 * 60 * 1000
    || (transaction.roomInput !== undefined && typeof transaction.roomInput !== 'string')
  ) {
    setStatus('This Castalia sign-in link is missing, expired, or does not match this browser session. Start sign-in again.', true);
    return;
  }
  const submit = connectForm.querySelector('button[type="submit"]');
  submit.disabled = true;
  setStatus('Finishing sign-in and opening your circles…');
  try {
    const roomOpened = await exchangeCastaliaLoginToken(callback.loginToken, transaction.roomInput || '');
    if (roomOpened) setStatus('Your circle is ready.');
    else setStatus('You’re signed in. Choose your circle.');
  } catch (error) {
    setStatus(getPlainBody(error), true);
  } finally {
    submit.disabled = false;
    callback.loginToken = null;
  }
}

connectForm.addEventListener('submit', (event) => {
  event.preventDefault();
  try {
    startCastaliaSso('');
  } catch (error) {
    setStatus(getPlainBody(error), true);
  }
});

$('#room-picker-open').addEventListener('click', async () => {
  const room = session.client?.getRoom(roomPickerSelect.value);
  if (!room) {
    setStatus('That circle is no longer available. Sign in again and choose another.', true);
    return;
  }
  try { await openMatrixRoom(room, { user_id: session.userId }); }
  catch (error) { setStatus(getPlainBody(error), true); }
});

$('#room-picker-switch-account').addEventListener('click', () => $('#logout-button').click());

messageForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const body = messageInput.value.trim();
  if (!body || !session.client || !session.roomId || !session.encrypted) return;
  const askMetheus = $('#ask-metheus').checked || pendingChartPromptMode !== 'ask';
  let outgoing = body;
  if (askMetheus) {
    try {
      if (pendingChartPromptMode === 'chart') {
        const gates = [...selectedChartGates].sort((a, b) => a - b);
        if (!gates.length) throw new Error('Choose at least one marker on your BodyGraph first.');
        outgoing = formatChartAsk(gates, body);
      } else if (pendingChartPromptMode === 'both') {
        const userGates = [...selectedChartGates].sort((a, b) => a - b);
        const metheusGates = [...selectedMetheusGates].sort((a, b) => a - b);
        if (!userGates.length || !metheusGates.length) throw new Error('Choose markers for both BodyGraphs first.');
        outgoing = formatChartAsk(userGates, body, metheusGates);
      } else {
        outgoing = `!metheus ask ${body}`;
      }
    } catch (error) {
      $('#ai-guide-status').textContent = error.message;
      return;
    }
  }
  const submit = messageForm.querySelector('button');
  submit.disabled = true;
  try {
    await session.client.sendTextMessage(session.roomId, outgoing);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    $('#ask-metheus').checked = false;
    pendingChartPromptMode = 'ask';
    $('#ai-guide-status').textContent = askMetheus
      ? 'Your question was shared with Mētheus AI. Its reply will appear here when available.'
      : 'Message shared with your circle.';
  } catch (error) {
    syncIndicator.textContent = getPlainBody(error);
  } finally {
    submit.disabled = false;
    messageInput.focus();
  }
});

const AI_ACTION_COMMANDS = {
  info: '!metheus ai-info',
  status: '!metheus ai-status',
  'opt-in': '!metheus ai-opt-in',
  'opt-out': '!metheus ai-opt-out',
  'chart-status': '!metheus chart-status',
  'chart-clear': '!metheus chart-clear',
};

document.querySelectorAll('[data-ai-action]').forEach((button) => {
  button.addEventListener('click', async () => {
    if (!session.client || !session.roomId || !session.encrypted) return;
    const command = AI_ACTION_COMMANDS[button.dataset.aiAction];
    if (!command) return;
    button.disabled = true;
    $('#ai-guide-status').textContent = 'Updating your circle’s AI choice…';
    try {
      await session.client.sendTextMessage(session.roomId, command);
      $('#ai-guide-status').textContent = 'Your choice was shared with the circle.';
    } catch (error) {
      $('#ai-guide-status').textContent = getPlainBody(error);
    } finally {
      button.disabled = false;
    }
  });
});

$('#ai-ask-chart-start').addEventListener('click', () => {
  if (!session.client || !session.roomId || !session.encrypted) return;
  const gates = [...selectedChartGates].sort((a, b) => a - b);
  if (!gates.length) {
    $('#ai-guide-status').textContent = 'Choose one or more markers on your BodyGraph first.';
    return;
  }
  pendingChartPromptMode = 'chart';
  $('#ask-metheus').checked = true;
  messageInput.value = '';
  messageInput.focus();
  $('#ai-guide-status').textContent = 'Your selected BodyGraph markers will be included with your next question only.';
});

$('#ai-ask-chart-profile-start').addEventListener('click', () => {
  if (!session.client || !session.roomId || !session.encrypted) return;
  const userGates = [...selectedChartGates].sort((a, b) => a - b);
  const metheusGates = [...selectedMetheusGates].sort((a, b) => a - b);
  if (!userGates.length || !metheusGates.length) {
    $('#ai-guide-status').textContent = 'Choose markers for both BodyGraphs first.';
    return;
  }
  pendingChartPromptMode = 'both';
  $('#ask-metheus').checked = true;
  messageInput.value = '';
  messageInput.focus();
  $('#ai-guide-status').textContent = 'Both selected BodyGraphs will be included with your next question only.';
});

$('#ai-chart-set-start').addEventListener('click', () => {
  if (!session.client || !session.roomId || !session.encrypted) return;
  const gates = [...selectedChartGates].sort((a, b) => a - b);
  if (!gates.length) {
    $('#ai-guide-status').textContent = 'Choose one or more markers on your BodyGraph first.';
    return;
  }
  const button = $('#ai-chart-set-start');
  button.disabled = true;
  session.client.sendTextMessage(session.roomId, formatChartSet(gates))
    .then(() => { $('#ai-guide-status').textContent = 'Your selected BodyGraph will be used for your future AI questions in this circle until you clear it.'; })
    .catch((error) => { $('#ai-guide-status').textContent = getPlainBody(error); })
    .finally(() => { button.disabled = false; });
});

messageInput.addEventListener('input', () => {
  messageInput.style.height = 'auto';
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 160)}px`;
});
messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    messageForm.requestSubmit();
  }
});

$('#logout-button').addEventListener('click', async () => {
  bodygraphLifecycle += 1;
  bodygraphLoadPromise = null;
  const client = session.client;
  if (client) {
    client.stopClient();
    try { await client.logout(); } catch { /* local disconnect still proceeds */ }
  }
  bodygraph?.dispose();
  bodygraph = null;
  recentBodygraphMentions.length = 0;
  session.client = null;
  session.sdk = null;
  session.userId = null;
  session.roomId = null;
  session.encrypted = false;
  session.seen.clear();
  selectedChartGates.clear();
  comparingGateMaps = false;
  renderGateAiIdeas();
  messageInput.value = '';
  timeline.querySelectorAll('.message').forEach((message) => message.remove());
  $('#welcome-card').hidden = false;
  connectForm.reset();
  connectForm.hidden = false;
  roomPicker.hidden = true;
  sessionStorage.removeItem(CASTALIA_SSO_TRANSACTION_KEY);
  conversation.hidden = true;
  connectPanel.hidden = false;
  $('#logout-button').hidden = true;
  messageInput.disabled = false;
  messageForm.querySelector('button').disabled = false;
  messageInput.placeholder = 'Write to your circle…';
  $('.composer-note').textContent = 'Messages are shared with everyone in this circle. Only messages marked “Ask Mētheus” are sent to the AI service.';
  $('#ask-metheus').checked = false;
  pendingChartPromptMode = 'ask';
  syncIndicator.textContent = 'Not connected';
  setStatus('You’re signed out.');
});

if (pendingSsoCallback) void handleCastaliaSsoCallback(pendingSsoCallback);
