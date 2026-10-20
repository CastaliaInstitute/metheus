import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const SVG_URL = '/chat/bodygraph-reference.svg?v=2';
const ENDOCRINE_URL = '/chat/endocrine-relations.json?v=0.2.3';
const CORRESPONDENCE_URL = '/chat/gate-endocrine-correspondences.json?v=0.2.0';
const $ = (selector) => document.querySelector(selector);

function pointInRoot(root, element, x, y) {
  const rootMatrix = root.getScreenCTM();
  const elementMatrix = element.getScreenCTM();
  if (!rootMatrix || !elementMatrix) return null;
  const point = root.createSVGPoint();
  point.x = x;
  point.y = y;
  const relative = rootMatrix.inverse().multiply(elementMatrix);
  const mapped = point.matrixTransform(relative);
  return { x: mapped.x, y: mapped.y };
}

function parseReference(text, svg) {
  const gates = new Set();
  const channels = new Set();
  for (const match of text.matchAll(/\bgate\s*#?\s*(\d{1,2})\b/gi)) {
    if (svg.getElementById(`gate-${match[1]}`)) gates.add(match[1]);
  }
  for (const match of text.matchAll(/\bchannel\s*#?\s*(\d{1,2})\s*[-–/]\s*(\d{1,2})\b/gi)) {
    const direct = `${match[1]}-${match[2]}`;
    const reverse = `${match[2]}-${match[1]}`;
    if (svg.querySelector(`.channel-group[data-channel="${direct}"]`)) channels.add(direct);
    else if (svg.querySelector(`.channel-group[data-channel="${reverse}"]`)) channels.add(reverse);
  }
  return { gates, channels };
}

function describeReference(gates, channels, svg) {
  const parts = [];
  for (const channel of channels) parts.push(`Channel ${channel}`);
  for (const gate of gates) {
    const node = svg.getElementById(`gate-${gate}`);
    const name = node?.getAttribute('data-reading');
    parts.push(name ? `Gate ${gate} · ${name}` : `Gate ${gate}`);
  }
  return parts;
}

export async function mountBodygraph() {
  const viewer = $('#bodygraph-viewer');
  const canvas = $('#bodygraph-canvas');
  const detail = $('#bodygraph-detail');
  const modeBodygraph = $('#map-mode-bodygraph');
  const modeCorrespondence = $('#map-mode-correspondence');
  const modeEndocrine = $('#map-mode-endocrine');
  const boundary = $('#map-boundary');
  const endocrineControls = $('#endocrine-controls');
  const filter = $('#endocrine-filter');
  const sourceHost = $('#bodygraph-source');
  const response = await fetch(SVG_URL, { cache: 'force-cache' });
  if (!response.ok) throw new Error('Bodygraph reference image could not be loaded.');
  const markup = await response.text();
  const parsed = new DOMParser().parseFromString(markup, 'image/svg+xml');
  const svg = parsed.documentElement;
  if (parsed.querySelector('parsererror') || svg.localName !== 'svg' || svg.querySelector('script')) {
    throw new Error('Bodygraph reference file is invalid or contains active content.');
  }
  svg.setAttribute('width', '360');
  svg.setAttribute('height', '360');
  svg.setAttribute('focusable', 'false');
  sourceHost.replaceChildren(document.importNode(svg, true));
  const source = sourceHost.querySelector('svg');
  const viewBox = (source.getAttribute('viewBox') || '0 0 360 360').split(/[\s,]+/).map(Number);
  const [vbX, vbY, vbW, vbH] = viewBox;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 1, 1200);
  camera.position.set(0, 0, 510);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'low-power' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x111821, 0);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minDistance = 350;
  controls.maxDistance = 760;
  controls.minPolarAngle = Math.PI / 2 - 0.65;
  controls.maxPolarAngle = Math.PI / 2 + 0.65;
  controls.rotateSpeed = 0.42;

  const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(vbW, vbH),
    new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }),
  );
  plane.rotation.x = -0.035;
  scene.add(plane);

  const endocrineGroup = new THREE.Group();
  endocrineGroup.visible = false;
  endocrineGroup.position.z = 4;
  scene.add(endocrineGroup);
  const correspondenceGroup = new THREE.Group();
  correspondenceGroup.visible = false;
  correspondenceGroup.position.z = 2.8;
  plane.add(correspondenceGroup);
  let endocrineRecords = [];
  let endocrineLoadPromise = null;
  let gateCorrespondences = [];
  let visibleGateCorrespondences = [];
  const endocrineDomainLabels = {
    hpt: 'Thyroid regulation', hpa: 'Stress-axis regulation', hpg: 'Reproductive-axis regulation',
    circadian: 'Circadian regulation', glucose: 'Glucose regulation', gut: 'Gut-incretin signaling',
    reproductive: 'Reproductive-cycle regulation',
  };
  const colorsByType = { hormone: 0x75c8be, process: 0xf0b66d, hormone_group: 0xd99fc8, receptor: 0x9eacd8 };

  function clearCorrespondences() {
    while (correspondenceGroup.children.length) {
      const object = correspondenceGroup.children.pop();
      object.geometry?.dispose();
      if (Array.isArray(object.material)) object.material.forEach((material) => { material.map?.dispose(); material.dispose(); });
      else { object.material?.map?.dispose(); object.material?.dispose(); }
    }
  }

  function renderCorrespondences() {
    clearCorrespondences();
    const list = $('#gate-correspondence-list');
    const query = $('#gate-correspondence-filter').value.trim().toLocaleLowerCase();
    const visibleItems = gateCorrespondences.filter((item) => {
      const searchable = [item.sourceFeature.label, item.sourceFeature.id, item.targetConcept.label, item.sourceSystem.name, item.sourceSystem.lineage, item.claimText].join(' ').toLocaleLowerCase();
      return !query || searchable.includes(query);
    });
    visibleGateCorrespondences = visibleItems;
    list.replaceChildren();
    const byGate = new Map();
    for (const item of visibleItems) {
      const group = byGate.get(item.sourceFeature.id) || [];
      group.push(item);
      byGate.set(item.sourceFeature.id, group);
    }
    $('#gate-correspondence-count').textContent = `Showing ${visibleItems.length} of ${gateCorrespondences.length} source-attributed entries across ${byGate.size} gates.`;
    for (const [gateId, items] of byGate) {
      const target = targets.find((entry) => entry.kind === 'gate' && entry.id === gateId);
      if (!target) continue;
      const [x, y] = toPlane(target.point);
      const marker = new THREE.Mesh(new THREE.RingGeometry(6, 9, 28), new THREE.MeshBasicMaterial({ color: 0x9a5eac, side: THREE.DoubleSide, depthTest: false }));
      marker.position.set(x, y, 2);
      marker.userData.gateId = gateId;
      correspondenceGroup.add(marker);
      if (byGate.size <= 8) {
        const labelCanvas = document.createElement('canvas');
        labelCanvas.width = 512;
        labelCanvas.height = 72;
        const context = labelCanvas.getContext('2d');
        context.font = 'bold 23px system-ui, sans-serif';
        context.fillStyle = '#51335d';
        const targetLabel = items.length > 1 ? `${items.length} sourced links` : items[0].targetConcept.label;
        const shortLabel = targetLabel.length > 34 ? `${targetLabel.slice(0, 31)}…` : targetLabel;
        context.fillText(`Gate ${gateId} · ${shortLabel}`, 8, 42);
        const texture = new THREE.CanvasTexture(labelCanvas);
        texture.colorSpace = THREE.SRGBColorSpace;
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }));
        sprite.position.set(x + 30, y + (y > 0 ? -12 : 12), 3);
        sprite.scale.set(104, 14.6, 1);
        correspondenceGroup.add(sprite);

      }

      for (const item of items) {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.correspondenceId = item.id;
        button.textContent = `${item.sourceFeature.label} → ${item.targetConcept.label} · ${item.sourceSystem.lineage || item.sourceSystem.name} · source-attributed; select for details`;
        list.append(button);
      }
    }
  }

  function displayCorrespondence(item) {
    if (!item) return;
    const citation = item.sourceCitations[0];
    detail.replaceChildren();
    const summary = document.createElement('span');
    summary.textContent = `${item.sourceFeature.label} → ${item.targetConcept.label}. ${item.claimText} `;
    detail.append(summary);
    const link = document.createElement('a');
    link.href = citation.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = `${citation.title} · ${citation.locator || 'Source'}`;
    detail.append(link);
    const limitations = document.createElement('span');
    limitations.textContent = ` Limits: ${item.limitations.join(' ')}`;
    detail.append(limitations);
    appendCandidatePhysiology(detail, item);
  }

  function appendCandidatePhysiology(parent, item) {
    const section = document.createElement('section');
    const heading = document.createElement('strong');
    heading.textContent = 'Separate candidate physiology catalog';
    const note = document.createElement('span');
    note.textContent = 'Checking for an exact shared organ ID…';
    section.append(heading, note);
    parent.append(section);
    ensureEndocrineCatalog().then((records) => {
      if (!section.isConnected) return;
      const related = records.filter((relation) => relation.sourceEntity.id === item.targetConcept.id || relation.targetEntity.id === item.targetConcept.id);
      section.replaceChildren(heading);
      const boundary = document.createElement('span');
      boundary.textContent = related.length
        ? `Exact entity ID match: ${item.targetConcept.id}. This joins catalog entries for reference only; it does not validate the gate-to-organ teaching.`
        : `No exact entity ID match for ${item.targetConcept.id} exists in the current endocrine relations catalog. No fuzzy name matching is used.`;
      section.append(boundary);
      if (!related.length) {
        const empty = document.createElement('span');
        empty.textContent = 'The two layers remain separate; absence of an exact catalog match is not evidence against either source.';
        section.append(empty);
        return;
      }
      for (const relation of related) {
        const relationText = document.createElement('p');
        relationText.textContent = `${relation.statement} Status: ${relation.evidenceStatus}; internal candidate physiology only.`;
        section.append(relationText);
        for (const source of relation.sourceCitations || []) {
          const sourceLink = document.createElement('a');
          sourceLink.href = source.url;
          sourceLink.target = '_blank';
          sourceLink.rel = 'noopener noreferrer';
          sourceLink.textContent = `${source.title} · ${source.locator || 'Source'}`;
          section.append(sourceLink);
        }
      }
    }).catch(() => {
      if (!section.isConnected) return;
      note.textContent = 'The separate candidate physiology catalog could not be loaded. This does not affect the source-attributed gate entry above.';
    });
  }

  function displayGateCorrespondences(gateId) {
    const matches = visibleGateCorrespondences.filter((entry) => entry.sourceFeature.id === gateId);
    if (matches.length === 1) return displayCorrespondence(matches[0]);
    if (!matches.length) return;
    detail.replaceChildren();
    for (const item of matches) {
      const section = document.createElement('section');
      const summary = document.createElement('span');
      summary.textContent = `${item.sourceFeature.label} → ${item.targetConcept.label}. ${item.claimText} `;
      const citation = item.sourceCitations[0];
      const link = document.createElement('a');
      link.href = citation.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = `${citation.title} · ${citation.locator || 'Source'}`;
      const limits = document.createElement('span');
      limits.textContent = ` Limits: ${item.limitations.join(' ')}`;
      section.append(summary, link, limits);
      appendCandidatePhysiology(section, item);
      detail.append(section);
    }
  }

  async function loadCorrespondences() {
    try {
      const response = await fetch(CORRESPONDENCE_URL, { cache: 'force-cache' });
      if (!response.ok) throw new Error('Gate correspondence catalog could not be loaded.');
      const catalog = await response.json();
      gateCorrespondences = catalog.correspondences;
      renderCorrespondences();
      detail.textContent = `Select a ring or source-list entry to read the attributed wording and limitations. Dense overlays omit on-map labels for readability; use the filter to find a gate, organ, or source.`;
    } catch {
      detail.textContent = 'The gate correspondence catalog could not be loaded. The generic BodyGraph is still available.';
    }
  }

  function clearEndocrine() {
    while (endocrineGroup.children.length) {
      const object = endocrineGroup.children.pop();
      object.geometry?.dispose();
      if (Array.isArray(object.material)) object.material.forEach((material) => { material.map?.dispose(); material.dispose(); });
      else { object.material?.map?.dispose(); object.material?.dispose(); }
    }
  }

  function renderEndocrine() {
    clearEndocrine();
    const selectedDomain = filter.value;
    const relations = endocrineRecords.filter((record) => selectedDomain === 'all' || record.domain === selectedDomain);
    const entities = new Map();
    for (const relation of relations) {
      entities.set(relation.sourceEntity.id, relation.sourceEntity);
      entities.set(relation.targetEntity.id, relation.targetEntity);
    }
    const nodes = [...entities.values()];
    if (!nodes.length) {
      detail.textContent = 'No candidate relations are available in this domain.';
      return;
    }
    const positions = new Map();
    const radius = Math.min(135, Math.max(74, nodes.length * 4.1));
    nodes.forEach((entity, index) => {
      const angle = -Math.PI / 2 + (index / nodes.length) * Math.PI * 2;
      positions.set(entity.id, new THREE.Vector3(Math.cos(angle) * radius, Math.sin(angle) * radius, 2));
    });
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x718c95, transparent: true, opacity: 0.55 });
    for (const relation of relations) {
      const from = positions.get(relation.sourceEntity.id);
      const to = positions.get(relation.targetEntity.id);
      if (!from || !to) continue;
      const geometry = new THREE.BufferGeometry().setFromPoints([from, to]);
      endocrineGroup.add(new THREE.Line(geometry, edgeMaterial.clone()));
    }
    nodes.forEach((entity) => {
      const position = positions.get(entity.id);
      const color = colorsByType[entity.entityType] || 0xb4c2c6;
      const sphere = new THREE.Mesh(new THREE.SphereGeometry(4.1, 18, 14), new THREE.MeshBasicMaterial({ color }));
      sphere.position.copy(position);
      sphere.userData.entityId = entity.id;
      endocrineGroup.add(sphere);

      const labelCanvas = document.createElement('canvas');
      labelCanvas.width = 512;
      labelCanvas.height = 64;
      const labelContext = labelCanvas.getContext('2d');
      labelContext.font = '22px system-ui, sans-serif';
      labelContext.fillStyle = '#17252b';
      const label = entity.label.length > 43 ? `${entity.label.slice(0, 40)}…` : entity.label;
      labelContext.fillText(label, 8, 39);
      const texture = new THREE.CanvasTexture(labelCanvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }));
      sprite.position.set(position.x + 5, position.y - 6, 3);
      sprite.scale.set(76, 9.5, 1);
      endocrineGroup.add(sprite);
    });
    const domainName = selectedDomain === 'all' ? 'all listed domains' : endocrineDomainLabels[selectedDomain] || selectedDomain;
    detail.textContent = `${nodes.length} candidate entities · ${relations.length} relations · ${domainName}. Select a node for catalog context. All entries are under review and internal only.`;
    endocrineGroup.userData.relations = relations;
    endocrineGroup.userData.entities = entities;
    endocrineGroup.userData.positions = positions;
  }

  async function ensureEndocrineCatalog() {
    if (endocrineRecords.length) return endocrineRecords;
    if (!endocrineLoadPromise) {
      endocrineLoadPromise = (async () => {
        const response = await fetch(ENDOCRINE_URL, { cache: 'force-cache' });
        if (!response.ok) throw new Error('Candidate endocrine catalog could not be loaded.');
        const catalog = await response.json();
        endocrineRecords = catalog.relations.map((relation) => {
          const text = `${relation.context?.setting || ''} ${relation.statement || ''}`.toLowerCase();
          let domain = 'other';
          if (/thyroid|\bhpt\b|trh|tsh/.test(text)) domain = 'hpt';
          else if (/menstrual|ovarian|follicular|luteal|pregnancy|menopause|\bhpg\b|gonadotropin/.test(text)) domain = 'reproductive';
          else if (/circadian|melatonin|sleep timing/.test(text)) domain = 'circadian';
          else if (/glucose|insulin|glucagon/.test(text)) domain = 'glucose';
          else if (/gut|incretin|\bglp-1\b/.test(text)) domain = 'gut';
          else if (/stress|adrenal|cortisol|\bhpa\b/.test(text)) domain = 'hpa';
          return { ...relation, domain };
        });
        const domains = [...new Set(endocrineRecords.map((relation) => relation.domain))].filter((domain) => domain !== 'all');
        domains.forEach((domain) => {
          if (filter.querySelector(`option[value="${domain}"]`)) return;
          const option = document.createElement('option');
          option.value = domain;
          option.textContent = endocrineDomainLabels[domain] || domain;
          filter.append(option);
        });
        return endocrineRecords;
      })().catch((error) => {
        endocrineLoadPromise = null;
        throw error;
      });
    }
    return endocrineLoadPromise;
  }

  async function loadEndocrine() {
    try {
      await ensureEndocrineCatalog();
      renderEndocrine();
    } catch {
      detail.textContent = 'The candidate endocrine catalog could not be loaded. The BodyGraph reference is still available.';
    }
  }

  function setMapMode(mode) {
    const endocrine = mode === 'endocrine';
    const correspondence = mode === 'correspondence';
    plane.visible = !endocrine;
    highlightObjects.visible = !endocrine && !correspondence;
    endocrineGroup.visible = endocrine;
    correspondenceGroup.visible = correspondence;
    sourceHost.hidden = endocrine;
    modeBodygraph.classList.toggle('is-selected', mode === 'bodygraph');
    modeBodygraph.setAttribute('aria-pressed', String(mode === 'bodygraph'));
    modeCorrespondence.classList.toggle('is-selected', correspondence);
    modeCorrespondence.setAttribute('aria-pressed', String(correspondence));
    modeEndocrine.classList.toggle('is-selected', endocrine);
    modeEndocrine.setAttribute('aria-pressed', String(endocrine));
    endocrineControls.hidden = !endocrine;
    $('#gate-correspondence-list').hidden = !correspondence;
    $('#gate-correspondence-tools').hidden = !correspondence;
    search.hidden = endocrine || correspondence;
    $('#bodygraph-clear').hidden = endocrine || correspondence;
    boundary.textContent = endocrine
      ? 'Separate candidate biology network · under review · internal only. Node positions are diagram layout, not anatomy. No gate/channel equivalence or personal inference.'
      : correspondence
        ? 'Source-attributed Human Design gate-to-organ teachings. Sources may differ; compare each lineage’s claim and limits. The overlay does not assert a gate-to-hormone mechanism or describe a person’s biology.'
        : 'The endocrine network is a separate candidate biology graph. Gate links are shown only in the distinct Correspondence view.';
    if (endocrine) { if (!endocrineRecords.length) loadEndocrine(); else renderEndocrine(); }
    else if (correspondence) { if (!gateCorrespondences.length) loadCorrespondences(); else renderCorrespondences(); }
    else detail.textContent = 'Choose a gate or channel to explore its place in the map.';
  }

  modeBodygraph.addEventListener('click', () => setMapMode('bodygraph'));
  modeCorrespondence.addEventListener('click', () => setMapMode('correspondence'));
  modeEndocrine.addEventListener('click', () => setMapMode('endocrine'));
  filter.addEventListener('change', renderEndocrine);
  $('#gate-correspondence-filter').addEventListener('input', renderCorrespondences);
  $('#gate-correspondence-list').addEventListener('click', (event) => {
    const button = event.target.closest('[data-correspondence-id]');
    if (!button) return;
    const item = gateCorrespondences.find((entry) => entry.id === button.dataset.correspondenceId);
    displayCorrespondence(item);
  });

  const targets = [];
  for (const gateNode of source.querySelectorAll('.gate[data-gate]')) {
    const marker = gateNode.querySelector('.gate-marker');
    if (!marker) continue;
    const point = pointInRoot(source, marker, Number(marker.getAttribute('cx')), Number(marker.getAttribute('cy')));
    if (point) targets.push({ kind: 'gate', id: gateNode.dataset.gate, center: gateNode.dataset.center, point });
  }
  for (const channelNode of source.querySelectorAll('.channel-group[data-channel]')) {
    const path = channelNode.querySelector('path.channel');
    if (!path) continue;
    const length = path.getTotalLength();
    const count = Math.max(12, Math.ceil(length / 2));
    const points = [];
    for (let index = 0; index <= count; index += 1) {
      const point = path.getPointAtLength(length * index / count);
      const mapped = pointInRoot(source, path, point.x, point.y);
      if (mapped) points.push(mapped);
    }
    if (points.length) targets.push({ kind: 'channel', id: channelNode.dataset.channel, point: points[Math.floor(points.length / 2)], points, from: channelNode.dataset.from, to: channelNode.dataset.to });
  }

  const texture = new THREE.Texture();
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  plane.material.map = texture;
  plane.material.needsUpdate = true;
  let objectUrl;
  let textureRevision = 0;
  function updateTexture() {
    const revision = ++textureRevision;
    const imageData = new XMLSerializer().serializeToString(source);
    const nextUrl = URL.createObjectURL(new Blob([imageData], { type: 'image/svg+xml;charset=utf-8' }));
    const image = new Image();
    image.onload = () => {
      if (revision !== textureRevision) { URL.revokeObjectURL(nextUrl); return; }
      texture.image = image;
      texture.needsUpdate = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = nextUrl;
    };
    image.onerror = () => URL.revokeObjectURL(nextUrl);
    image.src = nextUrl;
  }

  const highlightObjects = new THREE.Group();
  scene.add(highlightObjects);
  const removeHighlights = () => {
    while (highlightObjects.children.length) {
      const object = highlightObjects.children.pop();
      object.geometry?.dispose();
      object.material?.dispose();
    }
  };

  function highlight(gateIds, channelIds, fromChat = false) {
    const selectedGateIds = new Set(gateIds);
    const selectedChannelIds = new Set(channelIds);
    const gates = new Set(selectedGateIds);
    const channels = new Set(selectedChannelIds);
    const centersToShow = new Set();
    for (const gateId of selectedGateIds) {
      const gateNode = source.getElementById(`gate-${gateId}`);
      if (gateNode) centersToShow.add(gateNode.dataset.center);
    }
    for (const channelId of channels) {
      const channelNode = source.querySelector(`.channel-group[data-channel="${channelId}"]`);
      if (!channelNode) continue;
      gates.add(channelNode.dataset.from);
      gates.add(channelNode.dataset.to);
      for (const id of [channelNode.dataset.from, channelNode.dataset.to]) {
        const gateNode = source.getElementById(`gate-${id}`);
        if (gateNode) centersToShow.add(gateNode.dataset.center);
      }
    }
    source.querySelectorAll('.is-active,.is-related').forEach((node) => node.classList.remove('is-active', 'is-related'));
    source.querySelectorAll('.gate[data-gate]').forEach((node) => {
      if (gates.has(node.dataset.gate)) node.classList.add(gateIds.includes(node.dataset.gate) ? 'is-active' : 'is-related');
    });
    source.querySelectorAll('.channel-group[data-channel]').forEach((node) => {
      if (channels.has(node.dataset.channel)) node.classList.add('is-active');
    });
    source.querySelectorAll('.center[data-center]').forEach((node) => {
      if (centersToShow.has(node.dataset.center)) node.classList.add('is-active');
    });
    updateTexture();

    removeHighlights();
    for (const target of targets) {
      const isActive = target.kind === 'gate' ? selectedGateIds.has(target.id) : selectedChannelIds.has(target.id);
      const isRelated = !isActive && (target.kind === 'gate' ? gates.has(target.id) : channels.has(target.id));
      if (!isActive && !isRelated) continue;
      if (target.kind === 'gate') {
        const [x, y] = toPlane(target.point);
        const ring = new THREE.Mesh(
          new THREE.RingGeometry(isActive ? 3 : 2.5, isActive ? 5.6 : 4.6, 28),
          new THREE.MeshBasicMaterial({ color: isActive ? 0xffbc55 : 0xe5a855, transparent: true, opacity: isActive ? 0.98 : 0.55, side: THREE.DoubleSide, depthTest: false }),
        );
        ring.position.set(x, y, 1.5);
        highlightObjects.add(ring);
      } else if (isActive && target.points.length > 1) {
        const vertices = target.points.map((point) => {
          const [x, y] = toPlane(point);
          return new THREE.Vector3(x, y, 1.7);
        });
        const line = new THREE.Line(
          new THREE.BufferGeometry().setFromPoints(vertices),
          new THREE.LineBasicMaterial({ color: 0xffbc55, transparent: true, opacity: 0.94 }),
        );
        highlightObjects.add(line);
      }
    }
    const labels = describeReference(gateIds, channelIds, source);
    detail.textContent = labels.length ? `${fromChat ? 'Mention in chat · ' : ''}${labels.join(' · ')}. Highlight only; not a personal chart or individual claim.` : 'Choose a gate or channel to highlight it in the reference map.';
    return labels.length > 0;
  }

  function toPlane(point) {
    return [point.x - vbX - vbW / 2, vbH / 2 - (point.y - vbY)];
  }

  function highlightFromText(text) {
    const refs = parseReference(text, source);
    if (!refs.gates.size && !refs.channels.size) return false;
    return highlight([...refs.gates], [...refs.channels], true);
  }

  const search = $('#bodygraph-search');
  search.addEventListener('submit', (event) => {
    event.preventDefault();
    const query = $('#bodygraph-query').value.trim();
    const refs = parseReference(query, source);
    if (!refs.gates.size && !refs.channels.size) {
      detail.textContent = 'Try a gate number (for example, “Gate 34”) or a channel (for example, “Channel 34–20”).';
      return;
    }
    highlight([...refs.gates], [...refs.channels]);
  });
  $('#bodygraph-clear').addEventListener('click', () => {
    $('#bodygraph-query').value = '';
    highlight([], []);
  });

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let down = null;
  const graphPointFromIntersection = (intersection) => ({ x: vbX + intersection.uv.x * vbW, y: vbY + (1 - intersection.uv.y) * vbH });
  function targetAt(point) {
    let best = null;
    let distance = Infinity;
    for (const target of targets) {
      const samples = target.points || [target.point];
      for (const sample of samples) {
        const next = Math.hypot(sample.x - point.x, sample.y - point.y);
        if (next < distance) { best = target; distance = next; }
      }
    }
    return distance <= 5.5 ? best : null;
  }
  function hitTarget(event) {
    const bounds = canvas.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return null;
    pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
    pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const intersection = raycaster.intersectObject(plane)[0];
    return intersection ? targetAt(graphPointFromIntersection(intersection)) : null;
  }
  function selectEndocrineNode(event) {
    const bounds = canvas.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return;
    pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
    pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const node = raycaster.intersectObjects(endocrineGroup.children.filter((object) => object.userData.entityId))[0]?.object;
    if (!node) return;
    const entity = endocrineGroup.userData.entities.get(node.userData.entityId);
    const related = endocrineGroup.userData.relations.filter((relation) => relation.sourceEntity.id === entity.id || relation.targetEntity.id === entity.id);
    const relation = related[0];
    const citation = relation?.sourceCitations?.[0];
    detail.textContent = `${entity.label} · ${entity.entityType} · ${entity.compartment}. ${related.length} candidate relation${related.length === 1 ? '' : 's'}. ${relation?.statement || ''}${citation ? ` Source: ${citation.title} (${citation.locator}).` : ''} Catalog status: under review; internal only.`;
  }
  function selectCorrespondence(event) {
    const bounds = canvas.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return;
    pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
    pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const marker = raycaster.intersectObjects(correspondenceGroup.children.filter((object) => object.userData.gateId))[0]?.object;
    if (!marker) return;
    displayGateCorrespondences(marker.userData.gateId);
  }
  canvas.addEventListener('pointerdown', (event) => { down = { x: event.clientX, y: event.clientY }; });
  canvas.addEventListener('pointerup', (event) => {
    if (!down || Math.hypot(event.clientX - down.x, event.clientY - down.y) > 6) { down = null; return; }
    const target = hitTarget(event);
    if (endocrineGroup.visible) { selectEndocrineNode(event); down = null; return; }
    if (correspondenceGroup.visible) { selectCorrespondence(event); down = null; return; }
    down = null;
    if (!target) return;
    if (target.kind === 'gate') {
      $('#bodygraph-query').value = `Gate ${target.id}`;
      highlight([target.id], []);
    } else {
      $('#bodygraph-query').value = `Channel ${target.id}`;
      highlight([], [target.id]);
    }
  });

  function resize() {
    const rect = viewer.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return;
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
    renderer.setSize(rect.width, rect.height, false);
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(viewer);
  resize();
  updateTexture();
  let animationFrame;
  let animationRunning = false;
  const render = () => {
    if (!$('#bodygraph-panel').open) { animationRunning = false; return; }
    controls.update();
    renderer.render(scene, camera);
    animationFrame = requestAnimationFrame(render);
  };
  if (window.matchMedia('(max-width: 740px)').matches) $('#bodygraph-panel').open = false;
  const startRenderLoop = () => {
    if (animationRunning || !$('#bodygraph-panel').open) return;
    animationRunning = true;
    resize();
    render();
  };
  $('#bodygraph-panel').addEventListener('toggle', startRenderLoop);
  startRenderLoop();

  return {
    highlightFromText,
    dispose() {
      cancelAnimationFrame(animationFrame);
      animationRunning = false;
      $('#bodygraph-panel').removeEventListener('toggle', startRenderLoop);
      resizeObserver.disconnect();
      controls.dispose();
      renderer.dispose();
      texture.dispose();
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      removeHighlights();
      plane.geometry.dispose();
      plane.material.dispose();
    },
  };
}
