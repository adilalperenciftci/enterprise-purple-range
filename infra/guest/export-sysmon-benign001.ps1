$ErrorActionPreference = 'Stop'
Start-Transcript -LiteralPath 'C:\AVR-Lab\Experiments\BENIGN-001-export.log' -Force

$Event = Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-Sysmon/Operational'
    Id = 1
    StartTime = (Get-Date).AddHours(-1)
} | ForEach-Object {
    $Xml = [xml]$_.ToXml()
    $Data = @{}
    foreach ($Item in $Xml.Event.EventData.Data) { $Data[$Item.Name] = [string]$Item.'#text' }
    if ($Data.Image -eq 'C:\Windows\System32\whoami.exe') {
        [pscustomobject]@{ Event = $_; Data = $Data }
    }
} | Sort-Object { $_.Event.TimeCreated } | Select-Object -Last 1
if (-not $Event) { throw 'BENIGN-001 process creation was not found.' }
$Output = [ordered]@{
    record_id = $Event.Event.RecordId
    timestamp_utc = $Event.Event.TimeCreated.ToUniversalTime().ToString('o')
    process_guid = $Event.Data.ProcessGuid
    process_id = $Event.Data.ProcessId
    image = $Event.Data.Image
}
$Json = $Output | ConvertTo-Json -Compress
[IO.File]::WriteAllText('C:\AVR-Lab\Experiments\BENIGN-001-sysmon.json', $Json)
$Json
