// Assembles per-part GLBs from a modelkit manifest into an interactive view:
// orbit, auto-spin, explode slider, hover to name a part, click for details.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

interface Part {
  id: string; name: string; color: string; source: string; material: string | null;
  mass_g: number | null; mpn: string; description: string; explode_mm: number[];
  files: { glb: string };
}

const loader = new GLTFLoader();
const MM = 0.001; // GLBs are metres, Y up; manifest vectors are CAD mm, Z up
const toScene = ([x, y, z]: number[]) => new THREE.Vector3(x * MM, z * MM, -y * MM);

async function mount(el: HTMLElement) {
  const base = el.dataset.base!;
  const stage = el.querySelector<HTMLElement>('.viewer-stage')!;
  const canvas = el.querySelector('canvas')!;
  const status = el.querySelector<HTMLElement>('.viewer-status')!;
  const hoverEl = el.querySelector<HTMLElement>('.viewer-hover')!;
  const info = el.querySelector<HTMLElement>('.viewer-info')!;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 0.001, 100);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f98, 1.6));
  const key = new THREE.DirectionalLight(0xffffff, 2.2);
  camera.add(key); // light travels with the camera so no face is ever unlit
  key.position.set(0.6, 1, 0.8);
  scene.add(camera);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.autoRotate = el.dataset.spin === 'true';
  controls.autoRotateSpeed = 1.2;

  let manifest: { parts: Part[] };
  const groups: { part: Part; group: THREE.Group; offset: THREE.Vector3 }[] = [];
  try {
    manifest = await (await fetch(base + 'manifest.json')).json();
    await Promise.all(
      manifest.parts.map(async (part) => {
        const gltf = await loader.loadAsync(base + part.files.glb);
        const mat = new THREE.MeshStandardMaterial({ color: part.color, roughness: 0.62, metalness: part.source === 'bought' ? 0.35 : 0.05 });
        gltf.scene.traverse((o) => {
          const mesh = o as THREE.Mesh;
          if (!mesh.isMesh) return;
          mesh.material = mat;
          mesh.userData.part = part;
          const edges = new THREE.LineSegments(
            new THREE.EdgesGeometry(mesh.geometry, 28),
            new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.28 }),
          );
          edges.raycast = () => {};
          mesh.add(edges);
        });
        scene.add(gltf.scene);
        groups.push({ part, group: gltf.scene, offset: toScene(part.explode_mm) });
      }),
    );
  } catch (err) {
    status.textContent = 'Could not load the model.';
    console.error(err);
    return;
  }
  status.hidden = true;

  // Framing: radius grows with the explode amount so parts never leave the view.
  const sphereAt = (t: number) => {
    const box = new THREE.Box3();
    for (const g of groups) {
      g.group.position.copy(g.offset).multiplyScalar(t);
      g.group.updateMatrixWorld(true);
      box.expandByObject(g.group);
    }
    return box.getBoundingSphere(new THREE.Sphere());
  };
  const closed = sphereAt(0);
  const open = sphereAt(1);
  let explode = 0;
  const radius = (t: number) => closed.radius + (open.radius - closed.radius) * t;
  const fitDistance = (r: number) => (r / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2))) * 1.08;
  const home = new THREE.Vector3(1, 0.62, 1.25).normalize();

  function setExplode(t: number) {
    const dir = camera.position.clone().sub(controls.target);
    dir.multiplyScalar(radius(t) / radius(explode));
    explode = t;
    controls.target.lerpVectors(closed.center, open.center, t);
    camera.position.copy(controls.target).add(dir);
    for (const g of groups) g.group.position.copy(g.offset).multiplyScalar(t);
    dirty = true;
  }
  function reset() {
    controls.target.lerpVectors(closed.center, open.center, explode);
    camera.position.copy(controls.target).addScaledVector(home, fitDistance(radius(explode)));
    dirty = true;
  }

  let dirty = true;
  let visible = true;
  const resize = () => {
    const { clientWidth: w, clientHeight: h } = stage;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    dirty = true;
  };
  new ResizeObserver(resize).observe(stage);
  new IntersectionObserver(([e]) => (visible = e.isIntersecting)).observe(stage);
  resize();
  setExplode(0);
  reset();
  controls.addEventListener('change', () => (dirty = true));

  // Hover names a part; click pins its details.
  const ray = new THREE.Raycaster();
  let lit: THREE.Mesh | null = null;
  const pick = (ev: PointerEvent) => {
    const r = canvas.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1), camera);
    return ray.intersectObjects(groups.map((g) => g.group), true)[0]?.object as THREE.Mesh | undefined;
  };
  const highlight = (mesh: THREE.Mesh | null) => {
    if (lit === mesh) return;
    if (lit) (lit.material as THREE.MeshStandardMaterial).emissive.set(0x000000);
    lit = mesh;
    if (lit) (lit.material as THREE.MeshStandardMaterial).emissive.set(0x2a3f5f);
    dirty = true;
  };
  canvas.addEventListener('pointermove', (ev) => {
    const hit = pick(ev);
    highlight(hit ?? null);
    hoverEl.hidden = !hit;
    canvas.style.cursor = hit ? 'pointer' : 'grab';
    if (hit) {
      const r = stage.getBoundingClientRect();
      hoverEl.textContent = hit.userData.part.name;
      hoverEl.style.left = ev.clientX - r.left + 12 + 'px';
      hoverEl.style.top = ev.clientY - r.top + 12 + 'px';
    }
  });
  canvas.addEventListener('pointerleave', () => { highlight(null); hoverEl.hidden = true; });
  let downAt = [0, 0];
  canvas.addEventListener('pointerdown', (ev) => (downAt = [ev.clientX, ev.clientY]));
  canvas.addEventListener('pointerup', (ev) => {
    if (Math.hypot(ev.clientX - downAt[0], ev.clientY - downAt[1]) > 4) return; // it was a drag
    const part: Part | undefined = pick(ev)?.userData.part;
    info.hidden = !part;
    if (!part) return;
    const mass = part.mass_g == null ? null : `${part.mass_g >= 100 ? part.mass_g.toFixed(0) : part.mass_g.toFixed(1)} g`;
    info.querySelector('.viewer-info-name')!.textContent = part.name;
    info.querySelector('.viewer-info-meta')!.textContent = [mass, part.material, part.source, part.mpn].filter(Boolean).join(' · ');
    info.querySelector('.viewer-info-desc')!.textContent = part.description;
  });
  info.querySelector('.viewer-close')!.addEventListener('click', () => (info.hidden = true));

  const spinBtn = el.querySelector<HTMLButtonElement>('[data-act=spin]')!;
  const setSpin = (on: boolean) => {
    controls.autoRotate = on;
    spinBtn.textContent = on ? 'Pause' : 'Spin';
    spinBtn.setAttribute('aria-pressed', String(on));
  };
  spinBtn.addEventListener('click', () => setSpin(!controls.autoRotate));
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) setSpin(false);
  el.querySelector('[data-act=reset]')!.addEventListener('click', reset);
  el.querySelector<HTMLInputElement>('[data-act=explode]')?.addEventListener('input', (ev) =>
    setExplode(Number((ev.target as HTMLInputElement).value)),
  );

  renderer.setAnimationLoop(() => {
    if (!visible) return;
    controls.update();
    if (dirty || controls.autoRotate) renderer.render(scene, camera);
    dirty = false;
  });
  el.dataset.ready = 'true';
}

document.querySelectorAll<HTMLElement>('[data-viewer]:not([data-mounted])').forEach((el) => {
  el.dataset.mounted = 'true';
  mount(el);
});
