$ErrorActionPreference = 'Stop'
$Path = 'C:\AVR-Provision\replacement-password.txt'
if (-not (Test-Path -LiteralPath $Path)) { throw 'Replacement secret was not staged.' }
$Plain = [IO.File]::ReadAllText($Path).Trim()
$Secure = ConvertTo-SecureString $Plain -AsPlainText -Force
Set-LocalUser -Name 'lablocal' -Password $Secure
Set-LocalUser -Name 'Administrator' -Password $Secure
Remove-Item -LiteralPath $Path -Force
