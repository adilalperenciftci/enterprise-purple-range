$ErrorActionPreference = 'Stop'

$VBox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$Iso = 'C:\Users\Example\Downloads\enterprise-purple-range-media\Windows11Enterprise25H2-EVAL-en-us.iso'
$Vm = 'EPR-WIN11'
$BaseRoot = 'C:\Users\Example\VirtualBox VMs'
$VmRoot = Join-Path $BaseRoot $Vm
$SecretRoot = 'C:\Users\Example\Projects\enterprise-purple-range\secrets'
$PasswordFile = Join-Path $SecretRoot 'win11-password.txt'

if (-not (Test-Path -LiteralPath $Iso)) { throw 'Official Windows 11 Enterprise evaluation ISO is unavailable.' }
if (& $VBox list vms | Select-String -SimpleMatch ('"' + $Vm + '"')) { throw 'EPR-WIN11 already exists.' }
New-Item -ItemType Directory -Path $SecretRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $PasswordFile)) {
    $bytes = New-Object byte[] 24
    [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    [IO.File]::WriteAllText($PasswordFile, 'Avr!' + [Convert]::ToBase64String($bytes).Replace('/', '7').Replace('+', 'Q'))
}

& $VBox createvm --name $Vm --ostype Windows11_64 --basefolder $BaseRoot --register
& $VBox modifyvm $Vm --memory 3072 --cpus 2 --firmware efi --tpm-type 2.0 --graphicscontroller vboxsvga --vram 128 --boot1 dvd --boot2 disk --boot3 none --boot4 none --nic1 intnet --intnet1 epr-isolated --macaddress1 080027880020 --nic2 none --audio-enabled off --clipboard disabled --draganddrop disabled
& $VBox createmedium disk --filename (Join-Path $VmRoot 'EPR-WIN11.vdi') --size 65536 --format VDI --variant Standard
& $VBox storagectl $Vm --name SATA --add sata --controller IntelAhci
& $VBox storageattach $Vm --storagectl SATA --port 0 --device 0 --type hdd --medium (Join-Path $VmRoot 'EPR-WIN11.vdi')
& $VBox unattended install $Vm --iso $Iso --user lablocal --full-user-name 'AVR Lab Local' --user-password-file $PasswordFile --admin-password-file $PasswordFile --image-index 1 --locale en_US --country US --time-zone 'Europe/Istanbul' --hostname win11.lab.avr.local --install-additions *> $null
if ($LASTEXITCODE -ne 0) { throw 'VirtualBox unattended preparation failed.' }
& $VBox modifyvm $Vm --boot1 dvd --boot2 disk --boot3 none --boot4 none
& $VBox startvm $Vm --type headless
