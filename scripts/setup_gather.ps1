

$server = 'D:\code\zmq_practice\cps2_zmq\gather\MameServer.py'
$sink = 'D:\code\zmq_practice\cps2_zmq\gather\LogSink.py'
$worker = 'D:\Code\zmq_practice\cps2_zmq\gather\MameWorker.py'

$numWorkers = 1
Write-Output "Starting Server with $numWorkers workers"

$serverID = Start-Process -FilePath "python.exe" -ArgumentList ($server) -PassThru
Write-Output $serverID.id $server

$sinkID = Start-Process -FilePath "python.exe" -ArgumentList ($sink) -PassThru
Write-Output $sinkID.id $server
# Start-Sleep -s 4

foreach ($i in 1..$numWorkers) {
    $pythonID = Start-Process -FilePath "python.exe" -ArgumentList ($worker) -PassThru
    Write-Output $pythonID.Id $script
}

Write-Output "Everything closed"
