#!/usr/bin/env python3
"""Gera o mod.json do Rayman 3 HD Recompiled a partir da planilha de tradução.

Uso:
  python gerar_mod.py ..\\traducao\\traducao_ptbr.csv ..\\mod
  (depois)  app\\python\\python.exe app\\tools\\r3hd_modkit.py --home . pack saida\\rayman3-ptbr rayman3-ptbr.zip

Só as linhas com a coluna "ptbr" preenchida entram no mod.
Se a planilha tiver a coluna "ingles" (veja preencher_ingles.py), os códigos de controle
(\\f1:c, \\jc, \\c...) são conferidos contra o original.
Opções:  --id, --name, --version, --autor, --glyphs arquivo.json (lista de overrides "glyph")
"""
import argparse, csv, json, os, re, sys

BAD = set(';<>{}')          # a fonte do jogo não tem estes caracteres
TOKEN = re.compile(r'\\f[1-9]:\s?[^\\\s]|\\f\d:|\\hm\d+:|\\z\d+:|\\jc|\\c\d+:\d+:\d+:')   # códigos que NÃO podem mudar (\l pode)
LATIN1_OK = set(chr(c) for c in range(32, 127)) | set(chr(c) for c in range(0xA0, 0x100))

def tokens(s):
    return [re.sub(r'\s', '', t) for t in TOKEN.findall(s)]   # '\f1: b' e '\f1:b' valem o mesmo

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv'); ap.add_argument('saida')
    ap.add_argument('--id', default='pinhatt.rayman3-ptbr')
    ap.add_argument('--name', default='Português (Brasil)')
    ap.add_argument('--version', default='0.1.0')
    ap.add_argument('--autor', default='PINHATT')
    ap.add_argument('--glyphs', default=None)
    a = ap.parse_args()

    overrides, erros, avisos = [], [], []
    nao_latin1 = {}
    n_text = n_sub = 0
    with open(a.csv, encoding='utf-8-sig', newline='') as f:
        for ln, r in enumerate(csv.DictReader(f, delimiter=';'), start=2):
            pt = r['ptbr']
            if pt.strip() == '':
                continue
            en, chave, tipo = r.get('ingles'), r['chave'], r['tipo']
            tag = f'linha {ln} ({tipo} {chave})'
            bad = sorted(set(pt) & BAD)
            if bad:
                erros.append(f'{tag}: caracteres que a fonte não tem: {" ".join(bad)}')
            if en is not None and tokens(en) != tokens(pt):
                erros.append(f'{tag}: códigos de controle diferentes do inglês  {tokens(en)}  ->  {tokens(pt)}')
            for ch in set(pt):
                if ch not in LATIN1_OK:
                    nao_latin1.setdefault(ch, []).append(ln)
            if tipo == 'text':
                if len(pt.encode('latin-1', 'replace')) + 1 > int(r['bytes_orig']):
                    avisos.append(f'{tag}: maior que o espaço original ({r["bytes_orig"]} bytes)')
                overrides.append({'type': 'text', 'file': 'GAMEDATAbin/fix.lvl',
                                  'offset': int(chave), 'slot_sha256': r['hash_orig'], 'text': pt})
                n_text += 1
            elif tipo == 'subtitle':
                overrides.append({'type': 'subtitle', 'id': chave,
                                  'source_sha256': r['hash_orig'], 'text': pt})
                n_sub += 1
            else:
                erros.append(f'{tag}: tipo desconhecido')
    if a.glyphs:
        with open(a.glyphs, encoding='utf-8') as f:
            g = json.load(f)
        overrides = g + overrides
    for ch, lns in sorted(nao_latin1.items()):
        avisos.append(f'caractere "{ch}" (U+{ord(ch):04X}) fora do Latin-1 em {len(lns)} linha(s) — precisa de glifo')
    if erros:
        print('ERROS (corrija na planilha):')
        for e in erros: print('  -', e)
        sys.exit(1)
    mod = {
        'format': 1, 'id': a.id, 'name': a.name, 'version': a.version,
        'description': 'Tradução para português do Brasil dos textos, menus e legendas.',
        'authors': [a.autor], 'license': 'Tradução de fãs. Texto original © Ubisoft. Para uso com a sua própria cópia do jogo.',
        'target': {'title_id': '5841123F', 'releases': ['x360-xbla-5841123F-v1'], 'min_port_version': '0.36.0'},
        'requires': [], 'conflicts': [], 'overrides': overrides,
    }
    os.makedirs(a.saida, exist_ok=True)
    with open(os.path.join(a.saida, 'mod.json'), 'w', encoding='utf-8') as f:
        json.dump(mod, f, ensure_ascii=False, indent=1)
    print(f'OK: {n_text} textos + {n_sub} legendas -> {os.path.join(a.saida, "mod.json")}')
    for w in avisos: print('  aviso:', w)

if __name__ == '__main__':
    main()
