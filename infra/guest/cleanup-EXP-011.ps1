$ErrorActionPreference = 'Stop'
$Root = 'C:\AVR-Lab\Experiments\EXP-011'
if (Test-Path -LiteralPath $Root) { Remove-Item -LiteralPath $Root -Recurse -Force }
if (Test-Path -LiteralPath $Root) { throw 'EXP-011 cleanup failed.' }
