Detect secrets...........................................................Failed
- hook id: detect-secrets
- exit code: 1

ERROR: Potential secrets about to be committed to git repo!

Secret Type: Secret Keyword
Location:    ansible\roles\python_scripts\unittests\test_resolve_delinea_secret_id.py:76

Secret Type: Secret Keyword
Location:    ansible\roles\python_scripts\unittests\test_resolve_delinea_secret_id.py:407

Secret Type: Secret Keyword
Location:    ansible\roles\python_scripts\unittests\test_resolve_delinea_secret_id.py:450

Possible mitigations:
  - For information about putting your secrets in a safer place, please ask in
    #security
  - Mark false positives with an inline `pragma: allowlist secret` comment

If a secret has already been committed, visit
https://help.github.com/articles/removing-sensitive-data-from-a-repository
ERROR: Potential secrets about to be committed to git repo!

Secret Type: Secret Keyword
Location:    ansible\playbooks\disjoin-windows-domain.yaml:110

Secret Type: Secret Keyword
Location:    ansible\playbooks\join-windows-domain.yaml:116

Secret Type: Secret Keyword
Location:    ansible\roles\python_scripts\unittests\test_json_builder.py:71

Secret Type: Secret Keyword
Location:    ansible\roles\python_scripts\unittests\test_json_builder.py:72

Possible mitigations:
  - For information about putting your secrets in a safer place, please ask in
    #security
  - Mark false positives with an inline `pragma: allowlist secret` comment

If a secret has already been committed, visit
https://help.github.com/articles/removing-sensitive-data-from-a-repository