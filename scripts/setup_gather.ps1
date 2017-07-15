workflow Start-Server
{
    param ([string] $server, [string[]] $scripts)
    parallel {
        sequence {
            $server = 'D:\code\zmq_practice\cps2_zmq\gather\MameServer.py'
            $serverID = Start-Process -FilePath "python.exe" -ArgumentList ($server) -PassThru
            Write-Output $serverID.id $server

            foreach -parallel ($script in $scripts) {
                $pythonID = Start-Process -FilePath "python.exe" -ArgumentList ($script) -NoNewWindow -PassThru
                Write-Output $pythonID.Id $script
            }
        }

    }
    Write-Output "Workflow done"
}

$server = 'D:\code\zmq_practice\cps2_zmq\gather\MameServer.py'
$sink = 'D:\code\zmq_practice\cps2_zmq\gather\MongoSink.py'
$worker = 'D:\Code\zmq_practice\cps2_zmq\gather\MameWorker.py'

$numWorkers = 4
Write-Output "Starting Server with $numWorkers workers"
$scripts = {$sink}.Invoke()

foreach ($i in 1..$numWorkers) {
    $scripts.Add($worker)
}

Start-Server -server $server -scripts $scripts
Write-Output "Everything closed"
