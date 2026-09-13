$ErrorActionPreference = 'Stop'

$VBox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$Iso = 'C:\Users\Example\Downloads\enterprise-purple-range-media\WindowsServer2025-EVAL-en-us.iso'
$Vm = 'EPR-DC01'
$BaseRoot = 'C:\Users\Example\VirtualBox VMs'
$VmRoot = 'C:\Users\Example\VirtualBox VMs\EPR-DC01'
$SecretRoot = 'C:\Users\Example\Projects\enterprise-purple-range\secrets'
$PasswordFile = Join-Path $SecretRoot 'dc01-password.txt'

if (-not (Test-Path -LiteralPath $Iso)) { throw 'Official Windows Server evaluation ISO is unavailable.' }
if (& $VBox list vms | Select-String -SimpleMatch ('"' + $Vm + '"')) { throw 'EPR-DC01 already exists.' }
New-Item -ItemType Directory -Path $SecretRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $PasswordFile)) {
    $bytes = New-Object byte[] 24
    [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $password = 'Avr!' + [Convert]::ToBase64String($bytes).Replace('/', '7').Replace('+', 'Q')
    [IO.File]::WriteAllText($PasswordFile, $password)
}
& $VBox createvm --name $Vm --ostype Windows2025_64 --basefolder $BaseRoot --register
& $VBox modifyvm $Vm --memory 2048 --cpus 2 --firmware bios --graphicscontroller vboxsvga --vram 128 --boot1 dvd --boot2 disk --boot3 none --boot4 none --nic1 intnet --intnet1 epr-isolated --macaddress1 080027880010 --nic2 none --audio-enabled off --clipboard disabled --draganddrop disabled
& $VBox createmedium disk --filename (Join-Path $VmRoot 'EPR-DC01.vdi') --size 51200 --format VDI --variant Standard
& $VBox storagectl $Vm --name SATA --add sata --controller IntelAhci
& $VBox storageattach $Vm --storagectl SATA --port 0 --device 0 --type hdd --medium (Join-Path $VmRoot 'EPR-DC01.vdi')
& $VBox unattended install $Vm --iso $Iso --user lablocal --full-user-name 'AVR Lab Local' --user-password-file $PasswordFile --admin-password-file $PasswordFile --image-index 2 --locale en_US --country US --time-zone 'Europe/Istanbul' --hostname dc01.lab.avr.local --install-additions *> $null
if ($LASTEXITCODE -ne 0) { throw 'VirtualBox unattended preparation failed.' }
$Answer = Get-ChildItem -LiteralPath $VmRoot -Filter '*-autounattend.xml' | Select-Object -Single -ExpandProperty FullName
$Xml = [IO.File]::ReadAllText($Answer)
$Needle = '</CreatePartitions>'
$Partition = @'
</CreatePartitions>
                    <ModifyPartitions>
                        <ModifyPartition wcm:action="add">
                            <Order>1</Order><PartitionID>1</PartitionID><Active>true</Active>
                            <Format>NTFS</Format><Label>Windows</Label><Letter>C</Letter>
                        </ModifyPartition>
                    </ModifyPartitions>
'@
if (-not $Xml.Contains('<ModifyPartitions>')) {
    if (-not $Xml.Contains($Needle)) { throw 'Generated answer file has no partition insertion point.' }
    [IO.File]::WriteAllText($Answer, $Xml.Replace($Needle, $Partition))
}
& $VBox modifyvm $Vm --boot1 dvd --boot2 disk --boot3 none --boot4 none
& $VBox startvm $Vm --type headless
