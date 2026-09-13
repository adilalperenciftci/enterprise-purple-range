[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('Promote', 'Identities')][string]$Phase)
$ErrorActionPreference = 'Stop'

$VBox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$Root = 'C:\Users\Example\Projects\enterprise-purple-range'
$SecretRoot = Join-Path $Root 'secrets'
$LoginSecret = Join-Path $SecretRoot 'dc01-password.txt'
$DsrmSecret = Join-Path $SecretRoot 'dsrm-password.txt'
$IdentitySecret = Join-Path $SecretRoot 'domain-passwords.json'
$Vm = 'EPR-DC01'

if (-not (Test-Path -LiteralPath $LoginSecret)) { throw 'Local login secret is unavailable.' }
New-Item -ItemType Directory -Path $SecretRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $DsrmSecret)) {
    $bytes = New-Object byte[] 24
    [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    [IO.File]::WriteAllText($DsrmSecret, 'Avr!' + [Convert]::ToBase64String($bytes).Replace('/', '7').Replace('+', 'Q'))
}
if (-not (Test-Path -LiteralPath $IdentitySecret)) {
    $values = [ordered]@{}
    foreach ($name in @('labadmin', 'alice', 'bob', 'svc_web', 'svc_backup', 'svc_remote')) {
        $bytes = New-Object byte[] 24
        [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
        $values[$name] = 'Avr!' + [Convert]::ToBase64String($bytes).Replace('/', '7').Replace('+', 'Q')
    }
    [IO.File]::WriteAllText($IdentitySecret, ($values | ConvertTo-Json))
}

function Invoke-Guest([string[]]$Arguments) {
    if ($Phase -eq 'Promote') {
        & $VBox guestcontrol $Vm @Arguments --username lablocal --passwordfile $LoginSecret
    } else {
        & $VBox guestcontrol $Vm @Arguments --username Administrator --domain LAB --passwordfile $LoginSecret
    }
    if ($LASTEXITCODE -ne 0) { throw 'VirtualBox guest operation failed.' }
}

Invoke-Guest @('mkdir', '--parents', 'C:\AVR-Provision')
if ($Phase -eq 'Promote') {
    Invoke-Guest @('copyto', '--target-directory=C:\AVR-Provision\', (Join-Path $Root 'infra\guest\configure-dc01.ps1'), $DsrmSecret)
    & $VBox guestcontrol $Vm run --username lablocal --passwordfile $LoginSecret `
        --exe 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -- `
        -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File 'C:\AVR-Provision\configure-dc01.ps1'
} else {
    Invoke-Guest @('copyto', '--target-directory=C:\AVR-Provision\', (Join-Path $Root 'infra\guest\create-lab-identities.ps1'), $IdentitySecret)
    & $VBox guestcontrol $Vm run --username Administrator --domain LAB --passwordfile $LoginSecret `
        --exe 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -- `
        -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File 'C:\AVR-Provision\create-lab-identities.ps1'
}
