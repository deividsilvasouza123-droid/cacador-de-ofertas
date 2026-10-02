from __future__ import annotations
import csv, json, os, re, random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / 'data' / 'produtos.csv'
OUT = ROOT / 'output' / 'roteiros'
OUT.mkdir(parents=True, exist_ok=True)

CATEGORY_MAP = {
    'copo': 'Casa, cozinha e utilidades', 'panela': 'Casa, cozinha e utilidades', 'cozinha': 'Casa, cozinha e utilidades',
    'espelho': 'Casa, decoração e organização', 'organizador': 'Casa, organização', 'limpeza': 'Casa, limpeza',
    'varal': 'Casa, organização', 'maquiagem': 'Beleza', 'perfume': 'Beleza', 'body splash': 'Beleza',
    'fone': 'Gadgets/eletrônicos', 'power bank': 'Gadgets/eletrônicos', 'carregador': 'Gadgets/eletrônicos',
    'smartwatch': 'Gadgets/eletrônicos', 'led': 'Gadgets/eletrônicos', 'bicicleta': 'Fitness',
    'churrasqueira': 'Casa, cozinha e utilidades', 'pet': 'Pet', 'cachorro': 'Pet', 'gato': 'Pet'
}

ANGLES = [
    ('Curiosidade', 'POR QUE EU NÃO TINHA ISSO ANTES? 👀'),
    ('Problema→solução', 'Se isso também te incomoda, olha essa solução.'),
    ('Demonstração', 'Olha o que esse negócio faz na prática.'),
    ('Economia', 'Tem coisa simples que evita gastar mais depois.'),
    ('Desejo', 'Pronto. Agora eu preciso de um desses.'),
]


def money(s: str) -> float:
    m = re.sub(r'[^0-9,.-]', '', s or '').replace('.', '').replace(',', '.')
    try: return float(m)
    except Exception: return 0.0


def pct(s: str) -> float:
    m = re.sub(r'[^0-9,.-]', '', s or '').replace(',', '.')
    try: return float(m)
    except Exception: return 0.0


def sales_score(s: str) -> float:
    s = (s or '').lower().replace('mil', '000').replace('+', '')
    m = re.search(r'(\d+(?:[.,]\d+)?)', s)
    return float(m.group(1).replace(',', '.')) if m else 0


def category(name: str) -> str:
    n = name.lower()
    for k, v in CATEGORY_MAP.items():
        if k in n: return v
    return 'Achadinhos gerais'


def rank_products(rows: list[dict[str, str]], used_ids: set[str], n: int) -> list[dict[str, str]]:
    candidates = [r for r in rows if r['Item Id'] not in used_ids]
    for r in candidates:
        sales = sales_score(r['Sales'])
        comm = pct(r['Commission Rate'])
        price = money(r['Price'])
        # Prioriza tração, comissão e ticket acessível; mantém equilíbrio entre categorias.
        r['_score'] = sales * 1.0 + comm * 3.0 + max(0, 40 - price) * 0.05
        r['Categoria'] = category(r['Item Name'])
    candidates.sort(key=lambda x: x['_score'], reverse=True)
    return candidates[:n]


def build_fallback(r: dict[str, str]) -> list[dict[str, Any]]:
    name = r['Item Name'].strip()
    price = r['Price'].strip()
    link = r['Offer Link'].strip()
    short_name = name[:78] + ('…' if len(name) > 78 else '')
    out=[]
    for angle, default_hook in ANGLES:
        hook = default_hook
        if angle == 'Demonstração':
            voice = f'Olha como o {short_name} funciona na prática.'
        elif angle == 'Problema→solução':
            voice = f'Eu estava procurando uma forma mais prática para isso e achei o {short_name}.'
        elif angle == 'Economia':
            voice = f'Antes de gastar mais, olha essa opção: {short_name}.'
        elif angle == 'Desejo':
            voice = f'Depois de ver isso, eu colocaria na minha lista de achadinhos: {short_name}.'
        else:
            voice = f'Você também ainda não tinha visto o {short_name}?'
        scene = (
            f'Vídeo vertical 9:16, 8–15s, UGC brasileiro realista, ambiente doméstico comum, câmera de celular, '
            f'luz natural. Mostrar fielmente o produto "{name}"; nada de embalagem ou recurso que não esteja no cadastro. '
            f'Começar com o hook, depois mostrar o produto em uso por alguns segundos e finalizar com CTA.'
        )
        google = f'''Crie um vídeo vertical 9:16 de 8–15 segundos para afiliado brasileiro. Produto: {name}. Preço cadastrado: R$ {price}. Hook: {hook}. {scene} Narração em português-BR, natural, sem voz de apresentador publicitário. Texto na tela curto. CTA final: "Confere o preço no link." Não invente especificações, desconto ou funções.'''
        yt = f'''UGC BR 9:16, 8–15s. Produto: {short_name}. Hook: {hook} Mostrar uso real em casa, câmera celular, natural, sem cara de IA. PT-BR. Final: “Confere o preço no link.”'''
        out.append({'angle': angle, 'hook': hook, 'scene': scene, 'voiceover': voice, 'on_screen_text': hook, 'cta': 'Confere o preço no link.', 'google_flow_prompt': google, 'yt_creat_prompt': yt, 'offer_link': link})
    return out


def maybe_openai(r: dict[str, str]) -> list[dict[str, Any]] | None:
    key = os.getenv('OPENAI_API_KEY')
    if not key: return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        model = os.getenv('OPENAI_MODEL', 'gpt-6-luna')
        instruction = (ROOT/'prompts'/'master_prompt.txt').read_text(encoding='utf-8')
        inp = json.dumps({
            'id': r['Item Id'], 'name': r['Item Name'], 'price': r['Price'], 'sales': r['Sales'],
            'commission_rate': r['Commission Rate'], 'offer_link': r['Offer Link'], 'category': r.get('Categoria','')
        }, ensure_ascii=False)
        resp = client.responses.create(model=model, input=instruction + '\nPRODUTO:\n' + inp)
        text = resp.output_text
        start = text.find('['); end = text.rfind(']')
        if start >= 0 and end > start:
            data = json.loads(text[start:end+1])
            for x in data: x['offer_link'] = r['Offer Link']
            return data
    except Exception as exc:
        print('OpenAI fallback:', type(exc).__name__, str(exc))
    return None


def load_rows() -> list[dict[str,str]]:
    with PRODUCTS.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main() -> None:
    batch = int(os.getenv('BATCH_SIZE', '5'))
    used_file = ROOT/'data'/'processados.txt'
    used = set(used_file.read_text(encoding='utf-8').splitlines()) if used_file.exists() else set()
    rows = load_rows()
    selected = rank_products(rows, used, batch)
    manifest=[]
    for r in selected:
        scripts = maybe_openai(r) or build_fallback(r)
        obj = {'product': r, 'scripts': scripts}
        stamp = r['Item Id']
        (OUT/f'{stamp}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
        md = [f"# {r['Item Name']}", '', f"Preço cadastrado: R$ {r['Price']}", f"Vendas: {r['Sales']}", f"Comissão: {r['Commission Rate']}", f"Link: {r['Offer Link']}", '']
        for i,s in enumerate(scripts,1):
            md += [f"## Ângulo {i}: {s['angle']}", f"**Hook:** {s['hook']}", f"**Voz:** {s.get('voiceover','')}", f"**CTA:** {s.get('cta','')}", '', '**Google Flow**', s['google_flow_prompt'], '', '**YT CREAT**', s['yt_creat_prompt'], '']
        (OUT/f'{stamp}.md').write_text('\n'.join(md), encoding='utf-8')
        manifest.append({'product_id': stamp, 'product_name': r['Item Name'], 'offer_link': r['Offer Link'], 'scripts': scripts})
    with used_file.open('a', encoding='utf-8') as f:
        for r in selected: f.write(r['Item Id']+'\n')
    (ROOT/'output'/'roteiros'/'latest_batch.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Produtos selecionados:', len(selected))
    for r in selected: print(r['Item Id'], r['Item Name'][:80])

if __name__ == '__main__': main()
