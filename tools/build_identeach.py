"""포티처 index.html → 아이덴티치 홈페이지 /recommend/ 페이지 생성

포티처와 같은 흐름·같은 노션 데이터를 쓰고, 겉모습과 접수만 아이덴티치용으로 바꿉니다.

    python tools/build_identeach.py

- 색: BRAND.md 값만 (Iden Blue / Gray / Yellow 배지). 그라데이션·그림자 제거
- 3D 마스코트 이미지 제거, 상단에 아이덴티치 로고
- 접수: 홈페이지 문의폼과 같은 Formspree(mlgondpj), GA4 G-VBX1FGXLX9 (+ generate_lead)
- 검색 노출 막음(noindex). 실험 버전 recommend-v2, 유입은 주소 끝 ?src=
포티처를 고친 뒤 apply_programs.py → 이 스크립트 순서로 실행하면 두 페이지가 같아집니다.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'index.html'
OUT = Path(r'C:\Users\tjdwo\claude code .AI\Folder. identeach\recommend\index.html')
FT_SITE = 'https://tjdwo3435-byte.github.io/fortitcher-recommend/'

HEAD = '''<title>4초 프로그램 추천 | 아이덴티치</title>
<meta name="description" content="몇 번만 누르면 우리 학교에 맞는 아이덴티치 프로그램을 바로 추천해 드립니다." />
<!-- 실험 페이지: 검색 노출 막음. 정식 오픈 때 index,follow + canonical + sitemap 추가 -->
<meta name="robots" content="noindex,nofollow" />
<meta property="og:type" content="website" />
<meta property="og:locale" content="ko_KR" />
<meta property="og:site_name" content="아이덴티치" />
<meta property="og:title" content="4초 프로그램 추천 | 아이덴티치" />
<meta property="og:description" content="몇 번만 누르면 우리 학교에 맞는 프로그램을 바로 추천해 드립니다." />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@1.3.9/dist/web/static/pretendard.css" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VBX1FGXLX9"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-VBX1FGXLX9');
</script>
'''

ROOT_VARS = ''':root{
    --accent:#1D2087;
    --accent-press:#181A70;
    --accent-soft:#F1F1FB;
    --ink:#1A1A1A;
    --ink-2:#484848;
    --ink-3:#767676;
    --line:#D1D1D1;
    --line-2:#E8E8E8;
    --bg:#FFFFFF;
    --frame:#F1F1FB;
    --radius:16px;
    --radius-lg:16px;
    --shadow:none;
  }'''

# 포티처 민트 계열 → BRAND.md 값
COLOR_MAP = {
    '#12B5A8': '#1D2087', '#0DA093': '#181A70', '#E6F7F5': '#F1F1FB', '#CFEFEA': '#DDDEF5',
    '#BFE9E4': '#BABCE9', '#191F28': '#1A1A1A', '#4E5968': '#484848', '#8B95A1': '#767676',
    '#E5E8EB': '#D1D1D1', '#F2F4F6': '#E8E8E8', '#EDEFF2': '#F1F1FB', '#E5484D': '#C2362B',
}


def sub1(src, pattern, repl, flags=0, count_expected=1):
    new, n = re.subn(pattern, repl, src, flags=flags)
    if n < count_expected:
        sys.exit(f'변환 실패: {pattern!r} ({n}곳)')
    return new


def main():
    s = SRC.read_text(encoding='utf-8')

    # 1) head: 제목·메타·폰트 → 아이덴티치 (noindex, GA4)
    s = sub1(s, r'<title>.*?<style>', lambda m: HEAD + '<style>', flags=re.S)
    # 2) 색 토큰
    s = sub1(s, r':root\{.*?\n  \}', ROOT_VARS, flags=re.S)
    # 3) 그라데이션·그림자 제거 (BRAND.md 10-2)
    s = s.replace('background:linear-gradient(180deg,rgba(255,255,255,0) 0%,#fff 22%)', 'background:#fff')
    s = re.sub(r'background:linear-gradient\([^;}]*\)', 'background:var(--accent-soft)', s)
    s = re.sub(r'box-shadow:[^;}]+', 'box-shadow:none', s)
    s = re.sub(r'transition:([^;}]*?),?box-shadow [^,;}]+', r'transition:\1', s)
    for a, b in COLOR_MAP.items():
        s = re.sub(re.escape(a), b, s, flags=re.I)
    s = re.sub(r'rgba\(\s*18\s*,\s*181\s*,\s*168\s*,\s*([\d.]+)\)', r'rgba(29,32,135,\1)', s)
    s = s.replace('background:rgba(13,160,147,.18)', 'background:transparent')      # 3D 이미지 그림자
    s = s.replace('background:rgba(25,31,40,.45)', 'background:#0C0D36')            # 팝업 뒤 면: 반투명 대신 불투명 (BRAND 10-2)
    # 비활성 버튼: 흰 글자 대신 Gray 60 (BRAND.md 6절)
    s = s.replace('.cta:disabled{background:#D6DBE0;color:#fff;', '.cta:disabled{background:#E8E8E8;color:#767676;')
    s = s.replace('.mini-cta:disabled{background:#D6DBE0;', '.mini-cta:disabled{background:#E8E8E8;color:#767676;')
    # 추천 배지는 옐로 포인트 (10%)
    s += ''
    s = s.replace('</style>', '''  .p-rec,.rec-card .rank,.m-rank,.direct-tag{background:#FFD84D !important;color:#1A1A1A !important;}
  .brandbar .blink{display:block;width:132px;height:38px;overflow:hidden;flex:0 0 auto;}
  .brandbar .blogo{width:147px;height:auto;max-width:none;margin:-24px 0 0 -7px;display:block;}  /* logo.webp 여백 잘라 로고 가로 약 132px (BRAND 9-3 최소 120px) */
  .brandbar .bsub{color:var(--ink-2) !important;}
  .cta,.mini-cta,.more-btn{border-radius:999px !important;}
</style>''', 1)

    # 4) 3D 마스코트 제거
    s = sub1(s, r'var IMAGES = \{.*?\n  \};', "var IMAGES = { hero:'', loading:'', done:'' };", flags=re.S)
    s = sub1(s, r"return '<div class=\"img-ph\"[^\n]*", "return '';")

    # 5) 상단 브랜드 바: 포티처 → 아이덴티치 로고
    s = sub1(s, r"var html='<div class=\"brandbar\">.*?</div>';",
             "var html='<div class=\"brandbar\"><a class=\"blink\" href=\"/\" aria-label=\"아이덴티치 홈\"><img class=\"blogo\" src=\"/assets/images/logo.webp\" alt=\"아이덴티치\" /></a><span class=\"bsub\">4초 프로그램 추천</span></div>';")

    # 6) 접수: FormSubmit → Formspree, 실험 버전·유입 경로·전환 이벤트
    s = sub1(s, r"var CONFIG = \{[^\n]*",
             "var CONFIG = { cobraEmail:'idengroup@naver.com', formEndpoint:'https://formspree.io/f/mlgondpj', variant:'recommend-v2' };\n"
             "  var SRC=(location.search.match(/[?&]src=([^&]+)/)||[])[1]||'direct';")
    s = sub1(s, r"fetch\('https://formsubmit\.co/ajax/'\+encodeURIComponent\(to\),\{", "fetch(CONFIG.formEndpoint,{", count_expected=2)
    s = s.replace("_template:'table',", '')
    s = sub1(s, r"'개인정보 수집·이용 동의':", "'실험 버전':CONFIG.variant,'유입':SRC,'개인정보 수집·이용 동의':", count_expected=2)
    s = s.replace("'[포티처] '", "'[추천받기] '")
    s = sub1(s, r"function track\(n,p\)\{[^\n]*",
             "function track(n,p){ try{ if(window.gtag) window.gtag('event',n,Object.assign({variant:CONFIG.variant,src:SRC},p||{})); }catch(e){} }")
    s = sub1(s, r"track\('lead_sent',\{\}\);", "track('lead_sent',{});track('generate_lead',{form:'recommend'});")
    s = sub1(s, r"track\('lead_sent',\{direct:true\}\);", "track('lead_sent',{direct:true});track('generate_lead',{form:'recommend-direct'});")
    s = s.replace('포티처', '아이덴티치')

    # 7) 포티처 사이트에 있는 사진은 절대주소로
    s = s.replace('"img/programs/', '"' + FT_SITE + 'img/programs/')

    bad = re.findall(r'6C47D6|5836C0|691AFA|FF7A4D|14142B|18142E|1F2392|171980|linear-gradient|#12B5A8|#0DA093', s, flags=re.I)
    if bad:
        sys.exit('금지 값 남음: ' + ', '.join(sorted(set(bad))))
    OUT.write_text(s, encoding='utf-8')
    print('생성:', OUT, f'{len(s.encode()):,} bytes')


if __name__ == '__main__':
    main()
