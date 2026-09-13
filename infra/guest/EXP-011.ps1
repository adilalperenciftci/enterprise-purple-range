$ErrorActionPreference = 'Stop'
$Root = 'C:\AVR-Lab\Experiments\EXP-011'
New-Item -ItemType Directory -Path $Root -Force | Out-Null
$Result = Test-NetConnection -ComputerName '10.88.0.10' -Port 5985 -InformationLevel Detailed
$Marker = Join-Path $Root 'process-network-marker.txt'
[IO.File]::WriteAllText($Marker, 'EPR_EXP_011')
if (-not (Test-Path -LiteralPath $Marker)) { throw 'Marker write failed.' }
[PSCustomObject]@{
    Experiment = 'EXP-011'
    Target = '10.88.0.10'
    TcpSucceeded = $Result.TcpTestSucceeded
    Marker = $Marker
} | ConvertTo-Json -Compress
