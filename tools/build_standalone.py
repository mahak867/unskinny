"""Bundle showcase/index.html, the 3D model, images and three.js into one offline HTML file.
Usage: python3 tools/build_standalone.py path/to/three-0.128.0-package"""
import base64, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = sys.argv[1].rstrip('/') + '/'
s = open(os.path.join(ROOT, 'showcase/index.html')).read()
three = open(P + 'build/three.min.js').read()
orbit = open(P + 'examples/js/controls/OrbitControls.js').read()
model = open(os.path.join(ROOT, 'showcase/model.json')).read()
s = s.replace("fetch('model.json').then(r=>r.json())", "Promise.resolve(window.__MODEL__)")
s = s.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',
              '<script>window.__MODEL__=' + model + ';</script>\n<script>' + three + '</script>')
s = s.replace('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>',
              '<script>' + orbit + '</script>')
assert 'cdnjs' not in s and 'cdn.jsdelivr' not in s
for img, mt in [('sim_results.png', 'image/png'), ('weight_budget.png', 'image/png'), ('demo_spin.gif', 'image/gif')]:
    s = s.replace(f'src="{img}"', f'src="data:{mt};base64,' + base64.b64encode(open(os.path.join(ROOT, 'out', img), 'rb').read()).decode() + '"')
s = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
     '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
     + s.replace('<main>', '</head>\n<body>\n<main>', 1) + '\n</body>\n</html>\n')
for out in ('unskinny-mk2.html', 'docs/index.html'):
    os.makedirs(os.path.dirname(os.path.join(ROOT, out)) or ROOT, exist_ok=True)
    open(os.path.join(ROOT, out), 'w').write(s)
print('wrote', len(s) // 1024, 'KB')
