$ErrorActionPreference = 'Stop'

$Sysmon = 'C:\AVR-Provision\Sysmon64.exe'
$Config = 'C:\AVR-Provision\sysmon-epr.xml'
if (-not (Test-Path -LiteralPath $Sysmon) -or -not (Test-Path -LiteralPath $Config)) {
    throw 'Signed Sysmon binary and configuration must be staged first.'
}
$Signature = Get-AuthenticodeSignature -LiteralPath $Sysmon
if ($Signature.Status -ne 'Valid' -or $Signature.SignerCertificate.Subject -notmatch 'Microsoft') {
    throw 'Sysmon Authenticode validation failed.'
}

& auditpol.exe /set /subcategory:'Process Creation' /success:enable /failure:enable | Out-Null
& auditpol.exe /set /subcategory:'Logon' /success:enable /failure:enable | Out-Null
& auditpol.exe /set /subcategory:'Other Logon/Logoff Events' /success:enable /failure:enable | Out-Null
& auditpol.exe /set /subcategory:'Kerberos Authentication Service' /success:enable /failure:enable | Out-Null
& auditpol.exe /set /subcategory:'Kerberos Service Ticket Operations' /success:enable /failure:enable | Out-Null
New-Item -Path 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -Force | Out-Null
New-ItemProperty -Path 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit' `
    -Name ProcessCreationIncludeCmdLine_Enabled -PropertyType DWord -Value 1 -Force | Out-Null
New-Item -Path 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -Force | Out-Null
New-ItemProperty -Path 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' `
    -Name EnableScriptBlockLogging -PropertyType DWord -Value 1 -Force | Out-Null
wevtutil.exe sl Microsoft-Windows-PowerShell/Operational /e:true

if (Get-Service Sysmon64 -ErrorAction SilentlyContinue) {
    & $Sysmon -accepteula -c $Config | Out-Null
} else {
    & $Sysmon -accepteula -i $Config | Out-Null
}
if ((Get-Service Sysmon64).Status -ne 'Running') { throw 'Sysmon service is not running.' }
