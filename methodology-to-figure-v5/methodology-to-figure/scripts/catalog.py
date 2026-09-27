"""Read the two-sheet methodology workbook; never modify the input workbook."""
import argparse
import hashlib
import json
from pathlib import Path


def read_rows(sheet):
    rows = list(sheet.values)
    found = {}
    for row_number, row in enumerate(rows[1:], 2):
        if not row or all(v is None for v in row):
            continue
        key = str(row[0]).strip()
        if row[0] is None or key in found:
            raise ValueError(f'{sheet.title}:{row_number}: missing or duplicate id {key}')
        found[key] = (row_number, row)
    return found


def import_book(source):
    import openpyxl
    digest = hashlib.sha256(Path(source).read_bytes()).hexdigest()
    book = openpyxl.load_workbook(source, read_only=True, data_only=True)
    try:
        methods = read_rows(book['Methodologies'])
        sources = read_rows(book['Sources'])
        if methods.keys() != sources.keys():
            raise ValueError('Sheet id sets differ; resolve unmatched records first')
        records = []
        for key, (mr, m) in methods.items():
            sr, s = sources[key]
            if len(m) < 3 or len(s) < 4 or any(v is None for v in (m[1], m[2], s[1], s[2], s[3])):
                raise ValueError(f'Missing required cells for id {key}')
            if str(m[2]).strip().casefold() != str(s[1]).strip().casefold():
                raise ValueError(f'Keyword mismatch for id {key}')
            records.append({'id': key, 'keyword': str(m[2]).strip(), 'title': str(s[2]).strip(),
                            'methodology_paraphrase': str(m[1]), 'source_hint': str(s[3]),
                            'methodology_range': f'Methodologies!A{mr}:C{mr}',
                            'source_range': f'Sources!A{sr}:D{sr}',
                            'fulltext_status': 'not_verified'})
        return {'source_filename': Path(source).name, 'source_sha256': digest,
                'record_count': len(records), 'records': records}
    finally:
        book.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    imp = sub.add_parser('import')
    imp.add_argument('workbook')
    imp.add_argument('--out', required=True)
    lookup = sub.add_parser('lookup')
    lookup.add_argument('index')
    lookup.add_argument('--query', required=True)
    args = parser.parse_args()
    if args.command == 'import':
        result = import_book(args.workbook)
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
        print(json.dumps({'record_count': result['record_count'], 'out': str(target)}, ensure_ascii=False))
    else:
        records = json.loads(Path(args.index).read_text(encoding='utf-8-sig'))['records']
        q = args.query.strip().casefold()
        if not q:
            parser.error('query must not be empty')
        exact = [r for r in records if q in (str(r['id']).casefold(), r['keyword'].casefold(), r['title'].casefold())]
        result = exact or [r for r in records if q in (r['keyword'] + ' ' + r['title']).casefold()]
        print(json.dumps({'matches': result, 'count': len(result)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
