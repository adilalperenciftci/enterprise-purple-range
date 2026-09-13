$ErrorActionPreference = 'Stop'
Import-Module ActiveDirectory

$SecretPath = 'C:\AVR-Provision\domain-passwords.json'
if (-not (Test-Path -LiteralPath $SecretPath)) { throw 'Domain identity secrets were not staged.' }
$Secrets = Get-Content -Raw -LiteralPath $SecretPath | ConvertFrom-Json
Remove-Item -LiteralPath $SecretPath -Force

$Root = 'DC=LAB,DC=AVR,DC=LOCAL'
if (-not (Get-ADOrganizationalUnit -Filter "Name -eq 'AVR Lab'" -ErrorAction SilentlyContinue)) {
    New-ADOrganizationalUnit -Name 'AVR Lab' -Path $Root -ProtectedFromAccidentalDeletion $true
}
$Ou = 'OU=AVR Lab,' + $Root
$Users = @('labadmin', 'alice', 'bob', 'svc_web', 'svc_backup', 'svc_remote')
foreach ($Name in $Users) {
    if (-not (Get-ADUser -Filter "SamAccountName -eq '$Name'" -ErrorAction SilentlyContinue)) {
        $Password = ConvertTo-SecureString $Secrets.$Name -AsPlainText -Force
        New-ADUser -Name $Name -SamAccountName $Name -Path $Ou -Enabled $true `
            -AccountPassword $Password -PasswordNeverExpires $true -ChangePasswordAtLogon $false
    }
}
Add-ADGroupMember -Identity 'Domain Admins' -Members 'labadmin' -ErrorAction SilentlyContinue

