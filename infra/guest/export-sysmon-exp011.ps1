$ErrorActionPreference = 'Stop'

$Events = Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-Sysmon/Operational'
    Id = 1, 3, 11
    StartTime = (Get-Date).AddHours(-1)
}
$Parsed = foreach ($Event in $Events) {
    $Xml = [xml]$Event.ToXml()
    $Data = @{}
    foreach ($Item in $Xml.Event.EventData.Data) { $Data[$Item.Name] = [string]$Item.'#text' }
    [pscustomobject]@{ Event = $Event; Data = $Data }
}
$Process = $Parsed | Where-Object {
    $_.Event.Id -eq 1 -and $_.Data.CommandLine -like '*EXP-011.ps1*'
} | Sort-Object { $_.Event.TimeCreated } | Select-Object -Last 1
if (-not $Process) { throw 'EXP-011 process creation was not found.' }
$ProcessGuid = $Process.Data.ProcessGuid
$Output = foreach ($Item in $Parsed) {
    $Event = $Item.Event
    $Data = $Item.Data
    if ($Data.ProcessGuid -eq $ProcessGuid -and (
        $Event.Id -eq 1 -or
        ($Event.Id -eq 3 -and $Data.DestinationIp -eq '10.88.0.10' -and $Data.DestinationPort -eq '53') -or
        ($Event.Id -eq 11 -and $Data.TargetFilename -like 'C:\AVR-Lab\Experiments\EXP-011\*')
    )) {
        [ordered]@{
            record_id = $Event.RecordId
            event_id = $Event.Id
            timestamp_utc = $Event.TimeCreated.ToUniversalTime().ToString('o')
            process_guid = $Data.ProcessGuid
            process_id = $Data.ProcessId
            image = $Data.Image
            command_line = $Data.CommandLine
            source_ip = $Data.SourceIp
            source_port = $Data.SourcePort
            destination_ip = $Data.DestinationIp
            destination_port = $Data.DestinationPort
            target_filename = $Data.TargetFilename
        }
    }
}
$Json = $Output | ConvertTo-Json -Compress
[IO.File]::WriteAllText('C:\AVR-Lab\Experiments\EXP-011\sysmon-summary.json', $Json)
$Json
