param([string]$OutputDirectory = (Join-Path $PSScriptRoot '..\bin'))
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$env:P111_LOOKUP_SHA256='f142b4051e635f6f9f8f8fbf9b18f7db9a8a2ef99dbe4e8612be46c7da65f241'
$library=Join-Path $OutputDirectory 'libcandidate.rlib'
& rustc (Join-Path $PSScriptRoot 'src\engine\lib.rs') --crate-type rlib --crate-name turktokenizer_p82 --cfg lookup_index --cfg suffix_plan --cfg allowed_rules --cfg transition_keys --edition=2021 -C opt-level=3 -C panic=abort -C codegen-units=1 -o $library
if ($LASTEXITCODE -ne 0) { throw 'Engine compilation failed' }
& rustc (Join-Path $PSScriptRoot 'src\main.rs') --edition=2021 -C opt-level=3 -C panic=abort -C codegen-units=1 --extern "turktokenizer_p82=$library" -o (Join-Path $OutputDirectory 'turktokenizer.exe')
if ($LASTEXITCODE -ne 0) { throw 'CLI compilation failed' }
