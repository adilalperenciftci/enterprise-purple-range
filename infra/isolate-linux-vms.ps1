[CmdletBinding()]
param([ValidateSet('kali', 'meta', 'all')][string]$MachineName = 'all')
$ErrorActionPreference = 'Stop'

$VBox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$Root = 'C:\Users\Example\Projects\enterprise-purple-range'
$VagrantRoot = Join-Path $Root 'infra\range'
$SecretRoot = Join-Path $Root 'secrets'
New-Item -ItemType Directory -Path $SecretRoot -Force | Out-Null

$Machines = @(
    @{ Vagrant = 'kali'; User = 'vagrant'; Secret = 'kali-password.txt'; Vm = 'EPR-KALI'; Mac = '080027880030' },
    @{ Vagrant = 'meta'; User = 'vagrant'; Secret = 'meta-password.txt'; Vm = 'EPR-META'; Mac = '080027880040' }
)
if ($MachineName -ne 'all') { $Machines = @($Machines | Where-Object Vagrant -eq $MachineName) }
foreach ($Machine in $Machines) {
    $Secret = Join-Path $SecretRoot $Machine.Secret
    if (-not (Test-Path -LiteralPath $Secret)) {
        $bytes = New-Object byte[] 24
        [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
        [IO.File]::WriteAllText($Secret, 'Avr!' + [Convert]::ToBase64String($bytes).Replace('/', '7').Replace('+', 'Q'))
    }
    $Upload = Join-Path $SecretRoot ($Machine.Vagrant + '-chpasswd.txt')
    [IO.File]::WriteAllText($Upload, $Machine.User + ':' + [IO.File]::ReadAllText($Secret).Trim())
    Push-Location $VagrantRoot
    try {
        vagrant upload $Upload /tmp/epr-chpasswd $Machine.Vagrant
        if ($LASTEXITCODE -ne 0) { throw 'Credential staging failed.' }
        vagrant ssh $Machine.Vagrant -c "sudo sh -c 'chpasswd < /tmp/epr-chpasswd && rm -f /tmp/epr-chpasswd'"
        if ($LASTEXITCODE -ne 0) { throw 'Lab credential rotation failed.' }
        vagrant halt $Machine.Vagrant
        if ($LASTEXITCODE -ne 0) { throw 'VM halt failed.' }
    } finally {
        Pop-Location
        if (Test-Path -LiteralPath $Upload) { Remove-Item -LiteralPath $Upload -Force }
    }
    $Info = & $VBox showvminfo $Machine.Vm --machinereadable
    if (($Info | Select-String '^name=').Line -ne ('name="' + $Machine.Vm + '"')) { throw 'VM identity mismatch.' }
    & $VBox modifyvm $Machine.Vm --nic1 null --nic2 intnet --intnet2 epr-isolated --macaddress2 $Machine.Mac
    if ($LASTEXITCODE -ne 0) { throw 'VM isolation failed.' }
}
