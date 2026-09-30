"""노션 프로그램DB → 포티처 index.html 반영

노션 「프로그램DB」의 '포티처에 나오는 것' 보기에서 읽어온 행을
tools/programs.json 에 저장한 뒤 실행합니다.

    python tools/apply_programs.py

- 포티처 노출이 체크된 행만 씁니다 (programs.json 에는 그 행만 들어 있음)
- 카테고리마다 '순서'가 작은 것부터 앞에 옵니다. 추천 결과에는 앞의 3개가 나옵니다.
- index.html 의 D.PROGRAMS / PROGRAM_PITCH / PROGRAM_IMG / PROGRAM_MIN / PROGRAM_LEVEL 만 바꿉니다.
- 대상(학교급 선택)이 있으면 선생님이 고른 학교급·학년과 겹칠 때만 추천됩니다.
- 최저 예산이 있으면 선생님 예산 ±50만원 안의 프로그램만 추천됩니다.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'index.html'
DATA = ROOT / 'tools' / 'programs.json'
SITE = 'https://tjdwo3435-byte.github.io/fortitcher-recommend/'


def clean(v):
    # 노션 마크다운 이스케이프(\[ \~ 등) 제거
    return re.sub(r'\\([\[\]~*_`#|\\])', r'\1', (v or '').strip())


def replace_obj(src, name, value):
    """`var NAME=` 뒤의 JSON 객체 하나를 value 로 교체"""
    start = src.index('var ' + name + '=') + len('var ' + name + '=')
    _, end = json.JSONDecoder().raw_decode(src, start)
    body = json.dumps(value, ensure_ascii=False, indent=4).replace('\n}', '\n  }')
    return src[:start] + body + src[end:]


def main():
    rows = json.loads(DATA.read_text(encoding='utf-8'))
    src = PAGE.read_text(encoding='utf-8')

    m = re.search(r'var D = (\{.*?\});\n', src)
    D = json.loads(m.group(1))

    by_cat = {k: [] for k in D['PROGRAM_KEYS']}
    pitch, img, minb, level, unknown = {}, {}, {}, {}, set()
    for r in rows:
        name = clean(r.get('프로그램명') or r.get('프로그램 명'))
        cats = r['카테고리']
        if isinstance(cats, str):
            cats = json.loads(cats)
        for c in cats:
            if c not in by_cat:
                unknown.add(c)
                continue
            order = r.get('순서')
            by_cat[c].append((99 if order in (None, '') else order, name, clean(r.get('짧은 설명'))))
        if clean(r.get('한 줄 소개')):
            pitch[name] = clean(r['한 줄 소개'])
        if clean(r.get('대표 사진')):
            # 이 사이트에 올린 사진은 상대경로로 (로컬 미리보기에서도 보이게)
            img[name] = clean(r['대표 사진']).replace(SITE, '')
        if r.get('최저 예산') not in (None, ''):
            minb[name] = r['최저 예산']
        lv = r.get('대상') or r.get('대상 학교급') or []   # 대상 = 학교급 선택(초등 저/고학년·중·고)
        if isinstance(lv, str):
            lv = json.loads(lv) if lv.strip() else []
        if lv:
            level[name] = lv

    empty = [c for c, v in by_cat.items() if not v]
    for c in by_cat:
        by_cat[c].sort(key=lambda x: (x[0], x[1]))
        # 노출 프로그램이 없는 카테고리는 비움 → 결과 화면에서 '매니저가 찾아드려요' 안내
        D['PROGRAMS'][c] = [[n, d] for _, n, d in by_cat[c]]

    src = src[:m.start(1)] + json.dumps(D, ensure_ascii=False) + src[m.end(1):]
    src = replace_obj(src, 'PROGRAM_PITCH', pitch)
    src = replace_obj(src, 'PROGRAM_IMG', img)
    src = replace_obj(src, 'PROGRAM_MIN', minb)
    src = replace_obj(src, 'PROGRAM_LEVEL', level)
    PAGE.write_text(src, encoding='utf-8')

    print(f'반영: 프로그램 {len(rows)}개')
    for c, v in by_cat.items():
        print(f'  {c}: ' + (' / '.join(n + (f'({minb[n]}만)' if n in minb else '') for _, n, _ in v) if v else '(없음 — 매니저 안내 문구 표시)'))
    if unknown:
        print('경고: 페이지에 없는 카테고리 →', ', '.join(sorted(unknown)))
    names = {clean(r.get('프로그램명') or r.get('프로그램 명')) for r in rows}
    nomin = sorted(names - set(minb))
    nolv = sorted(names - set(level))
    if nolv:
        print('참고: 대상 학교급이 비어 있어 학년과 무관하게 추천됨 →', ', '.join(nolv))
    if nomin:
        print('참고: 최저 예산이 비어 있어 예산과 무관하게 추천됨 →', ', '.join(nomin))
    if empty:
        print('경고: 노출 프로그램이 없는 카테고리 →', ', '.join(empty))
    return 0


if __name__ == '__main__':
    sys.exit(main())
