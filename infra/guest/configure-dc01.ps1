$ErrorActionPreference = 'Stop'
Start-Transcript -LiteralPath 'C:\AVR-Provision\configure-dc01.log' -Force

$Interface = Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | Select-Object -First 1
if (-not $Interface) { throw 'No active isolated adapter was found.' }
Get-NetIPAddress -InterfaceIndex $Interface.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object IPAddress -ne '10.88.0.10' | Remove-NetIPAddress -Confirm:$false
if (-not (Get-NetIPAddress -InterfaceIndex $Interface.ifIndex -IPAddress '10.88.0.10' -ErrorAction SilentlyContinue)) {
    New-NetIPAddress -InterfaceIndex $Interface.ifIndex -IPAddress '10.88.0.10' -PrefixLength 24
}
Set-DnsClientServerAddress -InterfaceIndex $Interface.ifIndex -ServerAddresses '127.0.0.1'
if ($env:COMPUTERNAME -ne 'DC01') { Rename-Computer -NewName 'DC01' -Force }
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

$DsrmPath = 'C:\AVR-Provision\dsrm-password.txt'
if (-not (Test-Path -LiteralPath $DsrmPath)) { throw 'DSRM secret was not staged.' }
$Dsrm = ConvertTo-SecureString ([IO.File]::ReadAllText($DsrmPath).Trim()) -AsPlainText -Force
Remove-Item -LiteralPath $DsrmPath -Force
Install-ADDSForest -DomainName 'LAB.AVR.LOCAL' -DomainNetbiosName 'LAB' -InstallDNS `
    -SafeModeAdministratorPassword $Dsrm -NoRebootOnCompletion:$false -Force
