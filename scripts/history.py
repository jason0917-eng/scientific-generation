"""Compare declared visual descriptors, not image semantics or scientific truth."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

FIELDS = ('style', 'layout', 'elements', 'relation_visuals', 'topology')


def load(path):
    data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError(f'{path}: expected object')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', data.get('run_id', '')):
        raise ValueError(f'{path}: invalid run_id')
    for key in FIELDS:
        values = data.get(key)
        if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x.strip() for x in values):
            raise ValueError(f'{path}: {key} must be a nonempty string array')
    return data


def similarity(a, b):
    a, b = ({x.strip().casefold() for x in v} for v in (a, b))
    return len(a & b) / len(a | b)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_path(data, design_path):
    if not data.get('image_path'):
        return None
    image = Path(data['image_path'])
    return (image if image.is_absolute() else Path(design_path).parent / image).resolve()


def compare(data, history, design_path):
    root = Path(history)
    current_image = image_path(data, design_path)
    digest = sha(current_image) if current_image and current_image.is_file() else None
    matches = []
    for path in sorted(root.glob('*.json')):
        old = load(path)
        scores = {k: similarity(data[k], old[k]) for k in FIELDS}
        score = sum(scores[k] for k in FIELDS[:-1]) / 4
        matches.append({'run_id': old['run_id'], 'scores': scores, 'visual_score': score,
                        'needs_visual_review': score >= 0.80,
                        'identical_file': bool(digest and digest == old.get('image_sha256')),
                        'image_path': old.get('image_path'),
                        'image_available': bool(old.get('image_path') and Path(old['image_path']).is_file())})
    matches.sort(key=lambda x: (x['identical_file'], x['visual_score']), reverse=True)
    return {'status': 'no_history' if not matches else 'requires_visual_inspection',
            'history_count': len(matches), 'matches': matches[:5]}


def record(data, history, design_path):
    if data.get('review_status') != 'passed':
        raise ValueError('Only record figures with completed visual/scientific review')
    image = image_path(data, design_path)
    if not image or not image.is_file():
        raise ValueError('Reviewed image must exist')
    root = Path(history)
    root.mkdir(parents=True, exist_ok=True)
    item = dict(data, image_path=str(image), image_sha256=sha(image),
                recorded_at=datetime.now(timezone.utc).isoformat())
    destination = root / (data['run_id'] + '.json')
    with destination.open('x', encoding='utf-8') as handle:
        json.dump(item, handle, ensure_ascii=False, indent=2)
    return {'recorded': str(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['compare', 'record'])
    parser.add_argument('design')
    parser.add_argument('--history', required=True)
    args = parser.parse_args()
    data = load(args.design)
    result = (compare if args.command == 'compare' else record)(data, args.history, args.design)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
