# Como funciona

Notas técnicas sobre o mod. O sistema de mods do Rayman 3 HD Recompiled só aceita **dados**: um `mod.json` (e PNGs).
Na inicialização, o port aplica os overrides em memória por cima dos dados do jogo; nada no disco é alterado.

## Onde está o texto

| Arquivo (em `data\content\GAMEDATAbin`) | Conteúdo |
|---|---|
| `fix.lvl` | Todos os textos do jogo, **5 idiomas** em blocos separados (FR, EN, ES, IT, DE), em **Latin-1** de 1 byte por caractere |
| `fix.ptr` | Tabela de ponteiros (relocações) que apontam para as strings |
| `VS.sub` | Legendas das cutscenes (também 5 idiomas) |

O port roda em inglês, então o mod troca os **1.051 slots do bloco inglês** do `fix.lvl` (offsets 72496 a 190228) e as
**69 legendas em inglês** do `VS.sub`.

## Slots de texto

- Cada string termina em NUL e ocupa um *slot* alinhado a 4 bytes (texto + NUL + zeros até múltiplo de 4).
- `slot_sha256` = SHA-256 desses bytes do slot inteiro. Se o hash não bate, o mod é recusado em vez de aplicado errado.
- Texto maior que o slot é permitido: o empacotador realoca as strings para o espaço liberado pelas mais curtas e atualiza os ponteiros do `fix.ptr`. O orçamento total de espaço do bloco é de cerca de 54 KB; a tradução usa uma fração menor que isso, mas por isso algumas frases foram encurtadas.
- Uma string só pode ser movida se houver ponteiro para ela e nenhum ponteiro apontar para o meio dela. Se o `pack` recusar com `TEXT_TOO_LONG`, é preciso encurtar a frase indicada.

## Legendas (`VS.sub`)

Formato (little-endian): `u16 n` | `n` registros de 20 bytes | `u16 n` | `n` × (`u16 tamanho` + texto).

Cada registro de 20 bytes é `u32 flags | u32 filme | u32 início_ms | u32 fim_ms | u32 índice`. O byte baixo de `flags` é o
idioma: **1 = inglês, 2 = francês, 3 = espanhol, 4 = italiano, 5 = alemão**. O id usado no `mod.json` é
`vs.en.<filme>.<cue>`, onde `cue` conta as legendas daquele filme **dentro do idioma**. O `source_sha256` é o SHA-256 dos
**20 bytes do registro seguidos dos bytes do texto**. Tempo, ordem e quantidade de legendas não mudam.

## Fonte e acentos

A fonte do jogo (`FontRay`) já define todo o Latin-1 usado pelo português: `á à â ã é ê í ó ô õ ú ü ç` e as maiúsculas.
Por isso o mod **não precisa de overrides `glyph`** (o mod turco precisa, para ş ğ ı İ). Caracteres que a fonte não tem:
`; < > { }` e também `ª º`; o `gerar_mod.py` recusa os proibidos. Para "nº" foi usado "n°".

## Códigos de controle

Aparecem dentro do texto e precisam ser mantidos:

| Código | Efeito |
|---|---|
| `\l` | quebra de linha manual (pode ser movida) |
| `\jc` | centraliza a linha |
| `\f1:c` ... `\f0:` | ícone de botão do controle (entre `\f1:` e `\f0:`) |
| `\z145:` | parâmetro de layout em alguns textos de ajuda |
| `\c255:255:255:` | cor RGB do texto |
| `$...$` | delimitadores que o jogo exibe como aspas |

O `gerar_mod.py` compara esses códigos com os do original (quando a planilha tem a coluna `ingles`) e recusa diferenças.

## Limites do formato de mod

Até 4.096 overrides por mod (este usa 1.094), arquivos `.json`, `.png`, `.txt`, `.md`, e nada que seja código.

## Decisões de tradução

- Nomes mantidos: Hoodlums, Teensies, Lums, Leptys, Knaarens, Glute, Murfy, Globox, Razoff, Reflux, Begoniax e os nomes de criaturas do bestiário.
- Fases e itens traduzidos (por exemplo, "O Pântano Sombrio", "QG dos Hoodlums", "Jaula", "Ameixa").
- Botões: "aperte" (e não "pressione") nas dicas de controle, também para economizar espaço.
- Espaços duplos depois de pontuação foram reduzidos a um para caber no orçamento de bytes.
- Humor adaptado ao português do Brasil quando o trocadilho original não funciona.
