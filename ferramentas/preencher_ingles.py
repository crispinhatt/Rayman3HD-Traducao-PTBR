#!/usr/bin/env python3
"""Cria uma planilha LOCAL com o inglês do SEU jogo ao lado da tradução.

Serve para quem quer revisar ou continuar a tradução. Lê os arquivos do seu
jogo (nada é enviado a lugar nenhum), confere o hash de cada string e grava
traducao_com_ingles_local.csv. NÃO publique esse arquivo: ele contém o texto
original da Ubisoft.

Uso:
  python preencher_ingles.py ..\\traducao\\traducao_ptbr.csv  <pasta GAMEDATAbin>  saida.csv
  (a pasta GAMEDATAbin fica em  data\\content\\GAMEDATAbin  na instalação)
"""
import csv, hashlib, os, struct, sys, collections

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(1)
    src, pasta, saida = sys.argv[1:]
    fix = open(os.path.join(pasta, 'fix.lvl'), 'rb').read()
    sub = open(os.path.join(pasta, 'VS.sub'), 'rb').read()

    # --- legendas: VS.sub = u16 n | n registros de 20 bytes | u16 n | n x (u16 tam + texto)
    n = struct.unpack('<H', sub[:2])[0]
    recs, p = [], 2
    for _ in range(n):
        recs.append(sub[p:p + 20]); p += 20
    p += 2
    textos = []
    for _ in range(n):
        L = struct.unpack('<H', sub[p:p + 2])[0]; p += 2
        textos.append(sub[p:p + L]); p += L
    cont = collections.Counter(); legendas = {}
    for rr, t in zip(recs, textos):
        flags, filme = struct.unpack('<II', rr[:8])
        lang = flags & 0xFF                      # 1 = inglês
        i = f'vs.en.{filme}.{cont[(lang, filme)]}'; cont[(lang, filme)] += 1
        if lang == 1:
            legendas[i] = (sha(rr + t), t.decode('latin-1'))

    ok = ruim = 0
    with open(src, encoding='utf-8-sig', newline='') as f, \
         open(saida, 'w', encoding='utf-8-sig', newline='') as g:
        r = csv.DictReader(f, delimiter=';')
        w = csv.writer(g, delimiter=';', quoting=csv.QUOTE_ALL)
        w.writerow(['tipo', 'chave', 'bytes_orig', 'ingles', 'ptbr', 'hash_orig'])
        for row in r:
            if row['tipo'] == 'text':
                off = int(row['chave']); e = fix.index(b'\0', off)
                slot = fix[off:off + (((e - off + 1) + 3) // 4 * 4)]
                h, en = sha(slot), fix[off:e].decode('latin-1')
            else:
                h, en = legendas[row['chave']]
            if h == row['hash_orig']: ok += 1
            else: ruim += 1; print('hash diferente:', row['chave'])
            w.writerow([row['tipo'], row['chave'], row['bytes_orig'], en, row['ptbr'], row['hash_orig']])
    print(f'{ok} linhas conferem com o seu jogo; {ruim} diferentes.')

if __name__ == '__main__':
    main()
