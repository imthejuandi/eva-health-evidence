# Manifest of the evidence record

AI work product. Made by `make-evidence.py` on 2026-11-11T22:11:37Z. Transcript snapshot: 2026-11-11T21:01:49Z.
Repository: `claude/wonderful-meitner-l4g7p5` at commit `e5b42ff13608`, read through git on 2026-11-11T22:11:30Z.
Scratch folder: read from 21:38 UTC on 11 November 2026 to 2026-11-11T21:47:54Z.
Every item has its size and sha256. Sizes use binary units (1 MB = 1024 x 1024 bytes). Files in the repository are
listed by path, grouped by workstream and by the day they last changed. A folder with many files is listed once, with
its file count and a combined hash (the sha256 of its sorted `sha256  path` lines); `manifest.json` lists every file.

## 1. This record's own files

| File | Size | sha256 | What it is |
|---|---|---|---|
| `DELETIONS.md` | 355.1 KB | `d488ac6ac5eb59c1b07b598db9890c0dc0f51f28336f9c4e11f72f5dbb41d7c0` | What was deleted in the session, what it held, what survives |
| `README.md` | 5.6 KB | `a362a5f79160f34283db48df0fb553b709a11c5f5ebb4026b930e739cb461c01` | How to read the record, check a claim and unpack the archives |
| `TESTS-SUMMARY.md` | 4.4 MB | `4491f8938c24baca77bebf6340502fecea043caf70005d49981734e38f3d55de` | Every test and check run, in time order, with outcomes and proof; statements to the CEO traced |
| `dsrt-fixtures.json` | 2.7 MB | `3694cf8be7602f6d12b47b143b2bdcf76e140295f79e7c67eda5863485d87a2c` | The same, one row per folder |
| `dsrt-fixtures.md` | 7.1 KB | `55702e87ad5ee3bab6efd8810253b9547c9301780d74adbea3c03663d7b4e322` | The /tmp/dsrt-* test fixtures, by prefix, with the test that makes them |
| `make-evidence.py` | 171.3 KB | `811094078131e0ac96b006e865dc43664cb8d21e8b4b499f01ff9d02b8aed0d5` | The script that rebuilds this record |
| `redactions.json` | 52.9 KB | `00f4a3db57c743094266a085c828130384667c80d10772e8493dd4a1c3343ae6` | The same, as data |
| `redactions.md` | 34.1 KB | `d27168d3eb5e468e48265a75af52d023df4264877627920f2adf337d9101164c` | Every redaction by file and kind (no values) |
| `tests.json` | 16.0 MB | `911b1280277a7f65d64f4077701ea01d5382f2c2a4afc92dc9438601ce56ad4f` | The same, as data, with every command in full |
| `transcripts/SHA256SUMS` | 552 B | `7fd0b1368b30f7ede8b43cf88e1fc172ea669c350af64aeaae08de0c4e8080eb` | Checksums of the transcript parts (sha256sum -c) |
| `transcripts/parts.json` | 1.5 MB | `d18b68a7824ed674ebbdc607752358ed843f796f1a87c23b01a8ccc4a019744b` | Every transcript file: its part, size and sha256 before and after scrubbing |
| `scratch/SHA256SUMS` | 176 B | `0503a5d075cb0b17d53b0bf1f20ac888b2b9a8d8175871a82ab2312e1eaf9212` | Checksums of the scratch parts (sha256sum -c) |
| `scratch/parts.json` | 7.2 MB | `10c62989df4d5292fa51d7d7d9b99f18d99763f38c4dfdda318094b9bc8eea86` | Every scratch file: its part, size and sha256; what was left out and why |

## 2a. Archive: transcripts

Every command run and every output, in the main conversation and in every agent, workflow and tool-result file, as of the snapshot (scrubbed).

| Part | Size | sha256 | Files | First file | Last file |
|---|---|---|---|---|---|
| `transcripts/transcripts.part01.tar.xz` | 38.5 MB | `de6555f7d808630246cfccaa6050bb6f5e571ca24a76169bcd2c0e39ddad7c49` | 555 | `4e1a7523-c199-547a-904f-d87e53286958.jsonl` | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_1fa21b90-dde/agent-a74f169ea5bb8888e.prefix.json` |
| `transcripts/transcripts.part02.tar.xz` | 38.7 MB | `365fefb7069e77adff995a47186e4e99a39637cfe1f697cdacdb2529ae8ab1ea` | 467 | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_1fa21b90-dde/agent-a774c860776006570.jsonl` | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-ab4871eb18f26b4ac.prefix.json` |
| `transcripts/transcripts.part03.tar.xz` | 38.8 MB | `6fa8082ae9333fec7683cb10e57f57a71f6f8d7d4d3b184e8b65f3d0a1771304` | 376 | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-ad77e7e302ced1e0f.jsonl` | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_62eb781c-732/journal.jsonl` |
| `transcripts/transcripts.part04.tar.xz` | 38.7 MB | `08b349cdfb7bf744bc8f5b1a3ae00bc08b54560a01dc86a2079314ba01eb6a56` | 464 | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_68660c94-81e/agent-a063dc6f3a337a0f3.jsonl` | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a392dadad7da9c59e.prefix.json` |
| `transcripts/transcripts.part05.tar.xz` | 35.6 MB | `49cb338c4242e26f62215b811c0f703cb3075cb60b7423ac040542314fee7752` | 291 | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a3941642a3115dbce.jsonl` | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_c864fee6-8a6/agent-a8f413880597e40aa.prefix.json` |
| `transcripts/transcripts.part06.tar.xz` | 23.1 MB | `90c6c3d59854cd15f7a21bcb5327e422543b457e87512e426382d8afd8732a8e` | 949 | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_c864fee6-8a6/agent-ac5b98a1561a166da.jsonl` | `4e1a7523-c199-547a-904f-d87e53286958/ccr-tip.json` |

## 2b. Archive: scratch folder

The scratch folder's reports, reviews, test logs, DSRT results and compiles, and the background commands' outputs, as of the snapshot (scrubbed).

| Part | Size | sha256 | Files | First file | Last file |
|---|---|---|---|---|---|
| `scratch/scratch.part01.tar.xz` | 39.0 MB | `a94523c257e2b70d1ad6a437791e7cc4e3582e052888dd0179b35196d3df3974` | 7837 | `scratchpad/B01-r1-payload.json` | `scratchpad/merge-work/discover_spanish-spanish.json` |
| `scratch/scratch.part02.tar.xz` | 37.6 MB | `a54680930620934914be507f918c20ae1d4db054505f93b8c1ac58392ea69bf5` | 13373 | `scratchpad/merge-work/merged_evidence.json` | `tasks/aec43198f6bde0a6d.output` |

### What the transcript parts hold

| Kind | Files | Size at snapshot | First entry (UTC) | Last entry (UTC) |
|---|---|---|---|---|
| main conversation | 1 | 57.5 MB |  |  |
| background agents | 56 | 53.7 MB |  |  |
| agent metadata | 1489 | 12.9 MB |  |  |
| workflow agents | 752 | 1.1 GB |  |  |
| workflow run records and scripts | 82 | 8.1 MB |  |  |
| tool results (full outputs) | 721 | 46.8 MB |  |  |
| other | 1 | 89 B |  |  |

## 3. Committed proof in the repository, by workstream and date

### WS0 gates and plan

79 files, 2.0 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 

### WS1 ranges by family

3110 files, 66.9 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 

### WS1-K compile

744 files, 268.0 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 

### Central reviews and approvals

31 files, 2.5 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 

### Governance

24 files, 1.4 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 

### WS3 score

6 files, 859.6 KB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 

### WS1 mop-up round

45 files, 1.9 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 

### WS2 biological age v3

197 files, 4.0 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 

### Biological age and score analyses

22 files, 245.2 KB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 

### Biological age add-ons (October)

143 files, 2.0 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 

### Biomarker evidence (October)

796 files, 15.6 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 

### Audit and calibration reports

52 files, 1.8 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 
 
 
 
 
 
 
 
 
 

### Seed data and migrations

62 files, 2.6 MB.

| Last changed | Path | Files | Size | sha256 | What it proves |
|---|---|---|---|---|---|
 
 

## 4. Proof in the scratch folder (inside the scratch archive), by workstream

| Workstream | Folder | Files | Size | Dates | Combined sha256 |
|---|---|---|---|---|---|
| Background command outputs | `tasks/` | 183 | 7.7 MB | 2026-10-28 to 2026-11-11 | `e6de2082647c6636453e35c8ab804c730cd0bdd9192a47d7e8da350b998860af` |
| Biomarker evidence and biological age (October) | `scratchpad/bioage-scripts/` | 18 | 89.1 KB | 2026-10-28 to 2026-10-29 | `92ce49834c1bcbf21c5afa4cc2eb3dbe5cdfac88fcbea986d328827cec11d694` |
| Biomarker evidence and biological age (October) | `scratchpad/biomarcare-al-scripts/` | 2 | 101.3 KB | 2026-10-28 | `ebe5f9e9446a2db698f37b6e010d952002b6895e9c632fec71439a27dee9abdb` |
| Biomarker evidence and biological age (October) | `scratchpad/kdm-v22-refute-scripts/` | 1 | 470 B | 2026-10-28 | `a1a8af12faabb7f6b0fea7e818928d138f770ae6f5fb1dcba9c8d4b7a32772a1` |
| Biomarker evidence and biological age (October) | `scratchpad/biograma-scripts/` | 3 | 2.8 KB | 2026-10-28 | `db8f572d711102e297a15e1fcbc39f222c4c4a803033f972fe0c2338e2b664ff` |
| Biomarker evidence and biological age (October) | `scratchpad/critic-scripts/` | 2 | 949 B | 2026-10-28 | `6ee0f9f78c47a56b6ab8ab48516f7cbff6883d08bb94e0d274ce9ba8222d3fdf` |
| Biomarker evidence and biological age (October) | `scratchpad/ (files at the top)` | 6 | 367.8 KB | 2026-10-28 to 2026-11-10 | `7adf4a4854a3d53db2b1e3616a3b7df8c1034d987c56d2261c0161a5b692f851` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_repisalud/` | 2 | 935.0 KB | 2026-10-29 | `f093c5695dd13718d32b76f0578304992c77505f7154833e163db7a2a6da09b6` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_pesa/` | 1 | 5.4 KB | 2026-10-29 | `4d3bb26069ea6c094d9f916d49fd6dac3315e35fe5d936af75cd1b0ad15b6156` |
| Biomarker evidence and biological age (October) | `scratchpad/deliverables/` | 7 | 763.5 KB | 2026-10-29 | `84d9520e41016f2c72e41f18c920d329435fe98138464ef140d0cf1d43e7aa8f` |
| Biomarker evidence and biological age (October) | `scratchpad/cite/` | 1 | 6.2 KB | 2026-10-29 | `1fd666cca81193f7290d38638b2dc85e293021944bd30c3a4f479418df0b6c10` |
| Biomarker evidence and biological age (October) | `scratchpad/cysc/` | 790 | 51.4 MB | 2026-10-29 | `565864ddba670be327f55b9995511352b0edd20e9748e29eab3c8c77ab6fcff4` |
| Biomarker evidence and biological age (October) | `scratchpad/cite2/` | 3 | 3.0 KB | 2026-10-29 | `50d2477ae7c79942334be91fd321d0d8f94c842ae1eba8361e68e138a8eb2ecd` |
| Biomarker evidence and biological age (October) | `scratchpad/cite3/` | 9 | 68.1 KB | 2026-10-30 | `fa8f1eb7e34f53436412b7eab983bd034df178eb424e81ba511ff663f4543b97` |
| Biomarker evidence and biological age (October) | `scratchpad/abs/` | 132 | 4.0 MB | 2026-11-06 to 2026-11-09 | `4ee77be66655005386c2df63d5c82281510a3a3792c2171df1126424aa6255e2` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_labcli/` | 3 | 278.5 KB | 2026-11-08 | `fe966a4c556b1daaf0d088e8889b91984201db709535eadf9e42b181461144ac` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_mft/` | 2 | 130.7 KB | 2026-11-08 | `bee9a9475be815f3aae42e7e88f8c4ffb3b0635f7628d8d59b65bb70e76fc5b5` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_biomed/` | 2 | 62.8 KB | 2026-11-08 | `b30acf8d7acd8498429c0f4a3b5643ef80c6f802c1d9aa8259747a9441d25542` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_ling/` | 1 | 125.7 KB | 2026-11-08 | `3b6fd031cf0fa0b0df23f77692f7b054448a90b609352c6aa729b98c608da83d` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_pubmed/` | 20 | 63.0 KB | 2026-11-08 to 2026-11-09 | `0cb7271a9d8f7f41054bdc1b6e552050643422c3c8097abba5b0060d4970b12f` |
| Biomarker evidence and biological age (October) | `scratchpad/abstracts/` | 39 | 1.3 MB | 2026-11-08 to 2026-11-09 | `e14096e37c7e161a83dbef264cd6eec56c53e3122345fc9d4ec2c6eaf75ef441` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_ada/` | 4 | 642.0 KB | 2026-11-08 | `850271a82f28f8496bdef82a92eded028fab0e37a4aba181a6a31f9f603d0da0` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_epmc/` | 5 | 187.7 KB | 2026-11-08 to 2026-11-09 | `322faea6d0869f6ec7e9919e92448b09f98aa27f3e5d0f671e09a25ff01bde8f` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_konta/` | 2 | 107.5 KB | 2026-11-08 | `4812585b568b1110026bd293423f9c3f142bb31400fc699861f9ad14e9f3ab8a` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_tseng/` | 2 | 200.5 KB | 2026-11-08 | `b3db2b0528e18ff15019e9c1c8125b92ee68eea05b136fbdae177718cc1a6c1c` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_abs/` | 6 | 15.9 KB | 2026-11-08 | `839f82014e828d982296661c3f680cbfa1e625167571ceb55c5878b132c72e96` |
| Biomarker evidence and biological age (October) | `scratchpad/web/` | 29 | 3.4 MB | 2026-11-08 to 2026-11-09 | `3a00fd95f660ec8dffc6e06218b1747d78ce17a058676a4424c3867df3de805f` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_nla/` | 2 | 351.0 KB | 2026-11-08 to 2026-11-09 | `80e184c5cde616dddf5863d2ce8a10fe25b54630cdbacf3808851a9a29b8aa0d` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_aspree/` | 1 | 92.7 KB | 2026-11-09 | `54c039fd78165e0123ace08389b70c0d0c846d68c476df8cc1d62466d2d51720` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_biosfer/` | 2 | 133.0 KB | 2026-11-09 | `1eed24e23cc54f8fac9699856e38ca3fcb7a8b96390e88685478b18c7de9d29e` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_pmc12427746/` | 2 | 215.6 KB | 2026-11-09 | `dd18bdf48a0de59f39dabfcba4f3b099d612e0f6c71bdd967a4957ba8fa60c24` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_pmc2663974/` | 2 | 193.1 KB | 2026-11-09 | `5880e12bf15e4cd5c482cea1941e5fcc14e255e67df25bce7919e5f91a8776fd` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_rec/` | 2 | 717.2 KB | 2026-11-09 | `4915b82fd205f73859f7476d8a3d4e0bd8f76124f9656fa7c707fb2f9de35124` |
| Biomarker evidence and biological age (October) | `scratchpad/dl_ech/` | 2 | 1.3 MB | 2026-11-09 | `723283973ce9b19438956da9eed80eb0807a2c52ce39d0ec11d1e6c3704a7876` |
| Biomarker evidence and biological age (October) | `scratchpad/abstracts2/` | 6 | 15.6 KB | 2026-11-09 | `5b7c06e364ad7f870e09e22496fcc989574ed5f6baf95b60bb899dee78055984` |
| Central reviews and approvals | `scratchpad/review2/` | 25 | 3.7 MB | 2026-10-29 | `17309bf722bbad91af52ddd17337be0e7ff14c4bd799f3e4d798981008b745e6` |
| Central reviews and approvals | `scratchpad/review3/` | 3269 | 59.9 MB | 2026-10-30 | `755ce96409661527efb1f29bcf72f5db4e790346eb226d35d258c20cd70fd553` |
| Central reviews and approvals | `scratchpad/review4b/` | 17 | 579.5 KB | 2026-10-30 | `d8be1091285adeff8cfe371825a3629ec3f868f3de024446b03347b379a05e4e` |
| Central reviews and approvals | `scratchpad/review4/` | 11 | 40.2 KB | 2026-10-30 | `fe01316700188e86664409beac5323b44bcf884e94e2601b062111abedc28019` |
| Central reviews and approvals | `scratchpad/ (files at the top)` | 10 | 812.7 KB | 2026-10-30 to 2026-11-10 | `b37de31751d05252855e82d3755d5648fb0e6f2fbadbd05f1048229afeddfff0` |
| Central reviews and approvals | `scratchpad/review6/` | 2 | 1.7 KB | 2026-10-30 | `96e02df2ffd46434525f695058c07bc2e0c071e2c401f06a222b3873a352a106` |
| Central reviews and approvals | `scratchpad/review8/` | 961 | 16.9 MB | 2026-10-30 to 2026-10-31 | `d184695b0437aa59fbe45e8dc2cb4bfffb5d686cbc5e18283fffbf6cedae011a` |
| Central reviews and approvals | `scratchpad/review7/` | 10 | 260.7 KB | 2026-10-31 | `f2085d1dc1498af666f6f765174b7899f411b748709528b2ff987f4652690217` |
| Central reviews and approvals | `scratchpad/review9/` | 16 | 2.0 MB | 2026-10-31 | `74e3a5badf6b2706d1422231a026618ae1b0c2facec86e841c53cef1e263e154` |
| Central reviews and approvals | `scratchpad/review10/` | 5305 | 54.2 MB | 2026-10-31 | `a6553a8bf109dcc905d948f14fc8db412c5b3d14e41fc04a810a1c8c087b11c3` |
| Central reviews and approvals | `scratchpad/review11/` | 19 | 1.1 MB | 2026-10-31 | `6306982770206afeaf65dc720652ccfbcd63a6d1a6c729bf4e80f19fadfe5946` |
| Central reviews and approvals | `scratchpad/fable-review/` | 384 | 23.7 MB | 2026-11-06 to 2026-11-10 | `12678a77f61152ec4cf8d15d413c9553561d2044adf2b74fce72eb5368de0b0d` |
| Central reviews and approvals | `scratchpad/fable-rereview-2-stored/` | 2 | 40.4 KB | 2026-11-10 | `49fe1f4d5dec9bdcc64125bc41d755b4ca6164ccb156489a8c1eaa1e1549eedd` |
| Other scratch work | `scratchpad/ml-recent-scripts/` | 4 | 8.6 KB | 2026-10-28 | `00dc465e22e955786a8c2bc371b5fb10154421d52df4ebfe9c127f47d996be3e` |
| Other scratch work | `scratchpad/scripts/` | 81 | 575.3 KB | 2026-10-28 to 2026-11-10 | `bbeaf2adc081a44cfa69f382162f5ba87649fc38c7c8b1c74a0effa5267b1b55` |
| Other scratch work | `scratchpad/respected-scripts/` | 6 | 6.1 KB | 2026-10-28 | `294ef736a16f8c115b41d59356f132d33e7405242e4267b6888cbe557a96207f` |
| Other scratch work | `scratchpad/merge-work/` | 9 | 1.3 MB | 2026-10-28 | `5fcd77dae23a0bf05d87d922e302166e52cc2722ebdb73afb35afc5b02094334` |
| Other scratch work | `scratchpad/merge-scripts/` | 10 | 103.4 KB | 2026-10-28 | `aa6419b14dbfed6731696a99bddab7dd85b1edda49617cae221f0908668df1b9` |
| Other scratch work | `scratchpad/evav3-scripts/` | 10 | 484.6 KB | 2026-10-28 | `c8964f10bc1b17ec023231014eb96db2636fd7b6b2aeb9ec161f9916bfee47a4` |
| Other scratch work | `scratchpad/pai-verifier-scripts/` | 14 | 730.5 KB | 2026-10-28 | `3a9833bce344d53ea014480fb9d8661bfd28224573a4d5376add8b5ae6a9103a` |
| Other scratch work | `scratchpad/enabl-verify-scripts/` | 2 | 1.4 KB | 2026-10-28 | `5ef6c91b2a6ef3d835d3ecc1f4274a38803fb26092257327673ed41bb3b66b98` |
| Other scratch work | `scratchpad/ (files at the top)` | 331 | 13.2 MB | 2026-10-28 to 2026-11-10 | `bb8a8f138ac2be3bc7d35851a907917bfe3f17e2a48ec774e4d50f44f62447cf` |
| Other scratch work | `scratchpad/markage-scripts/` | 3 | 4.3 KB | 2026-10-28 | `5203d3f6b5c85b17dfe8d932bb72544537824f9e416efc5f4da36b3249ce3aea` |
| Other scratch work | `scratchpad/uc3m-arist-scripts/` | 1 | 863 B | 2026-10-28 | `2ccb81f0f821537a581f30ee258b586638a0653fbe5acf4e1867508a130aadca` |
| Other scratch work | `scratchpad/upo-verify-scripts/` | 2 | 1.9 KB | 2026-10-28 | `073169346f0bc8d15c75d24edeeeb6593dd9331bdea4a3b21ab5afd721c446e6` |
| Other scratch work | `scratchpad/lifelength-verify-scripts/` | 2 | 1.7 KB | 2026-10-28 | `0cdf6e58a6551535cee009af303e6230d3cf8f865b859ef49083c1f5aa8e4e43` |
| Other scratch work | `scratchpad/quironsalud-verify-scripts/` | 2 | 965 B | 2026-10-28 | `3f48b0dd47cfc1f91e7e299182aaaf84fd9086a9820b8a10c6c7f8e751d09bf9` |
| Other scratch work | `scratchpad/spc-verify-scripts/` | 2 | 1.4 KB | 2026-10-28 | `30ab293d5e7584046f64be39e9db98075ea7300d138deaa09bd3be58e122d1eb` |
| Other scratch work | `scratchpad/exernet-refute-scripts/` | 5 | 5.6 KB | 2026-10-28 | `44c1d63e39ff310438cff44ac607c1296730de10dcdce7e3e9d3bece322a95ef` |
| Other scratch work | `scratchpad/uc3m-refute-scripts/` | 2 | 1.4 KB | 2026-10-28 | `672dcecac024e18bf4187d8c810bf7e78276b2b09f045c85d13c8988f78eed7e` |
| Other scratch work | `scratchpad/scripts-refute-cic/` | 13 | 443.1 KB | 2026-10-28 | `bbff9e0a49cc535c66bfdff25f56706ffae765e04ece16b943fea5ccbec72e0b` |
| Other scratch work | `scratchpad/predimed-refute-scripts/` | 2 | 3.4 KB | 2026-10-28 | `bb27e051099f8c19993640ce2caa5b9a018935641e7cd226b41b5fdc9d576565` |
| Other scratch work | `scratchpad/gamc-refute-scripts/` | 24 | 820.6 KB | 2026-10-28 | `9286331f2a566656cd1819eb28d83bf9ba63e547f35029b067571cacec0a4b61` |
| Other scratch work | `scratchpad/gap-scripts/` | 5 | 9.4 KB | 2026-10-28 | `f85d00019ba910a8fa8e5893801c4358e82bb073758f517c09907f0f0300fec4` |
| Other scratch work | `scratchpad/g3-scripts/` | 13 | 309.9 KB | 2026-10-28 to 2026-10-29 | `429a51f5950eba97fbb1944fd952ab0c75457d367c7097a0934c06f570ed1eb4` |
| Other scratch work | `scratchpad/molisani-adv-scripts/` | 3 | 1.8 KB | 2026-10-29 | `7c382c0a344c2b4e8eb77983477235252be22b533b3149da32e2174463f65117` |
| Other scratch work | `scratchpad/final-synth-scripts/` | 2 | 2.0 KB | 2026-10-29 | `be448cad18cfe13bdfd8c26a0e45761ffa9145d75916ba663515c50c80073c1a` |
| Other scratch work | `scratchpad/spotcheck/` | 5 | 233.9 KB | 2026-10-29 | `c858b331d0defbe6080fa2a2681eace6ebdc26b9770d7c81b98e53bce8d6b69b` |
| Other scratch work | `scratchpad/methfix/` | 16 | 211.6 KB | 2026-10-29 | `8c33780e045ab6a20b20f24def937485dfddef9e51d08209352bc3da86846c6a` |
| Other scratch work | `scratchpad/methfix2/` | 34 | 894.2 KB | 2026-10-29 | `f40fb40ba1043bd25e3849c1aac70f74131f33b6e5e17bab978b46f6a8e5bc63` |
| Other scratch work | `scratchpad/onepager/` | 4 | 274.4 KB | 2026-10-29 | `54bca36253b846cdd6b3d1d29aed453c8f5f18d836a6304952a832409d01627b` |
| Other scratch work | `scratchpad/r2net/` | 6 | 1.1 MB | 2026-10-29 | `b5bda70be0fb67ef24ebf4afeaa7e3b0162d3f2c31806f373a92fb755e2302d9` |
| Other scratch work | `scratchpad/r2ts/` | 2 | 3.2 KB | 2026-10-29 | `673d18f4545f1c9eb832bda2c312180ccf2c94eb6a79bbdf5d0ab4a15e182bc2` |
| Other scratch work | `scratchpad/livecheck/` | 2 | 19.3 KB | 2026-11-03 | `10407cf0ca6a5d5aa7430044a6a8699f9be19c6c413addf1798148f24edec946` |
| Other scratch work | `scratchpad/t10/` | 2 | 59.2 KB | 2026-11-05 | `b0b96fa7f84b7061fadfefd33b8aed4173ce4df7a94692a4ac0184f7cd967ef6` |
| Other scratch work | `scratchpad/cache/` | 868 | 5.5 MB | 2026-11-06 to 2026-11-10 | `c862645d9d28a12aafd8a084ac8e7635d3198ab2e3304c9899642dd465a8b3e6` |
| Other scratch work | `scratchpad/work/` | 22 | 689.5 KB | 2026-11-06 to 2026-11-08 | `28852e05e03fc042233ee6368f85769fb7bafab73fe2d4fc0dbc57fb23ed6785` |
| Other scratch work | `scratchpad/w/` | 3 | 193.2 KB | 2026-11-06 | `53cc94246eb35ba11997807433c6dcd716c55cb47ca9108982575e87ff0e4137` |
| Other scratch work | `scratchpad/rx/` | 3 | 13.8 KB | 2026-11-06 | `9fa38bcbf00556aa3b486dcb093195d4663620fc80ec7d1fed65fb8f516eda12` |
| Other scratch work | `scratchpad/fam/` | 8 | 2.4 MB | 2026-11-06 | `397bf2bdecc584fb4ded58c984106ed36274e660eb0e3f17b978b72732f2cb8a` |
| Other scratch work | `scratchpad/wk/` | 2 | 79.4 KB | 2026-11-06 | `d8a4cc93e5fafc6f6606ecc44b09e22dca96b30ad28c15b95b070b83b29fb41b` |
| Other scratch work | `scratchpad/ws1opt/` | 42 | 355.5 KB | 2026-11-06 to 2026-11-07 | `847d88e68d0f7964dea71eb7f7091d8c8179ff0d0f999f386d8b89170de92291` |
| Other scratch work | `scratchpad/dump/` | 27 | 581.3 KB | 2026-11-06 | `fe0cc81cc1e3423f63fc1c57ac876c078a9b6199fa5d5168eded70b84d91c3de` |
| Other scratch work | `scratchpad/in/` | 15 | 774.4 KB | 2026-11-06 | `747cc5d154046203f06e400ce24d8cf3d925c2188d79475701a75ddc95ce2680` |
| Other scratch work | `scratchpad/lit/` | 196 | 2.8 MB | 2026-11-06 to 2026-11-08 | `a8ec96d209f9c4690b4ab7166e78cdf551430893e914572e05022e274a89dcfa` |
| Other scratch work | `scratchpad/tools/` | 25 | 251.3 KB | 2026-11-06 to 2026-11-10 | `fcae41419845198ca86d7ca7d060c60af33b66c3b09246975b14d3c27cf330a8` |
| Other scratch work | `scratchpad/qcache/` | 272 | 1.7 MB | 2026-11-06 to 2026-11-09 | `c86af619a92109ee3710166e406069f7c256680b4100084bcd97bdb347dfab51` |
| Other scratch work | `scratchpad/dl1/` | 30 | 1.5 MB | 2026-11-07 to 2026-11-10 | `b240d2d30ef1145ca785181b1a3dc5829a011b416d8f6c11517c255fcf93ad3f` |
| Other scratch work | `scratchpad/dl2/` | 4 | 356.6 KB | 2026-11-07 to 2026-11-10 | `7fdbae077bd4bf915f413bfafdd566874eb41a7895c3b89af2764b45207067f2` |
| Other scratch work | `scratchpad/extra/` | 6 | 262.2 KB | 2026-11-07 | `858c8f450446895181972bf8f29992c99e04eba1510d5a83ba72d88bcbbf0074` |
| Other scratch work | `scratchpad/qc-cache/` | 416 | 2.7 MB | 2026-11-07 to 2026-11-10 | `20fb008b181052527c5e27190040596cfba233ba55807b13dbcc5e97b159c6db` |
| Other scratch work | `scratchpad/cache2/` | 2 | 2.0 KB | 2026-11-07 | `30e00afe861b32f487e3403695bd8a9afb98b6809e20fd6242d15fb77dcf016a` |
| Other scratch work | `scratchpad/cache3/` | 2 | 56.2 KB | 2026-11-07 | `0d869bdf5cc8caaa49a43a181757caac427c25f1eb727ded44918f68ec6dc4d0` |
| Other scratch work | `scratchpad/j2src/` | 17 | 1.0 MB | 2026-11-07 | `d002561cb447b6b2cb8e9610b2664cd93ef65b338a3730c799f211ee57e93af0` |
| Other scratch work | `scratchpad/fetch/` | 44 | 1.0 MB | 2026-11-07 to 2026-11-10 | `30a2af5c9452e0f2aa7459460708b69610aad3b11f3e4a59ed641a6c8bfa07fa` |
| Other scratch work | `scratchpad/j5/` | 29 | 145.1 KB | 2026-11-07 | `7ce79267f6e8124681fa23bdee695dac1c85b7ebda3fe7b96096d98b488d5372` |
| Other scratch work | `scratchpad/fetched/` | 108 | 2.5 MB | 2026-11-07 to 2026-11-10 | `9a504bc6fce0d16cb4816414ce1cb8d4c2ed3905a5e937499cb5d753f19f7a55` |
| Other scratch work | `scratchpad/gen/` | 12 | 217.9 KB | 2026-11-07 to 2026-11-10 | `0a638b6072a8c1db0e7eaaa06c66bf3d0cde86effd871bbe3c5ccf4712601d43` |
| Other scratch work | `scratchpad/j1fetch-r2/` | 39 | 2.0 MB | 2026-11-07 | `b2e89538945a81a884162e4f1eabcc696df7b52062658e839e4464725bdfcd9a` |
| Other scratch work | `scratchpad/j1build/` | 2 | 66.4 KB | 2026-11-07 | `9774a9ab3e807d7dd7b8c8820ffb17f8bfcc57a0f0924e1157dca636c99ed838` |
| Other scratch work | `scratchpad/hong2023/` | 2 | 163.4 KB | 2026-11-07 | `68efa9398ccd7219a782b96da6ea31b0b0fb3d61c7e33d4a701deebd8bc46d31` |
| Other scratch work | `scratchpad/hong/` | 2 | 163.4 KB | 2026-11-07 | `51865a7875342cede5daec1bd97a434e788419ea9a2e1d0e5a944ccf2e134e1b` |
| Other scratch work | `scratchpad/shen/` | 2 | 153.8 KB | 2026-11-07 | `8d7524a5abaf7e36dc25945fe14f040acbee45edd5e6f82f9ecefa29322fc3f6` |
| Other scratch work | `scratchpad/epmc/` | 15 | 661.4 KB | 2026-11-07 to 2026-11-08 | `f31f68da630a51088184a4580f0a7b971485fff374c5de43d1a0c210b6cfc609` |
| Other scratch work | `scratchpad/j1r3b01/` | 57 | 1.9 MB | 2026-11-07 | `ce54abe2353db65aeb7953d74b2df45d25e1cbeea9c2df7b750d55762d9b6110` |
| Other scratch work | `scratchpad/pdf/` | 4 | 432.3 KB | 2026-11-08 | `c278f38fbcc9b33dfeee4d789aa03b6b1972f32678c0470985451cd196a9ab3f` |
| Other scratch work | `scratchpad/j3pdf/` | 3 | 305.1 KB | 2026-11-08 | `4a158cf0da1700402f1501ae912206ccf399c036357da77f5f45dc5c2e8e0604` |
| Other scratch work | `scratchpad/j3src/` | 1 | 119.2 KB | 2026-11-08 | `3c71ceb9a6885464c5e9ff08a69518fbdd6a4b6d5d272529b5a48c3d9897a57b` |
| Other scratch work | `scratchpad/j3build/` | 2 | 43.9 KB | 2026-11-08 | `8a0ea881e5676841ef08c21addddc253ce91d7e5ecf733e46454c7c37150f482` |
| Other scratch work | `scratchpad/k1/` | 3 | 4.4 KB | 2026-11-08 to 2026-11-10 | `c6b6919ace2ae92ce34c30c2a681192482d0cbeeabdc19ad2b3a91369cdc3340` |
| Other scratch work | `scratchpad/bin/` | 13 | 359.6 KB | 2026-11-08 to 2026-11-09 | `bdaa4acc8475c9c0a07e7ffcccec5b23a7d78156ad303d800a201f76d11b9428` |
| Other scratch work | `scratchpad/dl-pmc-crit/` | 2 | 279.5 KB | 2026-11-08 | `e3ce09f8824ea57c307829cad20f75784792cba30d2ea3169ea23581c79d1024` |
| Other scratch work | `scratchpad/dl-abs/` | 4 | 17.1 KB | 2026-11-08 | `75b83482bcc7991f54f2e836fa7ce093f1a22fd9d69e6146e8c6cb3b950853ae` |
| Other scratch work | `scratchpad/dl-epmc/` | 2 | 72.4 KB | 2026-11-08 | `a8c32ac8999b759f00d0e875b39982750fcef636ad5ac510b528584d59454993` |
| Other scratch work | `scratchpad/dl-pubmed/` | 6 | 14.2 KB | 2026-11-08 to 2026-11-09 | `f252ee059a55e78804743095ac0094328bc0fc2d8ee176f61e4c7edf38efbd97` |
| Other scratch work | `scratchpad/dl-pmc/` | 2 | 184.4 KB | 2026-11-08 | `ebeb4a6a19b8406aeff21aca89db9950c6b3d1d3a6acb35d8f83ea24933ca79f` |
| Other scratch work | `scratchpad/orig/` | 4 | 963.5 KB | 2026-11-08 to 2026-11-10 | `6893add052f592bfd7bc4e4be60a6b70bc0dbb78d068731b1f1c83698b2f0ee6` |
| Other scratch work | `scratchpad/live/` | 8 | 290.9 KB | 2026-11-08 to 2026-11-09 | `374bdcf7f87277d19db96ba023c00bb8aaefdf1ef726ef9686eddc40a84b2e1a` |
| Other scratch work | `scratchpad/recon/` | 3 | 251.2 KB | 2026-11-08 | `b2ee32a458ed1f0066fb0db7fc990efa453e64fa714c8c8417b1daa68ab6b7c2` |
| Other scratch work | `scratchpad/judge/` | 3 | 31.0 KB | 2026-11-08 | `0a9df540dbff28f4f6c978d452112d09f1d21cd5ec637a0371bd6c0a1eb563c5` |
| Other scratch work | `scratchpad/src-aspree/` | 1 | 3.2 KB | 2026-11-08 | `3f52f6db31294c568c4a6e78c9e4970dad4f5eebecff3c5757b76e46efe1ef80` |
| Other scratch work | `scratchpad/src-ling/` | 1 | 125.7 KB | 2026-11-08 | `123ef20fbb81172fc64c27be83fe087bb519da4445683b120ff0299af9ff5caa` |
| Other scratch work | `scratchpad/src1/` | 16 | 432.2 KB | 2026-11-08 | `2784a3f0ea6b2314f9c8fd90f9e8c082f351f27c5f381c8bd78809184b3b7e9b` |
| Other scratch work | `scratchpad/pages/` | 2 | 363.1 KB | 2026-11-08 | `94f610e798466af25013dc7f2a50ed1032871505bedfd1b1353f643aafab280b` |
| Other scratch work | `scratchpad/efetch/` | 5 | 10.6 KB | 2026-11-08 | `16734813efc3f18cfd8c8335cfa7222d57b7d654ad06d7d1558171b647c6e338` |
| Other scratch work | `scratchpad/pmc/` | 2 | 1.0 MB | 2026-11-08 | `1a16bc4d03fe0c05ffe522261035a51ff1d4f253d25705241aca7e8174254331` |
| Other scratch work | `scratchpad/src2/` | 2 | 132.9 KB | 2026-11-08 | `aea75e7e8f8111b2be5ace8b8f318118308ff8b5e1eed1f8f95ea0f58af67c28` |
| Other scratch work | `scratchpad/dl-pmc11734832/` | 1 | 175.5 KB | 2026-11-09 | `08f3b13a6b8e8daa4af1f2413d4ac14c138400e7ad19e39dcdb425cd54a03ce3` |
| Other scratch work | `scratchpad/refB_nla_giv7/` | 1 | 175.5 KB | 2026-11-09 | `698791563c24489c86ceccc0a0f6d2dd7684830c58736f0fe601a023ddb4f5f7` |
| Other scratch work | `scratchpad/nhanes/` | 2 | 856.0 KB | 2026-11-09 | `6059384547a2aeed27800d4ce900ff170cb29912e7bb9688daa94a6e95560197` |
| Other scratch work | `scratchpad/refb-f27-r1/` | 16 | 1.4 MB | 2026-11-09 | `3cdb0758d051a717285f3adf8f00e47b746a9f5055c7efcdbd8355c1b1fd01ba` |
| Other scratch work | `scratchpad/qc/` | 37 | 486.6 KB | 2026-11-09 to 2026-11-10 | `4292151e99a77d5f9b47e20bc63b97a310a9f3e35ef11637b403b4c66e6dddb0` |
| Other scratch work | `scratchpad/src-nla/` | 5 | 402.7 KB | 2026-11-09 | `c30630274df24a9810e591fdd6c933edf5792339cf08d8969c9217af07858d2f` |
| Other scratch work | `scratchpad/j1f27r2/` | 28 | 2.6 MB | 2026-11-09 | `3c6e62cd0bdc703c8ecb2fb438abe73cf320462c3bc50760aff6bf7ac09607bc` |
| Other scratch work | `scratchpad/src-fetch/` | 6 | 34.4 KB | 2026-11-09 | `4c70cb800c5654c4e6af60803bceb5ea6f28cb39e9f692930fe852af03321a71` |
| Other scratch work | `scratchpad/src-b03-hdl/` | 2 | 6.1 KB | 2026-11-09 | `43af55ed0d91d04dc2b4a02b233e12034b4e086a39d48a5d6ea440f93d85a546` |
| Other scratch work | `scratchpad/refa/` | 1 | 1.9 KB | 2026-11-09 | `a399d564abef9814710358e99203f22445eebed73a8b463d5c1ef807d5d16cc6` |
| Other scratch work | `scratchpad/refb/` | 3 | 2.1 KB | 2026-11-09 | `227ad4cd0b678ec713f49876f7bc6ad28498820d4cb6f74b85e9d885197398a1` |
| Other scratch work | `scratchpad/out/` | 6 | 393.6 KB | 2026-11-09 to 2026-11-10 | `77791407d605a0edaa8c8c9af95de41932477de9a39a181d3af1913acd078f00` |
| Other scratch work | `scratchpad/src_abs/` | 24 | 59.6 KB | 2026-11-09 | `c2149246b126bce7b88679a61b6b15fd24e18779c28cd5f81de8762569344b21` |
| Other scratch work | `scratchpad/src_full/` | 13 | 734.7 KB | 2026-11-09 | `c157e5cba95d990247c27a09394893464fb53a2686803d00efcd903973e79fcc` |
| Other scratch work | `scratchpad/tmp/` | 3 | 27.5 KB | 2026-11-09 | `a5699913c5316a23ed1bf713b936838eabb9fccd86ca38861230e42b56f9c7a9` |
| Other scratch work | `scratchpad/sources/` | 4 | 54.2 KB | 2026-11-09 | `0abd016a97713a463a492520254c7e6e6179332e396ca6d9845dea60e2db3d35` |
| Other scratch work | `scratchpad/test/` | 1 | 295 B | 2026-11-09 | `03b0a387a75f30b10ec7056c8682876c8d9ce51339d487678dc7a6d0f89333a1` |
| Other scratch work | `scratchpad/dl-f09-refa/` | 9 | 26.5 KB | 2026-11-09 | `584108cd43c28bf696770d021d0b6f9eb9deae5685c3f7799131e700371593ea` |
| Other scratch work | `scratchpad/refb-b04-f09/` | 31 | 519.1 KB | 2026-11-09 | `c6231ca994f8475a5bc6b5bb1036a0fa21de37cf6f703f8940ecdcaf06e106a7` |
| Other scratch work | `scratchpad/dl-epmc-fulltext/` | 1 | 70.7 KB | 2026-11-09 | `4997dae87cb45202c33b0b8a53c4d674c7f658f4de20473cdd2b80eb0149277f` |
| Other scratch work | `scratchpad/rehearsal/` | 2 | 326.4 KB | 2026-11-09 | `002a48952efe4385f8425238fdb845d8f94b4deb55c72cad2693a0b057f5f579` |
| Other scratch work | `scratchpad/rehearsal-cache/` | 2 | 65.8 KB | 2026-11-09 | `ed983b5093ac25f222e949f1ad8af9da430841677300f7d7e5f528a8157d5bb5` |
| Other scratch work | `scratchpad/dl-who-pdf/` | 1 | 859.5 KB | 2026-11-10 | `db230cc325cb14be9ecb09de89a9004a9dbeda5fd65d74787c07511f98103884` |
| Other scratch work | `scratchpad/repro/` | 3 | 28.9 KB | 2026-11-10 | `5397d79256166a3e7a9d284d79bfdda0ede5c4a7a8d94fd092a0ae6c98247d9e` |
| Other scratch work | `scratchpad/run/` | 2 | 34.6 KB | 2026-11-10 | `632f1f66c81ea3ae57b3bc8649599d155fe5af0aa9dc1911ceb0a30c8614889b` |
| Other scratch work | `scratchpad/verify_f12_scripts/` | 11 | 84.7 KB | 2026-11-10 | `10cb9b75575e7b94ff8e0049d839d15470394da8c119fe6831d2b4da9fabaa89` |
| Other scratch work | `scratchpad/verify_f12_src.sXru/` | 74 | 2.2 MB | 2026-11-10 | `9ecdc78d9f871d2199cdb0a88dfd9ac0837b0eadb4059917298a3297da29093f` |
| Other scratch work | `scratchpad/j3b05/` | 24 | 1.2 MB | 2026-11-10 | `112e40409b981a053ba8ce70f44d2a062fc6441477558cf834f5be2c6c08f2ad` |
| Other scratch work | `scratchpad/src-refb/` | 3 | 96.3 KB | 2026-11-10 | `6cffde6437446a027aa2b0aca9cc24940ce6ce7a698b0d67337e09be70ba7f82` |
| Other scratch work | `scratchpad/pubmed-dl/` | 1 | 16.4 KB | 2026-11-10 | `d8c4f086749a462ae99eaa83cb31a3afab982f7c6a474ab2305361ab1ca7880f` |
| Other scratch work | `scratchpad/k1check/` | 1 | 1.9 KB | 2026-11-10 | `95361a2c833f734d963ef140ea74286661f4515bea46123d81a64cef62410d4e` |
| Other scratch work | `scratchpad/dl-ash/` | 4 | 661.5 KB | 2026-11-10 | `7c47f0942ddead36b447ea18654d3dbc22a80fd76f1dce2993a788f1182bf0aa` |
| Other scratch work | `scratchpad/dl-pubmed1/` | 1 | 60.3 KB | 2026-11-10 | `755569440418a82bd15e36ec910936acd5a6df590055de781e86531a74276565` |
| Other scratch work | `scratchpad/dl-pmc1/` | 13 | 937.9 KB | 2026-11-10 | `1d6c36f0bd84b60edbbe20198c40a1a0ce981e922e7364c00505bf0909945424` |
| Other scratch work | `scratchpad/dl-epmc1/` | 1 | 210.8 KB | 2026-11-10 | `d58907552f30ebb12270dce3ed79bea87652bd6af424bef27fccb4531b9e63e7` |
| Other scratch work | `scratchpad/dsrt/` | 3 | 76.1 KB | 2026-11-10 | `2c2d3c331ec39a7cf6fc43b90ffec5780a79deb74d7b7109fd8bccb39796dbfa` |
| Other scratch work | `scratchpad/lex/` | 1 | 1.1 KB | 2026-11-10 | `84500df1abb00c97c6778335b9d58ae7388afd427a2c67261f3a017eccc7f5eb` |
| Other scratch work | `scratchpad/dl3/` | 9 | 758.3 KB | 2026-11-10 | `00423e127907978f17f09f7208aed358d77c2793dce90c4f6f51922b34479c14` |
| Other scratch work | `scratchpad/dl4/` | 4 | 154.8 KB | 2026-11-10 | `40e031165ec87cb688948957c637c9e0e9bf8e112fd96e3dc0f50636196f8bd2` |
| Other scratch work | `scratchpad/gov-edits/` | 31 | 566.1 KB | 2026-11-11 | `419fb253e231e6d7658d8e0f5c523c85069c325bd5edf9fb8559d598ce2a6025` |
| WS1 mop-up round | `scratchpad/ws1-mopup/` | 22 | 24.1 MB | 2026-11-10 to 2026-11-11 | `b22d648ee3326961ce38d779212f6492b9cbd724dec16b564d2942184d315361` |
| WS1 mop-up round | `scratchpad/mopup-decisions/` | 10 | 308.6 KB | 2026-11-11 | `f9cce099e90e46cb84286cef49a323fa487fa360ce2ac6098330c91fdc84c4ab` |
| WS1 mop-up round | `scratchpad/mopup-execution/` | 1 | 3.6 KB | 2026-11-11 | `98442153d7ec8c58f7e19054b7846550441ab9193a7c559124642f0881c8a41e` |
| WS1 mop-up round | `scratchpad/mopup-triage/` | 78 | 4.0 MB | 2026-11-11 | `7924b4e8ff797c4c06da1b2560822b6f4b669c883b9d0b352b0a8744a09854ec` |
| WS1 ranges by family | `scratchpad/mycheck/` | 322 | 3.8 MB | 2026-09-22 to 2026-11-03 | `925b200af378019038f5ba5a09489a1614899809808c0f33ea4377bc1c51e889` |
| WS1 ranges by family | `scratchpad/ (files at the top)` | 101 | 5.6 MB | 2026-10-29 to 2026-11-10 | `e0ab595d31b1d6af8b4bc4c40923ef769ca9584a137ca30d70b05a21cd802bef` |
| WS1 ranges by family | `scratchpad/f02-evrepair-r2/` | 488 | 4.1 MB | 2026-11-06 to 2026-11-08 | `f590d2beb97879a7ebe3e48a277fe0a3a52f29744843523a1de7571a2cbb424c` |
| WS1 ranges by family | `scratchpad/c1/` | 8 | 2.4 MB | 2026-11-06 | `681d2208839b073e2e322f4e2e2edb4b5d928496d0857f19d71149c84bdd2336` |
| WS1 ranges by family | `scratchpad/c2/` | 8 | 2.4 MB | 2026-11-06 | `9ae99aa375447765a85c01b6fa6d3065cea2ef60a574531ad59840bcc6430c31` |
| WS1 ranges by family | `scratchpad/c3/` | 8 | 2.4 MB | 2026-11-06 | `82a4dada3daaa8285d1169a68f08a735d14c58a816167d8ee1b95cdd1f02a5b2` |
| WS1 ranges by family | `scratchpad/cx/` | 8 | 2.4 MB | 2026-11-06 | `951b14e15174713fd3adb64f3bb3994839535d4ea2fc3320708b728a18fa72db` |
| WS1 ranges by family | `scratchpad/c0a/` | 8 | 2.4 MB | 2026-11-06 | `62eeaf9503b2ea5fcab63a8742a05d9e198e7047245022c921487b41ca1464ae` |
| WS1 ranges by family | `scratchpad/briefs/` | 30 | 1.3 MB | 2026-11-07 | `4ad65afffd894d7c69aae521971db84d3e07da827c8c52bbd64f2cc7296dbf77` |
| WS1 ranges by family | `scratchpad/f07/` | 226 | 6.1 MB | 2026-11-07 to 2026-11-08 | `a8c2d4f9087f5d7c484a1a5ad5db0c80072dc59d53c32f50f463d46e3a13d104` |
| WS1 ranges by family | `scratchpad/build/` | 12 | 260.9 KB | 2026-11-07 to 2026-11-10 | `30c21ebc441b953c33eb5ee2634b750bf2149f3c4df75f02d441997729e86735` |
| WS1 ranges by family | `scratchpad/f05-repair-r2/` | 34 | 1.6 MB | 2026-11-08 | `87f8443d9fbaae26fc98e485a4a0a61ca99a98203a514a6cc44f32e7c4678529` |
| WS1 ranges by family | `scratchpad/f05/` | 89 | 1.6 MB | 2026-11-08 | `92aa0d8a097925f202de55a4fc533d77d4ab5e56ed84f29e23df62f29439b360` |
| WS1 ranges by family | `scratchpad/f08/` | 126 | 1.5 MB | 2026-11-08 | `b2091454077d8e62a0f47269f8c1db1cec4edd59df416e0751e4658f774f299c` |
| WS1 ranges by family | `scratchpad/f02verify_src_bSWzWt/` | 64 | 1.4 MB | 2026-11-08 | `0ec03449c5d230acea83b0c05f4e1821cdad183793767430d16af87bc309b70f` |
| WS1 ranges by family | `scratchpad/f05verify/` | 121 | 1.4 MB | 2026-11-08 | `bc6352d7eb8d828467b63345bf34fd6875ca155062ab2a2d0d657213e6a15be0` |
| WS1 ranges by family | `scratchpad/b02r1/` | 2 | 2.5 KB | 2026-11-08 | `45985ce386b91676b5f8eb41c55560bab03aa00abe91f43a5ca206b8efad5d28` |
| WS1 ranges by family | `scratchpad/f08a/` | 7 | 42.4 KB | 2026-11-08 | `d97ca3d4c5f2178b367bea86564ba93a53832b18a1a71b3f01418023cb24ab56` |
| WS1 ranges by family | `scratchpad/f06/` | 57 | 1003.4 KB | 2026-11-08 | `21af8485cef86428446d05a348d3df5210dbe14d2555c30ecf640419fe8fc1d7` |
| WS1 ranges by family | `scratchpad/f06-verifier-B03/` | 43 | 1.4 MB | 2026-11-08 | `2fe0683c9c1ff6a8172ebe61037ac4054e7c2352aa70a2d6c55e9dd120bdf16f` |
| WS1 ranges by family | `scratchpad/f07v/` | 98 | 1.3 MB | 2026-11-08 | `df9c46ca6c94a1ffb07cfdd65f5890d5c1a5709dfe33fc3532a9bcbb20327217` |
| WS1 ranges by family | `scratchpad/f27-verify/` | 36 | 757.2 KB | 2026-11-08 | `3a254b03bf9f27e7e16d50946961675c21e13e714ad1f785a7c34f1362d175d3` |
| WS1 ranges by family | `scratchpad/compile-out/` | 8 | 2.7 MB | 2026-11-09 | `d936830b6b033ba0211cae93dda2814e018c295a110d9ea2fbdff5de85b7e6d9` |
| WS1 ranges by family | `scratchpad/f07-fixer-r2/` | 1242 | 46.7 MB | 2026-11-09 | `fb2ff61eb14f113b7a1fbe487381f94de4d626657de62545168b60eea956b71f` |
| WS1 ranges by family | `scratchpad/f11src/` | 44 | 780.6 KB | 2026-11-09 | `49a53d3f4a0b7d13ea5902db9f06e60fa502c741c27674f41fb5fc0bff27fe1f` |
| WS1 ranges by family | `scratchpad/compile-f11/` | 8 | 2.5 MB | 2026-11-09 | `5a9e9ab83b9804422f8688c6545efaa642f72ce70507d7dbf7eafba6dcbb47c6` |
| WS1 ranges by family | `scratchpad/f11r2/` | 16 | 319.3 KB | 2026-11-09 | `6cdd14d0cab10df59f02929f02db9ee181babc6f489ad4488876d585ffe58e1e` |
| WS1 ranges by family | `scratchpad/f10fix/` | 77 | 5.7 MB | 2026-11-09 to 2026-11-10 | `1ae7bb806a2ee8ffcac466b4af66f2ce94472343f5dcaf94a7f2865104162c84` |
| WS1 ranges by family | `scratchpad/gate-live/` | 8 | 5.9 MB | 2026-11-09 | `7f4fa262a0aa57deb278d52e0af575f1d5d42c81154f4c5e8c6c42bc906634ec` |
| WS1 ranges by family | `scratchpad/w4/` | 32 | 8.4 MB | 2026-11-09 | `0f51abf8ccb153dcc7c56cc9172b7f8b97daef6b21303901b8a90d06134a26be` |
| WS1 ranges by family | `scratchpad/f11fix/` | 23 | 2.5 MB | 2026-11-10 | `f92e5ae59fd6d0b3ddd4066bfa1a872d4be996b24956188d0eeaff607702aa70` |
| WS1 ranges by family | `scratchpad/f11fixer-r2b/` | 174 | 5.6 MB | 2026-11-10 | `721bf2b64d3362841bd301ee69d53f0f3a9b68ee8d7a28783abc63f832922fef` |
| WS1 ranges by family | `scratchpad/f09/` | 94 | 4.5 MB | 2026-11-10 | `912c55aba848fac48d58af07b8dd8b743cce561e447927c9160f32d96a3852d9` |
| WS1 ranges by family | `scratchpad/compileB/` | 8 | 5.9 MB | 2026-11-10 | `da9f28bbdfdb140678974166724755060a9a4a05ccc40d4ff958b4cb6d5b970e` |
| WS1 ranges by family | `scratchpad/compile-all-1/` | 8 | 5.9 MB | 2026-11-10 | `9f03d83a2aeec2644a14f6441eeb58fba677e0a4400b8a9300026faf1f045e75` |
| WS1 ranges by family | `scratchpad/compile-all-2/` | 8 | 5.9 MB | 2026-11-10 | `a10cbfd66b64b0d58509ba18df0d9b3e5f79fb70246140d8decbcec93f2ea54d` |
| WS1 ranges by family | `scratchpad/compile-main/` | 8 | 6.0 MB | 2026-11-10 | `4b4e95a158e06a858740e1d5a1948d7f9495fcd0a448cfba6a63bc10a6babcf4` |
| WS1 ranges by family | `scratchpad/f12/` | 250 | 4.6 MB | 2026-11-10 | `6b2252ede9bede610cef14306d577a99da7ad61258de8042ea7f935db5356674` |
| WS1 ranges by family | `scratchpad/f13/` | 171 | 3.5 MB | 2026-11-10 | `37baef06697653cae4369afa4c46fb9853a124a0b52227efc7abd679ddd58de4` |
| WS1 ranges by family | `scratchpad/f13v/` | 101 | 527.4 KB | 2026-11-10 | `d1a3aaf0bff9904bb8578e48375c077345bec7c22200b93939808d19e875aff5` |
| WS1 ranges by family | `scratchpad/fp1/` | 8 | 6.5 MB | 2026-11-10 | `88a50934254e6ea553743c9ca3a2d7c5fd28b64912f6a5a1465030e5d7d0d274` |
| WS1 ranges by family | `scratchpad/fp2/` | 8 | 6.5 MB | 2026-11-10 | `9d1c7148cc2aff3e30a86b00d64ddfb74f99e559f60e8a8de848da17b55be1c3` |
| WS1 ranges by family | `scratchpad/f14/` | 102 | 1.9 MB | 2026-11-10 | `a6d4fca46442feaa80c79d4d2eed99c72ce8f278cba03f9429e140c445a9df8e` |
| WS1 ranges by family | `scratchpad/f13verifier-Hdwcuo/` | 106 | 757.5 KB | 2026-11-10 | `ab147cb4f9a682af46566bc39bc3b8ff434dd2a1e6e957d8a5f0d4bfffbdc97d` |
| WS1 ranges by family | `scratchpad/f14v-fNv1Sa/` | 74 | 3.1 MB | 2026-11-10 | `688cfc9f248e1a0c91efa2518378f60a0c82f1940e8de46d78d35d5565e18fb1` |
| WS1 ranges by family | `scratchpad/f12fix/` | 30 | 3.9 MB | 2026-11-10 | `32cd5c07f8191e7f0245b48b02606a35f546b8525f260527c5daa8e0d4fc5e30` |
| WS1 ranges by family | `scratchpad/compiled-f13/` | 8 | 2.8 MB | 2026-11-10 | `8a105fcf92010e0e9c0537e6441a4a0adbf6f5d38de93f66295a002093eb9cbf` |
| WS1 ranges by family | `scratchpad/compiled-f13b/` | 8 | 2.8 MB | 2026-11-10 | `a36ff6cd8504dc5085b83b7d305aa6f4e99df36e5d675a73cdd912fbd703371d` |
| WS1 ranges by family | `scratchpad/compile/` | 10 | 2.8 MB | 2026-11-10 | `25b1572606f41408a0d34473cfd317b7dcae78d5c2632567feb6655461094707` |
| WS1 ranges by family | `scratchpad/compile2/` | 10 | 2.8 MB | 2026-11-10 | `a4132d09fe6448a2853ac380cd4e07f43b86f9a49c2c8571cfa0216cbbaf26bb` |
| WS1 ranges by family | `scratchpad/c12/` | 5 | 42.3 KB | 2026-11-10 | `0f82b279454456dc5a9135764ff7fd50af50f0301bafe1992af894b15c8cc79e` |
| WS1 ranges by family | `scratchpad/batch-sessions/` | 6 | 17.7 KB | 2026-11-10 | `64b53b532febcb77f0dd76f74c89de98ed3d34b3e9209843b0d250fc9c76303b` |
| WS1 ranges by family | `scratchpad/c27/` | 10 | 447.9 KB | 2026-11-10 | `969e03a858f2916a48f0d6f83e2fcbeb2b45a244286e2a0006a373356b2c7909` |
| WS3 score | `scratchpad/ws3-map/` | 60 | 24.8 MB | 2026-11-10 | `d53d0f4d5635a09f70ab6c2adaebe5dc1f8c2851fadd0958091497b4a07fb5a7` |
| WS3 score | `scratchpad/ws3-impl/` | 173 | 33.8 MB | 2026-11-10 | `fd4c2bb53528537d6d8ac9a93d69bf04870916a4644bc93cddc1898a65f20776` |
| WS3 score | `scratchpad/ (files at the top)` | 3 | 257.5 KB | 2026-11-10 | `f1895eda245c65a077d9fc1a6655f68d551d70322e4c0793bac13c8ca4b16eaf` |
| WS3 score | `scratchpad/fable-ws3-decisions/` | 63 | 9.5 MB | 2026-11-10 | `f17f2f2013e15ac6959ddebc8e79a8478f3caa864cc0ee2260335de9b2129e97` |
| WS3 score | `scratchpad/ws3-wave2/` | 850 | 172.9 MB | 2026-11-10 to 2026-11-11 | `85b72d3a16e699d7a845b53faf1ab3b6dab2b6745b49799c061e6d89b086d413` |

699 symbolic links are stored as links (mostly `node_modules` links to the repository's packages, and the tasks folder's links to agent transcripts, which are in the transcript archive).

Copies of the repository in the scratch folder, stored as differences from their commit:

| Folder | Commit | Made (UTC) | Identical files, not stored | Changed files, stored | Added files, stored |
|---|---|---|---|---|---|
| `scratchpad/review4b/repo` | `54ead22be7ee` | 2026-10-30 17:05 | 1730 | 0 | 0 |
| `scratchpad/ws3-wave2/decide-WS3-09/snap` | `1e5bcd2ff3e4` | 2026-11-11 20:37 | 5776 | 0 | 0 |

Left out of the scratch archive:

- `scratchpad/dl`: tools or downloads, not proof
- `scratchpad/evidence`: the evidence folder itself
- `scratchpad/src`: tools or downloads, not proof
- `scratchpad/venv`: tools or downloads, not proof
- `scratchpad/brief-size/proto`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-base`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-m1`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-m2`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-proto`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-urea`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/round1`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/tmp`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/decision.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/dups.js`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/measure-base-vs-committed.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/measure.js`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mkroot-gov.sh`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mkroot.sh`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mutant-m1.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mutant-m2-old-test-new-tool.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/patch1.js`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/sizes-base.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/sizes-proto.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/sizes-urea-stress.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/tests-base.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/tests-proto.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/verify-same.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/L1-scratch-work`: in progress (still being written at the snapshot); not read
- `scratchpad/gov-edits/L1-after-scratchcopy.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/L1-after.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/apply-action.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/apply-critical.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/apply-critical.report.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/check-new-quotes.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/check-new-quotes.out`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/critical-limits.before.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/critical-limits.structdiff.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/entry-problems.ts`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/facts.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/facts.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/jsondiff.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/jsonlines.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/mopup-decisions/arbiter`: in progress (still being written at the snapshot); not read
- `scratchpad/mopup-impl/build-today`: in progress (still being written at the snapshot); not read
- `scratchpad/mopup-impl/probe`: in progress (still being written at the snapshot); not read
- `scratchpad/mopup-impl/build-items.before.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/mopup-triage/consolidated`: in progress (still being written at the snapshot); not read
- `scratchpad/review3/review-dataflow/repo/node_modules`: installed packages, not proof
- `scratchpad/review3/verify-dataflow/repo/node_modules`: installed packages, not proof
- `scratchpad/ws3-wave2/WS3-09-fix`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-35-fix`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-37`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-38`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/merge-09`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/review-WS3-09`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/STATE.md`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/ws3-wave2/review-ws3-09-frozen-round2.json`: written in the last 20 minutes before the snapshot; not read

## 5. Cloud sessions this session started

This session is `session_016mEXZE6RheLMXSZTgYDUrW` on claude.ai. It started the sessions below; their own transcripts are on
claude.ai, not here. What each did is read from the main transcript, the programme branch's commits and the batch
scorecards.

| Session | Title | Created (UTC) | Last status seen | What it did | Proof |
|---|---|---|---|---|---|

## 6. Worktrees and branches: work not merged into the programme branch

Compared with `claude/wonderful-meitner-l4g7p5` at `e5b42ff13608`. A worktree in progress was not read (no status, no files).

| Worktree | Branch | HEAD | In progress | Commits not merged | Uncommitted changes |
|---|---|---|---|---|---|
| `/home/user/eva-health` | `claude/wonderful-meitner-l4g7p5` | `e5b42ff13608` | no | 0 | none |
| `/home/user/eva-health/.claude/worktrees/approval-fixes` | `central-fixes-wip` | `0ea1b343d342` | no | 0 | ?? docs/signoff/work/refutations/round-2/f12_white_cells_core--K1--nlr.both.65-74.none--high-a.json; ?? docs/signoff/work/refutations/round-2/f12_white_cells_core--K1--nlr.both.65-74.none--high-b.json; ?? docs/signoff/work/refutations/round-2/f12_white_cells_core--L2--neutrophils_absolute.female.All |
| `/home/user/eva-health/.claude/worktrees/gov` | `gov` | `b8aa500ad872` | yes | 5: b8aa500 2026-11-11T22:03:54+00:00 Governance: E6 vitest case and known issue C-32 for the M-04 transition; 4705992 2026-11-11T21:52:20+00:00 Governance: E6 baseline without the placeholder floor 0 on four locked rows (ruling M-04), for review; 76e9255 2026-11-11T21:48:47+00:00 Governance: Echevarne' | (not read: in progress) |
| `/home/user/eva-health/.claude/worktrees/mopup` | `mopup` | `e5b42ff13608` | yes | 0 | (not read: in progress) |
| `/home/user/eva-health/.claude/worktrees/ws3-a` | `ws3-a` | `209dd6cf99e4` | no | 0 | none |
| `/home/user/eva-health/.claude/worktrees/ws3-b` | `ws3-b` | `6cf61b7ad3ba` | no | 1: 6cf61b7 2026-11-10T13:33:55+00:00 Runner tests: every temporary fixture under one root removed after the run | none |
| `/home/user/eva-health/.claude/worktrees/ws3-c` | `ws3-c` | `c23d607ea5fc` | yes | 1: c23d607 2026-11-11T21:54:47+00:00 WS3-37: a spelling match never crosses a lipoprotein class, a quantity, a letter or a ratio | (not read: in progress) |
| `/home/user/eva-health/.claude/worktrees/ws3-d` | `ws3-d` | `dc0df7b60771` | no | 1: dc0df7b 2026-11-11T21:46:50+00:00 WS3-38: an electrolyte in mmol/L is its mEq/L; a unit with the same number is relabelled, not refused | none |
| `/home/user/eva-health/.claude/worktrees/ws3-e` | `ws3-e` | `9c2e727e296d` | yes | 1: 9c2e727 2026-11-11T22:05:52+00:00 Tools: briefs say each split action-limit text once; size ceiling per marker; September paragraph starts where its summary starts | (not read: in progress) |
| `/home/user/eva-health/.claude/worktrees/ws3-f` | `ws3-f` | `4b4b2770fdfc` | yes | 0 | (not read: in progress) |

| Branch | HEAD | Last commit (UTC) | Created (reflog) | Commits not merged |
|---|---|---|---|---|
| `central-fixes-wip` | `0ea1b34` | 2026-11-10 08:52 | 2026-11-10 08:30 | 0 |
| `claude/wonderful-meitner-l4g7p5` | `e5b42ff` | 2026-11-11 22:03 | 2026-10-28 13:49 | 0 |
| `gov` | `b8aa500` | 2026-11-11 22:03 | 2026-11-11 20:56 | 5: b8aa500 2026-11-11T22:03:54+00:00 Governance: E6 vitest case and known issue C-32 for the M-04 transition; 4705992 2026-11-11T21:52:20+00:00 Governance: E6 baseline without the placeholder floor 0 on four locked rows (ruling M-04), for review; 76e9255 2026-11-11T21:48:47+00:00 Governance: Echevarne' |
| `main` | `c472974` | 2026-09-22 17:20 | 2026-10-28 13:49 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `mopup` | `e5b42ff` | 2026-11-11 22:03 | 2026-11-11 20:56 | 0 |
| `signoff-b01-evidence` | `5bb68dc` | 2026-11-08 06:44 | 2026-11-08 06:18 | 1: 5bb68dc 2026-11-08T06:44:49+00:00 Sign-off programme: B01 evidence repair: quotes that E1 and E2 flagged, copied from the PubMed or Europe PMC record |
| `signoff-runner-r4` | `a95eb33` | 2026-11-08 04:14 | 2026-11-08 03:31 | 1: a95eb33 2026-11-08T04:14:06+00:00 Sign-off runner round 4: D5 compares every column and the change list; G2 compares messages and explanatory numbers; B2 probes isolate their rule |
| `signoff-runner-r4-repair` | `bf9101c` | 2026-11-08 07:25 | 2026-11-08 06:49 | 2: bf9101c 2026-11-08T07:25:38+00:00 Sign-off runner round 4 repair: D5 holds every difference from production, on every column, to the change list; a seed bound must be a number; a95eb33 2026-11-08T04:14:06+00:00 Sign-off runner round 4: D5 compares every column and the change list; G2 compares messag |
| `signoff-runner-r4-repair-verify` | `94fa6e6` | 2026-11-08 07:58 | 2026-11-08 07:26 | 3: 94fa6e6 2026-11-08T07:58:38+00:00 Sign-off runner round 4 repair review: reject, an added row's other columns are held only to the migration; bf9101c 2026-11-08T07:25:38+00:00 Sign-off runner round 4 repair: D5 holds every difference from production, on every column, to the change list; a seed bound |
| `signoff-runner-r4-verify` | `999c2be` | 2026-11-08 06:49 | 2026-11-08 06:47 | 2: 999c2be 2026-11-08T06:49:03+00:00 Sign-off runner round 4 review: reject, D5 does not hold changes on the other columns to the change list; a95eb33 2026-11-08T04:14:06+00:00 Sign-off runner round 4: D5 compares every column and the change list; G2 compares messages and explanatory numbers; B2 probes |
| `signoff-runner-r5` | `45a239e` | 2026-11-08 12:13 | 2026-11-08 08:01 | 4: 45a239e 2026-11-08T12:13:38+00:00 Sign-off runner round 5: G1 tests that the compile is idempotent and hashes the judge prompts; G2 holds added rows to a template; E1 follows its specified scope; 94fa6e6 2026-11-08T07:58:38+00:00 Sign-off runner round 4 repair review: reject, an added row's other co |
| `signoff-runner-r5-repair` | `26c1257` | 2026-11-08 16:43 | 2026-11-08 12:52 | 5: 26c1257 2026-11-08T16:43:47+00:00 Sign-off runner round 5 repair: G1 holds the reconciliation set D6 reads to the compile; E1 holds every split to a record; 45a239e 2026-11-08T12:13:38+00:00 Sign-off runner round 5: G1 tests that the compile is idempotent and hashes the judge prompts; G2 holds added |
| `signoff-runner-r5-verify` | `dd6ca45` | 2026-11-08 12:51 | 2026-11-08 12:14 | 5: dd6ca45 2026-11-08T12:51:36+00:00 Sign-off runner round 5 review: reject, G1 does not hold the reconciliation set D6 reads, and E1 lets a split go without a record; 45a239e 2026-11-08T12:13:38+00:00 Sign-off runner round 5: G1 tests that the compile is idempotent and hashes the judge prompts; G2 hol |
| `signoff-runner-r5-verify-repair` | `9e897cd` | 2026-11-08 17:16 | 2026-11-08 16:44 | 6: 9e897cd 2026-11-08T17:16:44+00:00 Sign-off runner round 5 repair review: accept, G1 holds the reconciliation set D6 reads and every split needs a record; 26c1257 2026-11-08T16:43:47+00:00 Sign-off runner round 5 repair: G1 holds the reconciliation set D6 reads to the compile; E1 holds every split to |
| `worktree-wf_0b31701a-bdd-1` | `c472974` | 2026-09-22 17:20 | 2026-11-08 06:18 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_3ebe2253-c2c-1` | `c472974` | 2026-09-22 17:20 | 2026-11-08 08:00 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_3ebe2253-c2c-2` | `c472974` | 2026-09-22 17:20 | 2026-11-08 12:14 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_3ebe2253-c2c-3` | `c472974` | 2026-09-22 17:20 | 2026-11-08 12:52 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_3ebe2253-c2c-4` | `c472974` | 2026-09-22 17:20 | 2026-11-08 16:44 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_f4eaa1cf-5f1-1` | `c472974` | 2026-09-22 17:20 | 2026-11-08 03:31 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_f4eaa1cf-5f1-2` | `c472974` | 2026-09-22 17:20 | 2026-11-08 04:14 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_f4eaa1cf-5f1-3` | `c472974` | 2026-09-22 17:20 | 2026-11-08 06:49 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `worktree-wf_f4eaa1cf-5f1-4` | `c472974` | 2026-09-22 17:20 | 2026-11-08 07:26 | 2: c472974 2026-09-22T17:20:21+08:00 Merge pull request #61: Retirar el botón «Recompute all scores»; huella de host en el correo de cierre; protección de contraseñas filtradas no se activa; 94b60d8 2026-09-22T09:16:29+00:00 admin: remove the "Recompute all scores" button; host-key request in the closi |
| `ws3-a` | `209dd6c` | 2026-11-10 13:28 | 2026-11-10 10:32 | 0 |
| `ws3-b` | `6cf61b7` | 2026-11-10 13:33 | 2026-11-10 10:32 | 1: 6cf61b7 2026-11-10T13:33:55+00:00 Runner tests: every temporary fixture under one root removed after the run |
| `ws3-c` | `c23d607` | 2026-11-11 21:54 | 2026-11-10 15:04 | 1: c23d607 2026-11-11T21:54:47+00:00 WS3-37: a spelling match never crosses a lipoprotein class, a quantity, a letter or a ratio |
| `ws3-d` | `dc0df7b` | 2026-11-11 21:46 | 2026-11-10 15:04 | 1: dc0df7b 2026-11-11T21:46:50+00:00 WS3-38: an electrolyte in mmol/L is its mEq/L; a unit with the same number is relabelled, not refused |
| `ws3-e` | `9c2e727` | 2026-11-11 22:05 | 2026-11-10 16:22 | 1: 9c2e727 2026-11-11T22:05:52+00:00 Tools: briefs say each split action-limit text once; size ceiling per marker; September paragraph starts where its summary starts |
| `ws3-f` | `4b4b277` | 2026-11-11 21:11 | 2026-11-10 16:29 | 0 |

## 7. In progress at the snapshot (not read, not archived)

- `scratchpad/brief-size/proto`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-base`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-m1`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-m2`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-proto`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/root-urea`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/round1`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/tmp`: in progress (still being written at the snapshot); not read
- `scratchpad/brief-size/decision.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/dups.js`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/measure-base-vs-committed.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/measure.js`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mkroot-gov.sh`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mkroot.sh`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mutant-m1.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/mutant-m2-old-test-new-tool.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/patch1.js`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/sizes-base.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/sizes-proto.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/sizes-urea-stress.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/tests-base.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/tests-proto.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/brief-size/verify-same.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/L1-scratch-work`: in progress (still being written at the snapshot); not read
- `scratchpad/gov-edits/L1-after-scratchcopy.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/L1-after.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/apply-action.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/apply-critical.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/apply-critical.report.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/check-new-quotes.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/check-new-quotes.out`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/critical-limits.before.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/critical-limits.structdiff.txt`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/entry-problems.ts`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/facts.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/facts.json`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/jsondiff.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/gov-edits/jsonlines.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/mopup-decisions/arbiter`: in progress (still being written at the snapshot); not read
- `scratchpad/mopup-impl/build-today`: in progress (still being written at the snapshot); not read
- `scratchpad/mopup-impl/probe`: in progress (still being written at the snapshot); not read
- `scratchpad/mopup-impl/build-items.before.cjs`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/mopup-triage/consolidated`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-09-fix`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-35-fix`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-37`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/WS3-38`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/merge-09`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/review-WS3-09`: in progress (still being written at the snapshot); not read
- `scratchpad/ws3-wave2/STATE.md`: written in the last 20 minutes before the snapshot; not read
- `scratchpad/ws3-wave2/review-ws3-09-frozen-round2.json`: written in the last 20 minutes before the snapshot; not read
- worktree `/home/user/eva-health/.claude/worktrees/gov` (branch `gov`, HEAD `b8aa500ad872`)
- worktree `/home/user/eva-health/.claude/worktrees/mopup` (branch `mopup`, HEAD `e5b42ff13608`)
- worktree `/home/user/eva-health/.claude/worktrees/ws3-c` (branch `ws3-c`, HEAD `c23d607ea5fc`)
- worktree `/home/user/eva-health/.claude/worktrees/ws3-e` (branch `ws3-e`, HEAD `9c2e727e296d`)
- worktree `/home/user/eva-health/.claude/worktrees/ws3-f` (branch `ws3-f`, HEAD `4b4b2770fdfc`)

## 8. Test fixtures in /tmp

13740 folders `/tmp/dsrt-*`, 11.5 GB: listed in `dsrt-fixtures.md`, not copied.
