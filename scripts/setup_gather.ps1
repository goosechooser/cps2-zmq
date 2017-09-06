$baseAddr ='tcp://127.0.0.1'
$basePort = 5556
$secondaryPort = $basePort + 1
$sinkTopics = 'MameWorker'

$server = 'D:\code\zmq_practice\scripts\mame_server_cli.py'
$sink = 'D:\code\zmq_practice\scripts\log_sink_cli.py'
$worker = 'D:\Code\zmq_practice\scripts\mame_worker_cli.py'

$numWorkers = 2
Write-Output "Starting Server with $numWorkers workers"

$serverID = Start-Process -FilePath "python.exe" -ArgumentList ($server, $baseAddr, $basePort) -PassThru
Write-Output $serverID.id $server

$sinkID = Start-Process -FilePath "python.exe" -ArgumentList ($sink, 666, $baseAddr, $secondaryPort, "--topics $sinkTopics") -PassThru
Write-Output $sinkID.id $sink
# Start-Sleep -s 4

foreach ($i in 1..$numWorkers) {
    $pythonID = Start-Process -FilePath "python.exe" -ArgumentList ($worker, $i, $baseAddr, $secondaryPort) -PassThru
    Write-Output $pythonID.Id $script
}

Write-Output "Everything closed"
