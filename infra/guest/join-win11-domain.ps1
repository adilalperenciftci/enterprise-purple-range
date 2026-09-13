$ErrorActionPreference = 'Stop'
Start-Transcript -LiteralPath 'C:\AVR-Provision\join-win11-domain.log' -Force

$Interface = Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | Select-Object -First 1
if (-not $Interface) { throw 'No active isolated adapter was found.' }
Get-NetIPAddress -InterfaceIndex $Interface.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object IPAddress -ne '10.88.0.20' | Remove-NetIPAddress -Confirm:$false
if (-not (Get-NetIPAddress -InterfaceIndex $Interface.ifIndex -IPAddress '10.88.0.20' -ErrorAction SilentlyContinue)) {
    New-NetIPAddress -InterfaceIndex $Interface.ifIndex -IPAddress '10.88.0.20' -PrefixLength 24
}
Set-DnsClientServerAddress -InterfaceIndex $Interface.ifIndex -ServerAddresses '10.88.0.10'

$SecretPath = 'C:\AVR-Provision\domain-passwords.json'
if (-not (Test-Path -LiteralPath $SecretPath)) { throw 'Domain join secret was not staged.' }
$Secrets = Get-Content -Raw -LiteralPath $SecretPath | ConvertFrom-Json
$Credential = [PSCredential]::new(
    'LAB\labadmin',
    (ConvertTo-SecureString $Secrets.labadmin -AsPlainText -Force)
)
if ($env:COMPUTERNAME -eq 'WIN11') {
    Add-Computer -DomainName 'LAB.AVR.LOCAL' -Credential $Credential -Force
} else {
    Add-Computer -DomainName 'LAB.AVR.LOCAL' -Credential $Credential -NewName 'WIN11' -Force
}
Remove-Item -LiteralPath $SecretPath -Force
Stop-Transcript
Restart-Computer -Force
