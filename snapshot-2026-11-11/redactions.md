# Redactions

Every redaction made while packing the archives, by file and kind. No value is shown.

- The CEO's email address is replaced with `[CEO email]`.
- Anything that looks like a secret is replaced with `[redacted secret]`. For a header, a variable or a
  password field only the value is replaced; the name stays so the reader sees what was there.
- Files in the repository are not packed here (they are listed with their hashes in MANIFEST.md),
  so they are not redacted. The repository holds no live secret: its `.env.example` has placeholders.
- The rules are in `make-evidence.py` (`SECRET_RULES`). Values that look like placeholders
  (`placeholder`, `example`, `process.env.X`, `${X}` and similar) are left as they are.

## Totals

| Kind | Replacements | Files |
|---|---|---|
| CEO email | 553 | 235 |
| JWT | 5 | 3 |
| Google API key | 2 | 2 |

## By file

| Archive | File | Kind | Count |
|---|---|---|---|
| scratch | `scratchpad/dl_ech/ech.html` | JWT | 2 |
| scratch | `scratchpad/web/ech_liposcale_en.html` | JWT | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958.jsonl` | CEO email | 63 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/agent-a1f70575a71782f72.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/agent-a29dc4421ec892bc8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/agent-a5f08227adfba878a.jsonl` | CEO email | 1 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/agent-ab7223897a1252b43.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a0cbe0378a314343d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a118a8ef19d246126.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a12ca1c730a4a8617.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a4149f7c3940ef016.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a50d7627a4c182834.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a727cb1e1fe0a1eb2.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a9393397bb4bb111f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-a9983b7b237762a52.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-aa85498c5f88bce90.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-ae1a229cfce6dec1d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-aeca0e70dde61006f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_0cf90519-582/agent-aff44ae7a9fb9d3d7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_24c12a30-a47/agent-a42415b63e9c176e5.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_24c12a30-a47/agent-a9612b2248517f99e.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_24c12a30-a47/agent-ad501311633c6c468.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_24c12a30-a47/agent-ae2fe587449f6a1c4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_24c12a30-a47/agent-ae62a975ce248d5c8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_24c12a30-a47/agent-aec1dae76571c4908.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a004926c5a3cd4c62.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a007397a256450350.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a0b17cd4e33990048.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a0debf334f0bb73ac.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a156e58365ba38444.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a19b03f9ecf76baaa.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a1bb8ded9b0400c84.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a1c21f079905029b9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a1f8a28998084bd41.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a1f972d2d1debb04d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a2bcc8911901cfd2c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a2d9c18c5fc5286cf.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a31e29236b137f1ba.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a31eb618b73174b79.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a32cdf08a07dd7214.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a359c59f041e1f23a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a3b6ad562a58de4d3.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a4063d917084dc37c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a41472d93ce49df82.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a421d75eefef83514.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a44842761e96e0349.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a4f8bfac9e1596d31.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a58de95628a8f7f01.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a635b259e1b8d0ca8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a69248bea0c90d33c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a69906cf712ec3c10.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a69e1fe0c2b28d4d4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a730d843e2002fa39.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a799140c64f81d5a8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a834179ea3469f9b1.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a86121ea3c848874c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a87a0f9c9d53ae7aa.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a8c582d68fbfc89bf.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a90519e6a2d88d95d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a917b6ff2d9a83cfe.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a939c5d9e4f66169c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a93cc418dfeb5999f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a96bcad07d84fd427.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a989a16962eb6cc18.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a98cae860fa8dfc9f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-a9c967c95cda3e543.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-aa351edd99fe976ab.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-aaba13c78730128f9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-aac2b9dadff65f0e0.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab16821d48e129855.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab28ebb9deb41f03f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab5a1c7fa2879a89a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab6fa8e98117d8de3.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab79c73bbcad68bfa.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab9b4050722d6dd03.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ab9c1def994f9a9eb.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-abe488da6f0522f63.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ac00dae9f13b1c764.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ac2a345430552fdc4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ac2d6cd61273d0bb9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ac98d2a6d29c2fe35.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-accd1f5427eccb8ee.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ad24a7e17af5ce705.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ad3f71beff965d400.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ad4c7cee285b72dfb.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ad561e325170ec821.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ad5f76b6cd5620776.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ad714b28bf33f3f72.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-adb375766fdfd2744.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-adb4caa870d5657a7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-adc9599dd2f501648.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ae44d458f8419e464.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ae592b3473f9f026c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ae6b39c6c46570c8a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-ae8de4e1528fa0b61.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-af1df7a2f1620ff19.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-af70c3d42994f5a6c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-afc7ca0d9bb19b1c0.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-afe32374601aa967c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_2dfbae57-bfa/agent-affe332c4cf9ded2c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a02d588f60bde1b5d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a06f170e71869179a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a0e8dfaaf6b265b7e.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a13432b80c0fcbdc7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a1f6c1f9e1d3d10ba.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a316f21a5f656f1c7.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a4c55a4d3bbef50bf.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a59c94823ce9a842f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a5ab0c09e78c962bb.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a770a11b8ed0dc2b2.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a82aad9f9656952fe.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-a943570246d5db5c1.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-aa25d45424dae958d.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-ac7278b0f0d32fa6d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-acc73857ba69f3943.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-ace6facdcfa382f85.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-ae02318931c6fd2f8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_368394f5-ac1/agent-ae4dee5f74d60a6e4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_3b28caa2-afe/agent-a863ce7fbb8fcf14f.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_3b28caa2-afe/agent-ab1e45820219fb82f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_3b28caa2-afe/agent-ad4f805800d53abbf.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_3b28caa2-afe/agent-ad962865c3af7cd58.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-a1be002a6b881a7c8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-a1c5c127922b93d70.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-a2d9a51052e60eaf8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-a87a3ec7b809574da.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-ab4871eb18f26b4ac.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-ad77e7e302ced1e0f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-afb52405168a1d6d5.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4359442e-d59/agent-afba2f6f0b796c1dc.jsonl` | CEO email | 3 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a0fbe9d5feb7935f8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a1f9f49c5f1c749ad.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a2de57d0616652a26.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a71b5d07340678a56.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a7a5bb6ffbb48f6a0.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a7d117b44aef6cf5b.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a8c6aac93351a62e4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a8d47b7a3d01e2c7f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a97e9753f995b03cb.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-a9a4ee55e4bb9a6c8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-ac5aa9f10dcd0ecf8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-acccef788b88b4dd9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-ae022400d168e3623.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-ae4ebb67ece7b7a40.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_4f895304-027/agent-aeecb90aeec958840.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_62eb781c-732/agent-a4a2ef8a38e83963f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_62eb781c-732/agent-a81adbfcb8b88bef7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_62eb781c-732/agent-a8467891dbd30a4cc.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a091760cea873579e.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a0c69863409f538fe.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a1672dc5ce1f36a97.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a27da6450d562dc4f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a2bb5414f767fd268.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a33c8a024d6053e5f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a35fa0f6884263cda.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a3718e2d45e5187bf.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a381d1a498b3da8f2.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a392dadad7da9c59e.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a3941642a3115dbce.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a3adf19b930accaf3.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a3d696d63f79e53fd.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a40d7bb15d118a335.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a453706c164be5a9d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a49072e749e34f45b.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a49072e749e34f45b.jsonl` | JWT | 1 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a4bb16e7ab816e0c0.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a4c70d572c0d0663b.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a5261eaa3f7a4dab7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a54fae59e661f3e23.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a54fba49358ad95e3.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a555dce2da970c12d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a57cdf469c520eee3.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a5b55c241c68e72af.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a5bdc9f7077b0feb2.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a5d1f5617cac695ec.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a5db2750fbdf0a3f2.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a5de230deb07272a8.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a60959f256af6cd0a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a62c6e266491ceed9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a63acc14988c0be87.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a6902fe7cd6ae8a51.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a69f4a07ea4beb88d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a6b703d38cc4eb188.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a726c9bb0a1ba541f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a75789bef2234a5cd.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a7c8dfb91497204f4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a81b48b6493e31782.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a85680c75ca553bb0.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a888e9c57a0c961c7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a8f6115e081efbf8c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a945dbf69ad105f4a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a95f97d85cb1f72d2.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a960ce2d6665acef4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a995a67003a32dffd.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a9963a4f7db089425.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a9d7c485d58eadce7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a9f27281156343df3.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-a9f855ab05698f278.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa3478815f6ef5886.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa3478815f6ef5886.jsonl` | Google API key | 1 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa441b9559e5d9795.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa45333ce2a202006.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa5c8f206e3a32ba1.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa6be3d708632428b.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aa83f1e9a4ec1acb1.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aab14be3b523da399.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aab1a820f7eb0c2b9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aab24e527b505cae6.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aaca26a4c251e3b9a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ab255cf5690a161fb.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ab26ba85f3226b712.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-abaa7e459dedfbed5.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-abda0546a21255af1.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-abe76736225cdd22b.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ac5a61670df0f6245.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ac7fb1ecf06690322.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ac95ab3a742dd1100.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-acc713f218b5e064f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-acce56bca66bc7cb7.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-acd6a7041bf372415.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-acf210b95805665ee.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ad6cbbcbbffdadde9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ada4e06ee1c2a8d0f.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-adb8d10832578cc89.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-addec4cf897d171e4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ae1d2cdbdcd44b358.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-ae2ce65174c55eb82.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-aeec4ed3810337a3c.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-af05faa76236de3da.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-af216a9108ed3a6b9.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-af356ca7aab50190a.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-af7ef304b31a43492.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-af9e02fe67aaefbe4.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-afaebb35575774427.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_b2b87189-304/agent-affc590b632db765d.jsonl` | CEO email | 2 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_fa799dd0-32b/agent-a199a535eee9fbe43.jsonl` | CEO email | 11 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_fa799dd0-32b/agent-a42d5714339753964.jsonl` | CEO email | 1 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_fa799dd0-32b/agent-a7768ac9786cab88e.jsonl` | CEO email | 1 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/subagents/workflows/wf_fa799dd0-32b/agent-aed3bfe3f2a692970.jsonl` | CEO email | 11 |
| transcripts | `4e1a7523-c199-547a-904f-d87e53286958/tool-results/bhqr5b98c.txt` | Google API key | 1 |

## JSON lines changed in form

None: every transcript line that parsed before a replacement still parses after it.

## Check after packing

On 2026-11-11T21:49:12Z every part was read back and every archived file scanned again with the same rules.

| Part | Size | Under 45 MB | sha256 matches | Files read | Matches left |
|---|---|---|---|---|---|
| `transcripts/transcripts.part01.tar.xz` | 38.5 MB | yes | yes | 555 | none |
| `transcripts/transcripts.part02.tar.xz` | 38.7 MB | yes | yes | 467 | none |
| `transcripts/transcripts.part03.tar.xz` | 38.8 MB | yes | yes | 376 | none |
| `transcripts/transcripts.part04.tar.xz` | 38.7 MB | yes | yes | 464 | none |
| `transcripts/transcripts.part05.tar.xz` | 35.6 MB | yes | yes | 291 | none |
| `transcripts/transcripts.part06.tar.xz` | 23.1 MB | yes | yes | 949 | none |
| `scratch/scratch.part01.tar.xz` | 39.0 MB | yes | yes | 7837 | none |
| `scratch/scratch.part02.tar.xz` | 37.6 MB | yes | yes | 13373 | none |
