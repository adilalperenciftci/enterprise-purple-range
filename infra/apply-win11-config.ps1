[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('Telemetry', 'DomainJoin', 'Experiments')][string]$Phase)
$ErrorActionPreference = 'Stop'

$VBox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$Root = 'C:\Users\Example\Projects\enterprise-purple-range'
$ToolRoot = 'C:\Users\Example\Downloads\enterprise-purple-range-tools'
$SecretRoot = Join-Path $Root 'secrets'
$LoginSecret = Join-Path $SecretRoot 'win11-password.txt'
$DomainSecrets = Join-Path $SecretRoot 'domain-passwords.json'
$LabAdminSecret = Join-Path $SecretRoot 'labadmin-password.txt'
$Vm = 'EPR-WIN11'

if (-not (Test-Path -LiteralPath $LoginSecret)) { throw 'WIN11 login secret is unavailable.' }
$User = 'lablocal'
$AuthSecret = $LoginSecret
if ($Phase -eq 'Experiments') {
    if (-not (Test-Path -LiteralPath $LabAdminSecret)) {
        if (-not (Test-Path -LiteralPath $DomainSecrets)) { throw 'Domain secrets are unavailable.' }
        $Secrets = Get-Content -Raw -LiteralPath $DomainSecrets | ConvertFrom-Json
        [IO.File]::WriteAllText($LabAdminSecret, $Secrets.labadmin)
    }
    $User = 'LAB\labadmin'
    $AuthSecret = $LabAdminSecret
}
function Invoke-Guest([string[]]$Arguments) {
    & $VBox guestcontrol $Vm @Arguments --username $User --passwordfile $AuthSecret
    if ($LASTEXITCODE -ne 0) { throw 'VirtualBox guest operation failed.' }
}

Invoke-Guest @('mkdir', '--parents', 'C:\AVR-Provision')
if ($Phase -eq 'Telemetry') {
    $User = 'lablocal'
    Invoke-Guest @('copyto', '--target-directory=C:\AVR-Provision\',
        (Join-Path $ToolRoot 'Sysmon\Sysmon64.exe'),
        (Join-Path $Root 'detections\sysmon\sysmon-epr.xml'),
        (Join-Path $Root 'infra\guest\configure-windows-telemetry.ps1'))
    & $VBox guestcontrol $Vm run --username $User --passwordfile $AuthSecret `
        --exe 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -- `
        -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File 'C:\AVR-Provision\configure-windows-telemetry.ps1'
} elseif ($Phase -eq 'DomainJoin') {
    if (-not (Test-Path -LiteralPath $DomainSecrets)) { throw 'Domain secrets are unavailable.' }
    Invoke-Guest @('copyto', '--target-directory=C:\AVR-Provision\',
        (Join-Path $Root 'infra\guest\join-win11-domain.ps1'), $DomainSecrets)
    & $VBox guestcontrol $Vm run --username $User --passwordfile $AuthSecret `
        --exe 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -- `
        -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File 'C:\AVR-Provision\join-win11-domain.ps1'
} else {
    Invoke-Guest @('mkdir', '--parents', 'C:\AVR-Lab\Experiments')
    Invoke-Guest @('copyto', '--target-directory=C:\AVR-Lab\Experiments\',
        (Join-Path $Root 'infra\guest\EXP-011.ps1'),
        (Join-Path $Root 'infra\guest\cleanup-EXP-011.ps1'))
}
